import os
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    deepseek_api_key: str | None = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY"))
    deepseek_base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"))
    deepseek_model: str = field(default_factory=lambda: os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    arxiv_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("ARXIV_TIMEOUT_SECONDS", "10")))
    supabase_url: str | None = field(default_factory=lambda: os.getenv("SUPABASE_URL"))
    supabase_service_role_key: str | None = field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    supabase_notes_table: str = field(default_factory=lambda: os.getenv("SUPABASE_NOTES_TABLE", "research_notes"))
    demo_mode: bool = field(default_factory=lambda: _env_bool("RESEARCHPILOT_DEMO_MODE", False))
    tool_client_mode: str = field(
        default_factory=lambda: os.getenv(
            "RESEARCH_TOOL_CLIENT_MODE",
            os.getenv("RESEARCHPILOT_TOOL_CLIENT", "local"),
        )
    )
    mcp_command: str = field(default_factory=lambda: os.getenv("MCP_SERVER_COMMAND", os.getenv("RESEARCHPILOT_MCP_COMMAND", sys.executable)))
    mcp_args: str = field(default_factory=lambda: os.getenv("MCP_SERVER_ARGS", os.getenv("RESEARCHPILOT_MCP_ARGS", "mcp_server/server.py")))
    mcp_cwd: str = field(default_factory=lambda: os.getenv("MCP_SERVER_CWD", os.getenv("RESEARCHPILOT_MCP_CWD", str(PROJECT_ROOT))))
    mcp_fallback_to_local: bool = field(default_factory=lambda: _env_bool("MCP_FALLBACK_TO_LOCAL", True, alias="RESEARCHPILOT_MCP_FALLBACK_TO_LOCAL"))
    mcp_startup_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("MCP_STARTUP_TIMEOUT_SECONDS", "10")))
    mcp_call_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("MCP_CALL_TIMEOUT_SECONDS", "30")))


def _env_bool(name: str, default: bool, alias: str | None = None) -> bool:
    value = os.getenv(name)
    if value is None and alias:
        value = os.getenv(alias)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
