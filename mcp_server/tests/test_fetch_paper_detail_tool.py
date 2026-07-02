from clients.arxiv_client import ArxivClient
from tools.fetch_paper_detail import fetch_paper_detail_tool


class FakeArxivClient(ArxivClient):
    def fetch_by_id(self, paper_id: str):
        return {
            "paper_id": paper_id,
            "title": "Faithful RAG",
            "authors": ["Ada Lovelace"],
            "abstract": "Evidence grounded generation.",
            "published_date": "2024-01-15",
            "source": "arxiv",
            "url": f"https://arxiv.org/abs/{paper_id}",
            "citation_count": None,
        }


def test_fetch_paper_detail_returns_structured_result():
    result = fetch_paper_detail_tool("2401.12345", "arxiv", arxiv_client=FakeArxivClient())

    assert result["paper"]["paper_id"] == "2401.12345"
    assert result["paper"]["title"] == "Faithful RAG"
