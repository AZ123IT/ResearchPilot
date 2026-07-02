import time
from dataclasses import dataclass

from clients.arxiv_client import ArxivClient
from clients.semantic_scholar_client import SemanticScholarClient
from data import DEMO_WARNING, demo_mode_enabled, load_demo_papers
from models.schemas import Paper


SUPPORTED_SOURCES = {"arxiv", "semantic_scholar", "auto", "demo"}
SEARCH_CACHE_TTL_SECONDS = 600


@dataclass
class CacheEntry:
    papers: list[dict]
    expires_at: float
    source: str
    search_source_summary: dict


_SEARCH_CACHE: dict[tuple[str, str, int], CacheEntry] = {}


def clear_search_cache() -> None:
    _SEARCH_CACHE.clear()


def expire_search_cache_for_tests() -> None:
    for entry in _SEARCH_CACHE.values():
        entry.expires_at = 0


def search_papers_tool(
    query: str,
    max_results: int = 5,
    source: str = "auto",
    arxiv_client: ArxivClient | None = None,
    semantic_client: SemanticScholarClient | None = None,
) -> dict:
    source = source.lower()
    if source not in SUPPORTED_SOURCES:
        return _empty_result(source, [f"Unsupported source: {source}"])

    max_results = max(1, min(max_results, 20))
    cache_key = _cache_key(query, source, max_results)

    if demo_mode_enabled() or source == "demo":
        return _search_demo(query, max_results)

    if source == "arxiv":
        return _search_single_source(
            query,
            max_results,
            source="arxiv",
            cache_key=cache_key,
            search=lambda: (arxiv_client or ArxivClient()).search(query, max_results),
        )

    if source == "semantic_scholar":
        return _search_single_source(
            query,
            max_results,
            source="semantic_scholar",
            cache_key=cache_key,
            search=lambda: (semantic_client or SemanticScholarClient()).search(query, max_results),
        )

    return _search_auto(query, max_results, cache_key, arxiv_client, semantic_client)


def _search_demo(query: str, max_results: int) -> dict:
    papers = _rank_demo_papers(query, load_demo_papers())[:max_results]
    summary = _summary(demo=len(papers))
    return {
        "source": "demo",
        "papers": _validate_papers(papers),
        "warnings": [DEMO_WARNING],
        "fallback_used": True,
        "cache_used": False,
        "search_source_summary": summary,
    }


def _search_single_source(query: str, max_results: int, source: str, cache_key: tuple[str, str, int], search) -> dict:
    warnings: list[str] = []
    try:
        papers = _validate_papers(search())[:max_results]
        summary = _summary(**{source: len(papers)})
        _store_cache(cache_key, papers, source, summary)
        return {
            "source": source,
            "papers": papers,
            "warnings": warnings,
            "fallback_used": False,
            "cache_used": False,
            "search_source_summary": summary,
        }
    except Exception as exc:
        warnings.append(_search_failure_warning(source, exc))
        cached = _get_cache(cache_key)
        if cached is not None:
            warnings.append(f"Used cached {source} results after search failure.")
            return _cached_result(cached, warnings)
        return _empty_result(source, warnings)


def _search_auto(
    query: str,
    max_results: int,
    cache_key: tuple[str, str, int],
    arxiv_client: ArxivClient | None,
    semantic_client: SemanticScholarClient | None,
) -> dict:
    warnings: list[str] = []
    arxiv_papers: list[dict] = []
    semantic_papers: list[dict] = []
    fallback_used = False

    try:
        arxiv_papers = _validate_papers((arxiv_client or ArxivClient()).search(query, max_results))
    except Exception as exc:
        fallback_used = True
        warnings.append(_search_failure_warning("arxiv", exc))

    if len(arxiv_papers) < max_results:
        try:
            fallback_used = True
            remaining = max_results - len(arxiv_papers)
            semantic_papers = _validate_papers((semantic_client or SemanticScholarClient()).search(query, max_results))
            semantic_papers = semantic_papers[: max(remaining, 0) or max_results]
        except Exception as exc:
            warnings.append(_search_failure_warning("semantic_scholar", exc, fallback=True))

    merged = _dedupe([*arxiv_papers, *semantic_papers])[:max_results]
    if not merged:
        cached = _get_cache(cache_key)
        if cached is not None:
            warnings.append("Used cached auto search results after external search failure.")
            return _cached_result(cached, warnings)

    summary = _summary(arxiv=len(arxiv_papers), semantic_scholar=len(semantic_papers))
    if merged:
        _store_cache(cache_key, merged, "auto", summary)

    return {
        "source": "auto",
        "papers": merged,
        "warnings": warnings,
        "fallback_used": fallback_used,
        "cache_used": False,
        "search_source_summary": summary,
    }


