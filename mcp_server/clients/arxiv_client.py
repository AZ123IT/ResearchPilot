import re
import xml.etree.ElementTree as ET

import httpx


ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
MAX_QUERY_TERMS = 6

# Question scaffolding that carries no topic signal. Left in an arXiv query, these words
# match almost every paper, so results drift to whatever was submitted most recently.
QUERY_STOPWORDS = {
    "a", "about", "an", "and", "approaches", "are", "best", "between", "can", "common", "current",
    "do", "does", "for", "from", "how", "improve", "improving", "in", "is", "latest", "methods",
    "new", "of", "on", "recent", "should", "techniques", "the", "there", "to", "use", "used",
    "uses", "using", "via", "what", "when", "which", "who", "why", "with", "work", "works",
}


def build_arxiv_query(question: str, operator: str = "AND") -> str:
    """Turn a natural-language question into a fielded arXiv query over its topic terms."""
    terms: list[str] = []
    for term in re.findall(r"[A-Za-z0-9][A-Za-z0-9-]*", question):
        lowered = term.lower()
        if lowered in QUERY_STOPWORDS or len(lowered) < 2 or lowered in terms:
            continue
        terms.append(lowered)
    if not terms:
        return f'all:"{question.strip()}"'
    return f" {operator} ".join(f"all:{term}" for term in terms[:MAX_QUERY_TERMS])


class ArxivClient:
    def __init__(self, timeout_seconds: float = 10, http_client: httpx.Client | None = None):
        self.timeout_seconds = timeout_seconds
        self.http_client = http_client
        self.base_url = "https://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int) -> list[dict]:
        # Require every topic term first; loosen to any term only if that finds nothing.
        papers = self._query(build_arxiv_query(query, "AND"), max_results)
        if not papers:
            papers = self._query(build_arxiv_query(query, "OR"), max_results)
        return papers

    def fetch_by_id(self, paper_id: str) -> dict | None:
        papers = self._parse_feed(self._get({"id_list": paper_id}))
        return papers[0] if papers else None

    def _query(self, search_query: str, max_results: int) -> list[dict]:
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        return self._parse_feed(self._get(params))

    def _get(self, params: dict) -> str:
        if self.http_client is not None:
            response = self.http_client.get(self.base_url, params=params)
        else:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(self.base_url, params=params)
        response.raise_for_status()
        return response.text

    def _parse_feed(self, xml_text: str) -> list[dict]:
        root = ET.fromstring(xml_text)
        papers = []
        for entry in root.findall("atom:entry", ATOM_NS):
            url = _text(entry, "atom:id")
            paper_id = url.rstrip("/").split("/")[-1]
            papers.append(
                {
                    "paper_id": paper_id,
                    "title": _normalize(_text(entry, "atom:title")),
                    "authors": [
                        _normalize(_text(author, "atom:name"))
                        for author in entry.findall("atom:author", ATOM_NS)
                    ],
                    "abstract": _normalize(_text(entry, "atom:summary")),
                    "published_date": _text(entry, "atom:published")[:10],
                    "source": "arxiv",
                    "url": url,
                    "citation_count": None,
                }
            )
        return papers


def _text(element: ET.Element, path: str) -> str:
    found = element.find(path, ATOM_NS)
    return found.text.strip() if found is not None and found.text else ""


def _normalize(text: str) -> str:
    return " ".join((text or "").split())
