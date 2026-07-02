from clients.arxiv_client import ArxivClient
from clients.semantic_scholar_client import SemanticScholarClient
from data import find_demo_paper
from models.schemas import Paper


def fetch_paper_detail_tool(
    paper_id: str,
    source: str,
    arxiv_client: ArxivClient | None = None,
    semantic_client: SemanticScholarClient | None = None,
) -> dict:
    source = source.lower()
    warnings: list[str] = []

    try:
        if source == "arxiv":
            paper = (arxiv_client or ArxivClient()).fetch_by_id(paper_id)
        elif source == "semantic_scholar":
            paper = (semantic_client or SemanticScholarClient()).fetch_by_id(paper_id)
            if paper is None:
                warnings.append("Semantic Scholar detail lookup is not implemented; using search result metadata when available.")
        elif source == "demo":
            paper = find_demo_paper(paper_id)
        else:
            return {"paper": None, "warnings": [f"Unsupported source: {source}"]}
    except Exception as exc:
        return {"paper": None, "warnings": [f"{source} detail lookup failed: {exc}"]}

    return {"paper": Paper.model_validate(paper).model_dump() if paper else None, "warnings": warnings}
