from clients.arxiv_client import ArxivClient
from tools.search_papers import clear_search_cache, expire_search_cache_for_tests, search_papers_tool


class FakeArxivClient(ArxivClient):
    def search(self, query: str, max_results: int):
        return [
            {
                "paper_id": "2401.12345",
                "title": "Faithful RAG",
                "authors": ["Ada Lovelace"],
                "abstract": "Evidence grounded generation.",
                "published_date": "2024-01-15",
                "source": "arxiv",
                "url": "https://arxiv.org/abs/2401.12345",
                "citation_count": None,
            }
        ][:max_results]


class FailingArxivClient(ArxivClient):
    def search(self, query: str, max_results: int):
        raise RuntimeError("arXiv unavailable")


class FakeSemanticClient:
    def __init__(self, papers: list[dict] | None = None):
        self.papers = papers or [
            {
                "paper_id": "ss-1",
                "title": "Semantic Scholar RAG",
                "authors": ["Grace Hopper"],
                "abstract": "Semantic fallback evidence.",
                "published_date": "2024-02-01",
                "source": "semantic_scholar",
                "url": "https://www.semanticscholar.org/paper/ss-1",
                "citation_count": 3,
            }
        ]

    def search(self, query: str, max_results: int):
        return self.papers[:max_results]


def test_search_papers_returns_structured_results():
    clear_search_cache()
    result = search_papers_tool("rag faithfulness", 3, "arxiv", arxiv_client=FakeArxivClient())

    assert result["source"] == "arxiv"
    assert result["papers"][0]["paper_id"] == "2401.12345"
    assert result["papers"][0]["authors"] == ["Ada Lovelace"]


def test_demo_mode_returns_stable_local_papers(monkeypatch):
    monkeypatch.setenv("RESEARCHPILOT_DEMO_MODE", "true")
    clear_search_cache()

    result = search_papers_tool(
        "rag faithfulness",
        2,
        "auto",
        arxiv_client=FailingArxivClient(),
        semantic_client=FakeSemanticClient([]),
    )

    assert result["source"] == "demo"
    assert result["fallback_used"] is True
    assert result["cache_used"] is False
    assert len(result["papers"]) == 2
    assert {paper["source"] for paper in result["papers"]} == {"demo"}
    assert result["search_source_summary"]["demo"] == 2
    assert any("Demo mode enabled" in warning for warning in result["warnings"])


def test_search_papers_semantic_scholar_source_works():
    clear_search_cache()

    result = search_papers_tool(
        "rag faithfulness",
        3,
        "semantic_scholar",
        semantic_client=FakeSemanticClient(),
    )

    assert result["source"] == "semantic_scholar"
    assert result["papers"][0]["paper_id"] == "ss-1"
    assert result["search_source_summary"]["semantic_scholar"] == 1


def test_search_papers_auto_falls_back_to_semantic_scholar_when_arxiv_fails():
    clear_search_cache()

    result = search_papers_tool(
        "rag faithfulness",
        3,
        "auto",
        arxiv_client=FailingArxivClient(),
        semantic_client=FakeSemanticClient(),
    )

    assert result["fallback_used"] is True
    assert result["papers"][0]["source"] == "semantic_scholar"
    assert any("arXiv search failed" in warning for warning in result["warnings"])


def test_search_papers_auto_merges_and_deduplicates_results():
    clear_search_cache()
    semantic = FakeSemanticClient(
        [
            {
                "paper_id": "duplicate-title",
                "title": "Faithful RAG",
                "authors": ["Grace Hopper"],
                "abstract": "Duplicate by title.",
                "published_date": "2024-02-01",
                "source": "semantic_scholar",
                "url": "https://www.semanticscholar.org/paper/duplicate-title",
                "citation_count": 3,
            },
            {
                "paper_id": "ss-2",
                "title": "Different RAG",
                "authors": ["Grace Hopper"],
                "abstract": "Different paper.",
                "published_date": "2024-02-02",
                "source": "semantic_scholar",
                "url": "https://www.semanticscholar.org/paper/ss-2",
                "citation_count": 5,
            },
        ]
    )

    result = search_papers_tool("rag faithfulness", 3, "auto", arxiv_client=FakeArxivClient(), semantic_client=semantic)

    titles = [paper["title"] for paper in result["papers"]]
    assert titles == ["Faithful RAG", "Different RAG"]
    assert result["fallback_used"] is True


def test_search_cache_is_used_when_external_client_fails():
    clear_search_cache()
    first = search_papers_tool("rag faithfulness", 1, "arxiv", arxiv_client=FakeArxivClient())

    cached = search_papers_tool("rag faithfulness", 1, "arxiv", arxiv_client=FailingArxivClient())

    assert first["papers"]
    assert cached["cache_used"] is True
    assert cached["fallback_used"] is True
    assert cached["source"] == "cache"
    assert cached["papers"][0]["paper_id"] == "2401.12345"


def test_expired_search_cache_is_not_used_when_external_client_fails():
    clear_search_cache()
    search_papers_tool("rag faithfulness", 1, "arxiv", arxiv_client=FakeArxivClient())
    expire_search_cache_for_tests()

    result = search_papers_tool("rag faithfulness", 1, "arxiv", arxiv_client=FailingArxivClient())

    assert result["cache_used"] is False
    assert result["papers"] == []
