from tools.format_citation import format_citation_tool


def test_format_citation_tool_returns_non_empty_citation_text():
    result = format_citation_tool(
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

    assert result["citation_text"]
    assert result["style"] == "IEEE"
