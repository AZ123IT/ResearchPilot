import os

import httpx


class SemanticScholarClient:
    def __init__(self, timeout_seconds: float = 10, http_client: httpx.Client | None = None):
        self.timeout_seconds = timeout_seconds
        self.http_client = http_client
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    def search(self, query: str, max_results: int) -> list[dict]:
        params = {
            "query": query,
            "limit": max_results,
            "fields": "paperId,title,authors,abstract,year,publicationDate,url,citationCount",
        }
        headers = {}
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        if api_key:
            headers["x-api-key"] = api_key

        if self.http_client is not None:
            response = self.http_client.get(self.base_url, params=params, headers=headers)
        else:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(self.base_url, params=params, headers=headers)

        response.raise_for_status()
        payload = response.json()
        return [self._normalize_paper(item) for item in payload.get("data", []) if item.get("paperId")]

    def fetch_by_id(self, paper_id: str) -> dict | None:
        return None

    def _normalize_paper(self, item: dict) -> dict:
        paper_id = item.get("paperId", "")
        return {
            "paper_id": paper_id,
            "title": item.get("title") or "Untitled Semantic Scholar paper",
            "authors": [author.get("name", "") for author in item.get("authors", []) if author.get("name")],
            "abstract": item.get("abstract") or "",
            "published_date": item.get("publicationDate") or (str(item.get("year")) if item.get("year") else ""),
            "source": "semantic_scholar",
            "url": item.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}",
            "citation_count": item.get("citationCount"),
        }
