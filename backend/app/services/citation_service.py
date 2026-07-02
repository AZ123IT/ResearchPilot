import re

from app.models.schemas import CitationStyle, Paper


def format_citation(paper: Paper, style: CitationStyle | str) -> str:
    normalized_style = _normalize_style(style)
    if normalized_style == "IEEE":
        return _format_ieee(paper)
    if normalized_style == "APA":
        return _format_apa(paper)
    if normalized_style == "BibTeX":
        return _format_bibtex(paper)
    raise ValueError(f"Unsupported citation style: {style}")


def _normalize_style(style: CitationStyle | str) -> CitationStyle:
    lookup = {"ieee": "IEEE", "apa": "APA", "bibtex": "BibTeX"}
    normalized = lookup.get(str(style).strip().lower())
    if normalized is None:
        raise ValueError(f"Unsupported citation style: {style}")
    return normalized  # type: ignore[return-value]


def _format_ieee(paper: Paper) -> str:
    authors = _join_authors_ieee(paper.authors)
    year = _year(paper.published_date)
    source = _display_source(paper.source)
    return f'{authors}, "{paper.title}", {source}, {year}. [Online]. Available: {paper.url}'


def _format_apa(paper: Paper) -> str:
    authors = _join_authors_apa(paper.authors)
    year = _year(paper.published_date)
    source = _display_source(paper.source)
    return f"{authors} ({year}). {paper.title}. {source}. {paper.url}"


def _format_bibtex(paper: Paper) -> str:
    year = _year(paper.published_date)
    key = _bibtex_key(paper, year)
    authors = " and ".join(paper.authors) or "Unknown"
    return "\n".join(
        [
            f"@article{{{key},",
            f"  title = {{{paper.title}}},",
            f"  author = {{{authors}}},",
            f"  year = {{{year}}},",
            f"  url = {{{paper.url}}},",
            f"  note = {{{_display_source(paper.source)}}}",
            "}",
        ]
    )


def _join_authors_ieee(authors: list[str]) -> str:
    if not authors:
        return "Unknown author"
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    return f"{', '.join(authors[:-1])}, and {authors[-1]}"


def _join_authors_apa(authors: list[str]) -> str:
    if not authors:
        return "Unknown author"
    formatted = [_format_apa_name(author) for author in authors]
    if len(formatted) == 1:
        return formatted[0]
    return f"{', '.join(formatted[:-1])}, & {formatted[-1]}"


def _format_apa_name(author: str) -> str:
    parts = [part for part in author.split() if part]
    if not parts:
        return "Unknown"
    surname = parts[-1]
    initials = " ".join(f"{part[0]}." for part in parts[:-1])
    return f"{surname}, {initials}".strip()


def _display_source(source: str) -> str:
    if source.lower() == "arxiv":
        return "arXiv"
    if source.lower() == "semantic_scholar":
        return "Semantic Scholar"
    return source


def _year(published_date: str) -> str:
    match = re.search(r"\d{4}", published_date or "")
    return match.group(0) if match else "n.d."


def _bibtex_key(paper: Paper, year: str) -> str:
    first_author = paper.authors[0] if paper.authors else "unknown"
    surname = re.sub(r"[^a-z0-9]", "", first_author.split()[-1].lower())
    first_title_word = next(
        (re.sub(r"[^a-z0-9]", "", word.lower()) for word in paper.title.split() if word),
        "paper",
    )
    return f"{surname}{year}{first_title_word}"
