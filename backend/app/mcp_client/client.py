import asyncio
import json
import os
import shlex
import threading
from concurrent.futures import Future
from typing import Any, Protocol

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.core.config import Settings, get_settings
from tools.fetch_paper_detail import fetch_paper_detail_tool
from tools.format_citation import format_citation_tool
from tools.notes import save_to_notes_tool, search_notes_tool
from tools.search_papers import search_papers_tool


class ResearchToolClient(Protocol):
    async def search_papers(self, query: str, max_results: int, source: str) -> dict: ...

    async def fetch_paper_detail(self, paper_id: str, source: str) -> dict: ...

    async def format_citation(self, paper: dict, style: str) -> dict: ...

    async def save_to_notes(
        self,
        content: str,
        paper_id: str | None,
        tag: str | None,
        title: str | None = None,
        source: str | None = None,
        url: str | None = None,
    ) -> dict: ...

    async def search_notes(self, query: str, top_k: int) -> dict: ...


class LocalToolClient:
    """Direct Python tool adapter for tests and deterministic local development."""

    async def search_papers(self, query: str, max_results: int, source: str = "auto") -> dict:
        return search_papers_tool(query=query, max_results=max_results, source=source)

    async def fetch_paper_detail(self, paper_id: str, source: str = "arxiv") -> dict:
        return fetch_paper_detail_tool(paper_id=paper_id, source=source)

    async def format_citation(self, paper: dict, style: str = "IEEE") -> dict:
        return format_citation_tool(paper=paper, style=style)

    async def save_to_notes(
        self,
        content: str,
        paper_id: str | None = None,
        tag: str | None = None,
        title: str | None = None,
        source: str | None = None,
        url: str | None = None,
    ) -> dict:
        return save_to_notes_tool(content=content, paper_id=paper_id, tag=tag, title=title, source=source, url=url)

    async def search_notes(self, query: str, top_k: int = 5) -> dict:
        return search_notes_tool(query=query, top_k=top_k)


class MCPToolClient:
    """MCP stdio protocol adapter.

    The client starts the configured MCP stdio server command for each call. This keeps
    one-shot protocol calls isolated from the persistent-session adapter.
    """

    def __init__(self, settings: Settings | None = None, fallback_client: LocalToolClient | None = None):
        self.settings = settings or get_settings()
        self.fallback_client = fallback_client or LocalToolClient()

    async def search_papers(self, query: str, max_results: int, source: str = "auto") -> dict:
        return await self._call_tool(
            "search_papers",
            {"query": query, "max_results": max_results, "source": source},
            lambda: self.fallback_client.search_papers(query, max_results, source),
        )

    async def fetch_paper_detail(self, paper_id: str, source: str = "arxiv") -> dict:
        return await self._call_tool(
            "fetch_paper_detail",
            {"paper_id": paper_id, "source": source},
            lambda: self.fallback_client.fetch_paper_detail(paper_id, source),
        )

    async def format_citation(self, paper: dict, style: str = "IEEE") -> dict:
        return await self._call_tool(
            "format_citation",
            {"paper": paper, "style": style},
            lambda: self.fallback_client.format_citation(paper, style),
        )

    async def save_to_notes(
        self,
        content: str,
        paper_id: str | None = None,
        tag: str | None = None,
        title: str | None = None,
        source: str | None = None,
        url: str | None = None,
    ) -> dict:
        return await self._call_tool(
            "save_to_notes",
            {"content": content, "paper_id": paper_id, "tag": tag, "title": title, "source": source, "url": url},
            lambda: self.fallback_client.save_to_notes(content, paper_id, tag, title, source, url),
        )

    async def search_notes(self, query: str, top_k: int = 5) -> dict:
        return await self._call_tool(
            "search_notes",
            {"query": query, "top_k": top_k},
            lambda: self.fallback_client.search_notes(query, top_k),
        )

    async def _call_tool(self, tool_name: str, arguments: dict[str, Any], fallback_factory) -> dict:
        try:
            result = await self._call_protocol_tool(tool_name, arguments)
            result.setdefault("_meta", {})["client_mode"] = "mcp"
            result["_meta"]["fallback_used"] = False
            return result
        except Exception as exc:
            if not self.settings.mcp_fallback_to_local:
                raise
            fallback_result = await fallback_factory()
            fallback_result.setdefault("warnings", []).append(
                f"MCP protocol call failed for {tool_name}; used local fallback: {exc}"
            )
            fallback_result.setdefault("_meta", {})["client_mode"] = "mcp"
            fallback_result["_meta"]["fallback_used"] = True
            return fallback_result

    async def _call_protocol_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict:
        server_params = _server_params(self.settings)
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                return _decode_mcp_result(result)


