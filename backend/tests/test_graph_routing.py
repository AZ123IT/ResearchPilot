from app.agent.graph import run_research_graph
from app.models.schemas import ResearchRequest


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
        return {
            "paper_id": paper["paper_id"],
            "style": style,
            "citation_text": 'Ada Lovelace, "Faithful RAG", arXiv, 2024.',
        }

    async def save_to_notes(
        self,
        content: str,
        paper_id: str | None,
        tag: str | None,
        title: str | None = None,
        source: str | None = None,
        url: str | None = None,
    ):
        return {"storage": "memory", "note": {"content": content, "paper_id": paper_id, "tag": tag}, "warnings": []}

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


def test_question_goes_through_full_workflow(monkeypatch):
    monkeypatch.setattr("app.agent.nodes.get_research_tool_client", lambda: FakeToolClient())

    response = run_research_graph(
        ResearchRequest(
            question="What improves RAG faithfulness?",
            max_results=2,
            citation_style="IEEE",
        )
    )

    step_names = [step.step_name for step in response.steps]
    assert step_names == [
        "plan_research_task",
        "search_notes",
        "search_papers",
        "fetch_paper_details",
        "extract_summary",
        "verify_evidence",
        "format_citations",
        "save_notes",
        "generate_final_review",
    ]
    assert response.papers
    assert response.citations
    assert response.evidence_items
    assert response.literature_review.findings
    assert response.literature_review.summary
    assert response.prior_notes
    assert response.reused_notes
    assert response.memory_storage == "memory"


def test_workflow_returns_warnings_when_external_search_fails(monkeypatch):
    class FailingToolClient(FakeToolClient):
        async def search_papers(self, query: str, max_results: int, source: str = "auto"):
            return {"papers": [], "warnings": ["arXiv unavailable"]}

    monkeypatch.setattr("app.agent.nodes.get_research_tool_client", lambda: FailingToolClient())

    response = run_research_graph(
        ResearchRequest(
            question="What improves RAG faithfulness?",
            max_results=2,
            citation_style="APA",
        )
    )

    assert "arXiv unavailable" in response.warnings
    assert response.steps[-1].status == "success"


def test_tool_call_logs_include_timing_and_fallback_fields(monkeypatch):
    monkeypatch.setattr("app.agent.nodes.get_research_tool_client", lambda: FakeToolClient())

    response = run_research_graph(
        ResearchRequest(
            question="What improves RAG faithfulness?",
            max_results=2,
            citation_style="IEEE",
        )
    )

    assert response.tool_call_logs
    for log in response.tool_call_logs:
        assert log.step_name
        assert log.tool_name
        assert log.started_at
        assert log.finished_at
        assert log.duration_ms >= 0
        assert log.error_message is None
        assert log.fallback_used is False


def test_note_search_failure_does_not_crash_workflow(monkeypatch):
    class NoteFailingToolClient(FakeToolClient):
        async def search_notes(self, query: str, top_k: int):
            raise RuntimeError("note search unavailable")

    monkeypatch.setattr("app.agent.nodes.get_research_tool_client", lambda: NoteFailingToolClient())

    response = run_research_graph(
        ResearchRequest(
            question="What improves RAG faithfulness?",
            max_results=2,
            citation_style="IEEE",
        )
    )

    assert response.steps[-1].step_name == "generate_final_review"
    assert any("search_notes failed" in warning for warning in response.warnings)
    assert response.prior_notes == []


def test_deterministic_fallback_review_is_structured_and_marks_weak_evidence(monkeypatch):
    class MixedEvidenceToolClient(FakeToolClient):
        async def search_papers(self, query: str, max_results: int, source: str = "auto"):
            return {
                "source": "demo",
                "papers": [
                    {
                        "paper_id": "demo-rag-faithfulness",
                        "title": "Faithfulness Audits for Retrieval Augmented Generation",
                        "authors": ["Mina Park"],
                        "abstract": (
                            "Retrieval augmented generation systems improve faithfulness when answers cite retrieved evidence, "
                            "compare generated claims against source passages, and abstain when retrieval support is missing."
                        ),
                        "published_date": "2025-02-10",
                        "source": "demo",
                        "url": "https://example.local/demo-rag-faithfulness",
                        "citation_count": None,
                    },
                    {
                        "paper_id": "demo-empty",
                        "title": "Sparse Metadata In Research Automation",
                        "authors": ["Noor Singh"],
                        "abstract": "",
                        "published_date": "2025-04-15",
                        "source": "demo",
                        "url": "https://example.local/demo-empty",
                        "citation_count": None,
                    },
                ],
                "warnings": ["Demo mode enabled: using local fixture papers."],
                "fallback_used": True,
                "cache_used": False,
                "search_source_summary": {"arxiv": 0, "semantic_scholar": 0, "demo": 2, "cache": 0},
            }

        async def fetch_paper_detail(self, paper_id: str, source: str):
            return {"paper": None, "warnings": []}

    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr("app.agent.nodes.get_research_tool_client", lambda: MixedEvidenceToolClient())

    response = run_research_graph(
        ResearchRequest(
            question="What improves RAG faithfulness?",
            max_results=2,
            citation_style="IEEE",
        )
    )

    assert response.literature_review.summary.startswith("Reviewed 2 demo papers")
    assert response.literature_review.key_findings
    assert any("deterministic" in method.lower() for method in response.literature_review.methods)
    assert any("abstracts" in limitation.lower() for limitation in response.literature_review.limitations)
    assert response.literature_review.low_confidence_claims
    assert any("DeepSeek API key is not configured" in warning for warning in response.warnings)
