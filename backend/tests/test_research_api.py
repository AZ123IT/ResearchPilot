from fastapi.testclient import TestClient

from app.main import app


class FakeToolClient:
    async def search_papers(self, query: str, max_results: int, source: str = "auto"):
        return {
            "papers": [
                {
                    "paper_id": "2401.12345",
                    "title": "Faithful RAG",
                    "authors": ["Ada Lovelace"],
                    "abstract": "Retrieval augmented generation improves faithfulness by grounding answers in retrieved evidence.",
                    "published_date": "2024-01-15",
                    "source": "arxiv",
                    "url": "https://arxiv.org/abs/2401.12345",
                    "citation_count": None,
                }
            ],
            "warnings": [],
        }

    async def fetch_paper_detail(self, paper_id: str, source: str):
        return {
            "paper": {
                "paper_id": paper_id,
                "title": "Faithful RAG",
                "authors": ["Ada Lovelace"],
                "abstract": "Retrieval augmented generation improves faithfulness by grounding answers in retrieved evidence.",
                "published_date": "2024-01-15",
                "source": "arxiv",
                "url": f"https://arxiv.org/abs/{paper_id}",
                "citation_count": None,
            },
            "warnings": [],
        }

    async def format_citation(self, paper: dict, style: str):
        return {"paper_id": paper["paper_id"], "style": style, "citation_text": "citation"}

    async def save_to_notes(
        self,
        content: str,
        paper_id: str | None,
        tag: str | None,
        title: str | None = None,
        source: str | None = None,
        url: str | None = None,
    ):
        return {"storage": "memory", "note": {"content": content}, "warnings": []}

    async def search_notes(self, query: str, top_k: int):
        return {
            "storage": "memory",
            "notes": [
                {
                    "note_id": "n1",
                    "paper_id": "p1",
                    "title": "Prior RAG Note",
                    "content_preview": "Prior evidence about RAG faithfulness.",
                    "tag": "rag",
                    "source": "memory",
                    "score": 2,
                    "storage": "memory",
                }
            ],
            "warnings": [],
        }


def test_research_run_endpoint_returns_structured_response(monkeypatch):
    monkeypatch.setattr("app.agent.nodes.get_research_tool_client", lambda: FakeToolClient())
    client = TestClient(app)

    response = client.post(
        "/api/research/run",
        json={
            "question": "What improves RAG faithfulness?",
            "max_results": 2,
            "citation_style": "IEEE",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["steps"]
    assert payload["papers"]
    assert payload["literature_review"]["summary"]
    assert payload["literature_review"]["findings"]
    assert payload["evidence_items"]
    assert payload["citations"]
    assert payload["tool_call_logs"][0]["step_name"]
    assert "duration_ms" in payload["tool_call_logs"][0]
    assert payload["prior_notes"]
    assert payload["reused_notes"]
    assert "fallback_summary" in payload
    assert payload["memory_storage"] == "memory"
    assert payload["cache_used"] is False
    assert payload["research_plan"]
    assert payload["research_plan"][0]["title"] == "Scope research task"
    assert payload["evidence_coverage"]
    assert payload["evidence_coverage"][0]["support_status"] == "supported"
    assert payload["adaptive_search"]["search_rounds"] >= 1
    assert payload["adaptive_search"]["initial_query"] == "What improves RAG faithfulness?"


def test_research_run_endpoint_completes_in_demo_mode_without_external_keys(monkeypatch):
    monkeypatch.setenv("RESEARCHPILOT_DEMO_MODE", "true")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    client = TestClient(app)

    response = client.post(
        "/api/research/run",
        json={
            "question": "What are recent methods for improving RAG faithfulness?",
            "max_results": 2,
            "citation_style": "IEEE",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["papers"]) == 2
    assert {paper["source"] for paper in payload["papers"]} == {"demo"}
    assert payload["search_source_summary"]["demo"] == 2
    assert payload["memory_storage"] == "memory"
    assert payload["fallback_summary"]
    assert any("Demo mode enabled" in warning for warning in payload["warnings"])
    assert any("DeepSeek API key is not configured" in warning for warning in payload["warnings"])
    assert payload["literature_review"]["summary"].startswith("Reviewed 2 demo papers")
    assert payload["literature_review"]["key_findings"]
    assert payload["research_plan"]
    assert payload["adaptive_search"]["triggered"] is False
