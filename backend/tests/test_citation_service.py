from app.services.citation_service import format_citation
from app.models.schemas import Paper


def sample_paper() -> Paper:
    return Paper(
        paper_id="2401.12345",
        title="Faithful Retrieval Augmented Generation",
        authors=["Ada Lovelace", "Alan Turing"],
        abstract="A study of grounded generation methods.",
        published_date="2024-01-15",
        source="arxiv",
        url="https://arxiv.org/abs/2401.12345",
        citation_count=None,
    )


def test_format_ieee_citation_includes_authors_title_year_and_url():
    citation = format_citation(sample_paper(), "IEEE")

    assert citation.startswith("Ada Lovelace and Alan Turing")
    assert '"Faithful Retrieval Augmented Generation"' in citation
    assert "2024" in citation
    assert "https://arxiv.org/abs/2401.12345" in citation


def test_format_apa_citation_includes_year_title_and_source_url():
    citation = format_citation(sample_paper(), "APA")

    assert citation.startswith("Lovelace, A., & Turing, A. (2024).")
    assert "Faithful Retrieval Augmented Generation." in citation
    assert "arXiv." in citation
    assert "https://arxiv.org/abs/2401.12345" in citation


def test_format_bibtex_citation_is_non_empty_and_uses_arxiv_key():
    citation = format_citation(sample_paper(), "BibTeX")

    assert citation.startswith("@article{lovelace2024faithful")
    assert "title = {Faithful Retrieval Augmented Generation}" in citation
    assert "author = {Ada Lovelace and Alan Turing}" in citation
    assert "url = {https://arxiv.org/abs/2401.12345}" in citation
