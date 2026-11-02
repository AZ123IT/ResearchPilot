import httpx

from clients.arxiv_client import ArxivClient, build_arxiv_query


FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.12345v1</id>
    <published>2024-01-15T00:00:00Z</published>
    <title>Faithful  Retrieval-Augmented
      Generation</title>
    <summary>We study grounded generation.</summary>
    <author><name>Ada Lovelace</name></author>
  </entry>
</feed>"""

EMPTY_FEED = '<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'


def test_build_arxiv_query_keeps_topic_terms_and_drops_question_words():
    query = build_arxiv_query("What are recent methods for improving RAG faithfulness?")

    assert query == "all:rag AND all:faithfulness"


def test_build_arxiv_query_supports_or_and_caps_terms():
    query = build_arxiv_query("graph neural network protein folding benchmark dataset survey", "OR")

    assert query.split(" OR ") == [
        "all:graph",
        "all:neural",
        "all:network",
        "all:protein",
        "all:folding",
        "all:benchmark",
    ]


def test_search_sorts_by_relevance_and_parses_feed():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, text=FEED)

    client = ArxivClient(http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    papers = client.search("How does RAG faithfulness work?", 3)

    assert len(requests) == 1
    assert requests[0].url.params["search_query"] == "all:rag AND all:faithfulness"
    assert requests[0].url.params["sortBy"] == "relevance"
    assert papers[0]["paper_id"] == "2401.12345v1"
    assert papers[0]["title"] == "Faithful Retrieval-Augmented Generation"
    assert papers[0]["published_date"] == "2024-01-15"


def test_search_loosens_to_or_when_and_query_finds_nothing():
    queries: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        queries.append(request.url.params["search_query"])
        return httpx.Response(200, text=EMPTY_FEED if len(queries) == 1 else FEED)

    client = ArxivClient(http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    papers = client.search("rag faithfulness", 3)

    assert queries == ["all:rag AND all:faithfulness", "all:rag OR all:faithfulness"]
    assert len(papers) == 1
