import xml.etree.ElementTree as ET

import httpx


ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


class ArxivClient:
    def __init__(self, timeout_seconds: float = 10):
        self.timeout_seconds = timeout_seconds
        self.base_url = "https://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int) -> list[dict]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
        return self._parse_feed(response.text)

    def fetch_by_id(self, paper_id: str) -> dict | None:
        params = {"id_list": paper_id}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
        papers = self._parse_feed(response.text)
        return papers[0] if papers else None

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