class PersistentMCPToolClient(MCPToolClient):
    """Reusable MCP stdio session.

    The MCP SDK exposes stdio transports and sessions as async context managers.
    The backend graph is currently synchronous, so this client owns a dedicated
    background event loop and schedules all MCP calls onto that loop.
    """

    def __init__(self, settings: Settings | None = None, fallback_client: LocalToolClient | None = None):
        super().__init__(settings=settings, fallback_client=fallback_client)
        self._lock = threading.Lock()
        self._ready = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._session: ClientSession | None = None
        self._queue: asyncio.Queue | None = None
        self._startup_error: BaseException | None = None
        self._closed = False

    async def _call_protocol_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict:
        self._ensure_started()
        if self._loop is None or self._queue is None:
            raise RuntimeError("Persistent MCP session is not available")
        future: Future = Future()
        self._loop.call_soon_threadsafe(self._queue.put_nowait, (tool_name, arguments, future))
        result = await asyncio.to_thread(future.result, self.settings.mcp_call_timeout_seconds)
        return _decode_mcp_result(result)

    async def close(self) -> None:
        loop = self._loop
        queue = self._queue
        if loop is None or queue is None or loop.is_closed() or self._closed:
            return
        self._closed = True
        future: Future = Future()
        loop.call_soon_threadsafe(queue.put_nowait, (None, None, future))
        await asyncio.to_thread(future.result, self.settings.mcp_call_timeout_seconds)
        if self._thread is not None:
            await asyncio.to_thread(self._thread.join, self.settings.mcp_call_timeout_seconds)

    def _ensure_started(self) -> None:
        if self._session is not None and self._thread and self._thread.is_alive():
            return

        with self._lock:
            if self._session is not None and self._thread and self._thread.is_alive():
                return
            self._ready.clear()
            self._startup_error = None
            self._closed = False
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._run_loop, name="researchpilot-mcp-session", daemon=True)
            self._thread.start()

        if not self._ready.wait(self.settings.mcp_startup_timeout_seconds):
            raise RuntimeError("Timed out starting persistent MCP session")
        if self._startup_error is not None:
            raise RuntimeError(f"Persistent MCP session startup failed: {self._startup_error}")

    def _run_loop(self) -> None:
        assert self._loop is not None
        asyncio.set_event_loop(self._loop)
        self._loop.create_task(self._session_worker())
        self._loop.run_forever()
        self._loop.close()

    async def _session_worker(self) -> None:
        try:
            async with stdio_client(_server_params(self.settings)) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    self._session = session
                    self._queue = asyncio.Queue()
                    self._ready.set()
                    while True:
                        tool_name, arguments, future = await self._queue.get()
                        if tool_name is None:
                            future.set_result(True)
                            break
                        try:
                            future.set_result(await session.call_tool(tool_name, arguments=arguments))
                        except BaseException as exc:
                            future.set_exception(exc)
        except BaseException as exc:  # pragma: no cover - exercised via fallback behavior
            self._startup_error = exc
            self._ready.set()
        finally:
            self._session = None
            self._queue = None
            assert self._loop is not None
            self._loop.call_soon(self._loop.stop)


_CLIENT_SINGLETON: ResearchToolClient | None = None


def get_research_tool_client(settings: Settings | None = None) -> ResearchToolClient:
    global _CLIENT_SINGLETON
    resolved = settings or get_settings()
    mode = resolved.tool_client_mode.lower()
    if mode == "mcp":
        mode = "mcp_single"
    if mode == "mcp_single":
        return MCPToolClient(resolved)
    if mode == "mcp_persistent":
        if settings is not None:
            return PersistentMCPToolClient(resolved)
        if not isinstance(_CLIENT_SINGLETON, PersistentMCPToolClient):
            _CLIENT_SINGLETON = PersistentMCPToolClient(resolved)
        return _CLIENT_SINGLETON
    return LocalToolClient()


async def close_research_tool_client() -> None:
    global _CLIENT_SINGLETON
    if isinstance(_CLIENT_SINGLETON, PersistentMCPToolClient):
        await _CLIENT_SINGLETON.close()
    _CLIENT_SINGLETON = None


def _server_params(settings: Settings) -> StdioServerParameters:
    return StdioServerParameters(
        command=settings.mcp_command,
        args=shlex.split(settings.mcp_args),
        cwd=settings.mcp_cwd,
        env=_mcp_env(settings),
    )


def _mcp_env(settings: Settings) -> dict[str, str]:
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    mcp_path = os.path.join(settings.mcp_cwd, "mcp_server")
    env["PYTHONPATH"] = f"{mcp_path}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else mcp_path
    return env


def _decode_mcp_result(result: Any) -> dict:
    structured_content = getattr(result, "structured_content", None)
    if isinstance(structured_content, dict):
        return structured_content

    content = getattr(result, "content", None) or []
    if content:
        text = getattr(content[0], "text", None)
        if text:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                return {"result": text}
            if isinstance(parsed, dict):
                return parsed
            return {"result": parsed}

    return {"content": str(result)}
