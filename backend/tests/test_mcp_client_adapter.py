import asyncio

from app.core.config import Settings
from app.mcp_client.client import LocalToolClient, MCPToolClient, PersistentMCPToolClient, get_research_tool_client


def test_local_tool_client_can_call_format_citation():
    client = LocalToolClient()

    result = asyncio.run(
        client.format_citation(
            {
                "paper_id": "2401.12345",
                "title": "Faithful Retrieval Augmented Generation",
                "authors": ["Ada Lovelace"],
                "abstract": "Grounded generation methods.",
                "published_date": "2024-01-15",
                "source": "arxiv",
                "url": "https://arxiv.org/abs/2401.12345",
                "citation_count": None,
            },
            "IEEE",
        )
    )

    assert result["paper_id"] == "2401.12345"
    assert result["citation_text"]


def test_tool_client_factory_returns_expected_client_types():
    assert isinstance(get_research_tool_client(Settings(tool_client_mode="local")), LocalToolClient)
    assert isinstance(get_research_tool_client(Settings(tool_client_mode="mcp_single")), MCPToolClient)
    assert isinstance(get_research_tool_client(Settings(tool_client_mode="mcp_persistent")), PersistentMCPToolClient)


def test_persistent_mcp_client_falls_back_to_local_when_startup_fails():
    settings = Settings(
        tool_client_mode="mcp_persistent",
        mcp_command="/definitely/missing/python",
        mcp_args="mcp_server/server.py",
        mcp_fallback_to_local=True,
    )
    client = PersistentMCPToolClient(settings)

    result = asyncio.run(
        client.format_citation(
            {
                "paper_id": "2401.12345",
                "title": "Faithful Retrieval Augmented Generation",
                "authors": ["Ada Lovelace"],
                "abstract": "Grounded generation methods.",
                "published_date": "2024-01-15",
                "source": "arxiv",
                "url": "https://arxiv.org/abs/2401.12345",
                "citation_count": None,
            },
            "IEEE",
        )
    )
    asyncio.run(client.close())

    assert result["citation_text"]
    assert result["_meta"]["fallback_used"] is True
