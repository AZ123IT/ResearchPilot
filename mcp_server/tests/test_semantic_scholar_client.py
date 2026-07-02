import httpx

from clients.semantic_scholar_client import SemanticScholarClient


def test_semantic_scholar_client_normalizes_mocked_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["query"] == "rag faithfulness"
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "paperId": "abc123",
                        "title": "Faithful RAG",
                        "abstract": "A paper about grounded generation.",
                        "year": 2024,
                        "publicationDate": "2024-02-03",
                        "url": "https://www.semanticscholar.org/paper/abc123",
                        "citationCount": 17,
                        "authors": [{"name": "Ada Lovelace"}, {"name": "Alan Turing"}],
                    }
                ]
            },
        )

    client = SemanticScholarClient(http_client=httpx.Client(transport=httpx.MockTransport(handler)))

    papers = client.search("rag faithfulness", 2)

    assert papers == [
        {
            "paper_id": "abc123",
            "title": "Faithful RAG",
            "authors": ["Ada Lovelace", "Alan Turing"],
            "abstract": "A paper about grounded generation.",
            "published_date": "2024-02-03",
            "source": "semantic_scholar",
            "url": "https://www.semanticscholar.org/paper/abc123",
            "citation_count": 17,
        }
    ]