def _validate_papers(papers: list[dict]) -> list[dict]:
    return [Paper.model_validate(paper).model_dump() for paper in papers]


def _dedupe(papers: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped: list[dict] = []
    for paper in papers:
        key = paper.get("paper_id") or _normalize_title(paper.get("title", ""))
        title_key = _normalize_title(paper.get("title", ""))
        if key in seen or title_key in seen:
            continue
        seen.add(key)
        seen.add(title_key)
        deduped.append(paper)
    return deduped


def _store_cache(cache_key: tuple[str, str, int], papers: list[dict], source: str, summary: dict) -> None:
    _SEARCH_CACHE[cache_key] = CacheEntry(
        papers=papers,
        expires_at=time.time() + SEARCH_CACHE_TTL_SECONDS,
        source=source,
        search_source_summary=summary,
    )


def _get_cache(cache_key: tuple[str, str, int]) -> CacheEntry | None:
    entry = _SEARCH_CACHE.get(cache_key)
    if entry is None or entry.expires_at <= time.time():
        return None
    return entry


def _cached_result(entry: CacheEntry, warnings: list[str]) -> dict:
    summary = dict(entry.search_source_summary)
    summary["cache"] = len(entry.papers)
    return {
        "source": "cache",
        "papers": entry.papers,
        "warnings": warnings,
        "fallback_used": True,
        "cache_used": True,
        "search_source_summary": summary,
    }


def _empty_result(source: str, warnings: list[str]) -> dict:
    return {
        "source": source,
        "papers": [],
        "warnings": warnings,
        "fallback_used": bool(warnings),
        "cache_used": False,
        "search_source_summary": _summary(),
    }


def _summary(arxiv: int = 0, semantic_scholar: int = 0, demo: int = 0) -> dict:
    return {"arxiv": arxiv, "semantic_scholar": semantic_scholar, "demo": demo, "cache": 0}


def _cache_key(query: str, source: str, max_results: int) -> tuple[str, str, int]:
    return (" ".join(query.lower().split()), source, max_results)


def _normalize_title(title: str) -> str:
    return " ".join(title.lower().split())


def _source_label(source: str) -> str:
    return "Semantic Scholar" if source == "semantic_scholar" else "arXiv"


def _rank_demo_papers(query: str, papers: list[dict]) -> list[dict]:
    query_terms = set(_normalize_title(query).split())

    def score(paper: dict) -> tuple[int, str]:
        haystack = _normalize_title(f"{paper.get('title', '')} {paper.get('abstract', '')}")
        return (len(query_terms & set(haystack.split())), paper.get("published_date", ""))

    return sorted(papers, key=score, reverse=True)


def _search_failure_warning(source: str, exc: Exception, fallback: bool = False) -> str:
    label = _source_label(source)
    message = str(exc) or exc.__class__.__name__
    is_timeout = "timeout" in exc.__class__.__name__.lower() or "timed out" in message.lower()
    if is_timeout:
        return f"{label} timeout while searching; {'fallback failed' if fallback else 'using fallback path when available'}: {message}"
    if fallback:
        return f"{label} fallback search failed: {message}"
    return f"{label} search failed: {message}"
