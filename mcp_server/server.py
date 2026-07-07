from mcp.server.fastmcp import FastMCP

from tools.fetch_paper_detail import fetch_paper_detail_tool
from tools.format_citation import format_citation_tool
from tools.notes import save_to_notes_tool, search_notes_tool
from tools.search_papers import search_papers_tool


mcp = FastMCP("ResearchPilot Research MCP Server")


@mcp.tool()
def search_papers(query: str, max_results: int = 5, source: str = "auto") -> dict:
    """Search academic papers from arXiv or a configured fallback source."""
    return search_papers_tool(query=query, max_results=max_results, source=source)


@mcp.tool()
def fetch_paper_detail(paper_id: str, source: str = "arxiv") -> dict:
    """Fetch detailed metadata for a paper."""
    return fetch_paper_detail_tool(paper_id=paper_id, source=source)


@mcp.tool()
def format_citation(paper: dict, style: str = "IEEE") -> dict:
    """Format a paper citation as IEEE, APA, or BibTeX."""
    return format_citation_tool(paper=paper, style=style)


@mcp.tool()
def save_to_notes(
    content: str,
    paper_id: str | None = None,
    tag: str | None = None,
    title: str | None = None,
    source: str | None = None,
    url: str | None = None,
) -> dict:
    """Save a research note to Supabase when configured, otherwise memory."""
    return save_to_notes_tool(content=content, paper_id=paper_id, tag=tag, title=title, source=source, url=url)


@mcp.tool()
def search_notes(query: str, top_k: int = 5) -> dict:
    """Search previously saved research notes."""
    return search_notes_tool(query=query, top_k=top_k)


if __name__ == "__main__":
    mcp.run()
