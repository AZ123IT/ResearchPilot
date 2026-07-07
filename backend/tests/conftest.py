import pytest

from app.core.config import get_settings


RUNTIME_ENV_KEYS = (
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "RESEARCHPILOT_DEMO_MODE",
    "RESEARCH_TOOL_CLIENT_MODE",
    "RESEARCHPILOT_TOOL_CLIENT",
    "MCP_SERVER_COMMAND",
    "MCP_SERVER_ARGS",
    "MCP_SERVER_CWD",
)


@pytest.fixture(autouse=True)
def isolate_runtime_environment(monkeypatch):
    for key in RUNTIME_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
