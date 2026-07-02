import re

from models.schemas import Paper


def format_citation_tool(paper: dict, style: str) -> dict:
    validated = Paper.model_validate(paper)
    citation_text = _format(validated, style)
    return {"style": _normalize_style(style), "paper_id": validated.paper_id, "citation_text": citation_text}


def _format(paper: Paper, style: str) -> str:
    normalized = _normalize_style(style)
    if normalized == "IEEE":
        authors = _join_authors_ieee(paper.authors)
        return f'{authors}, "{paper.title}", {_display_source(paper.source)}, {_year(paper.published_date)}. [Online]. Available: {paper.url}'
    if normalized == "APA":
        authors = _join_authors_apa(paper.authors)
        return f"{authors} ({_year(paper.published_date)}). {paper.title}. {_display_source(paper.source)}. {paper.url}"

    authors = " and ".join(paper.authors) or "Unknown"
    return "\n".join(
        [
            f"@article{{{_bibtex_key(paper)},",
            f"  title = {{{paper.title}}},",
            f"  author = {{{authors}}},",
            f"  year = {{{_year(paper.published_date)}}},",
            f"  url = {{{paper.url}}},",
            f"  note = {{{_display_source(paper.source)}}}",
            "}",
        ]
    )


def _normalize_style(style: str) -> str:
    lookup = {"ieee": "IEEE", "apa": "APA", "bibtex": "BibTeX"}
    normalized = lookup.get(style.strip().lower())
    if normalized is None:
        raise ValueError(f"Unsupported citation style: {style}")
    return normalized


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
    surname = parts[-1] if parts else "Unknown"
    initials = " ".join(f"{part[0]}." for part in parts[:-1])
    return f"{surname}, {initials}".strip()


def _display_source(source: str) -> str:
    return "arXiv" if source.lower() == "arxiv" else source


def _year(published_date: str) -> str:
    match = re.search(r"\d{4}", published_date or "")
    return match.group(0) if match else "n.d."


def _bibtex_key(paper: Paper) -> str:
    surname = re.sub(r"[^a-z0-9]", "", (paper.authors[0].split()[-1] if paper.authors else "unknown").lower())
    first_title_word = next(
        (re.sub(r"[^a-z0-9]", "", word.lower()) for word in paper.title.split() if word),
        "paper",
    )
    return f"{surname}{_year(paper.published_date)}{first_title_word}"
