from types import SimpleNamespace

from app.core.config import Settings
from app.llm.deepseek_client import DeepSeekClient, parse_findings
from app.models.schemas import Paper


class FakeCompletions:
    def __init__(self, content: str):
        self.content = content
        self.kwargs: dict = {}

    def create(self, **kwargs):
        self.kwargs = kwargs
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _client(content: str) -> tuple[DeepSeekClient, FakeCompletions]:
    completions = FakeCompletions(content)
    fake_openai = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return DeepSeekClient(settings=Settings(deepseek_api_key="test-key"), client=fake_openai), completions


def test_extract_findings_requests_json_and_parses_it():
    client, completions = _client('{"findings": ["Retrieval grounding reduces hallucination.", "Citation checks improve faithfulness."]}')
    paper = Paper(paper_id="p1", title="Faithful RAG", abstract="Grounding reduces hallucination.", source="arxiv", url="https://arxiv.org/abs/p1")

    findings = client.extract_findings("How to improve RAG faithfulness?", [paper])

    assert [finding.text for finding in findings] == [
        "Retrieval grounding reduces hallucination.",
        "Citation checks improve faithfulness.",
    ]
    assert completions.kwargs["response_format"] == {"type": "json_object"}
    assert "Faithful RAG" in completions.kwargs["messages"][1]["content"]


def test_parse_findings_drops_lead_in_numbering_and_markdown():
    content = "Here are three findings:\n1. **Grounding** reduces hallucination.\n- Citation checks help.\n\n3) Abstention matters."

    assert parse_findings(content) == [
        "Grounding reduces hallucination.",
        "Citation checks help.",
        "Abstention matters.",
    ]


def test_parse_findings_accepts_object_items_and_skips_empty_values():
    content = '{"findings": [{"claim": "Claim A."}, {"text": "Claim B."}, "", null]}'

    assert parse_findings(content) == ["Claim A.", "Claim B."]
