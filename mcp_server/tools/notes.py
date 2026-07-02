import os
from datetime import UTC, datetime
from uuid import uuid4

from models.schemas import Note


_MEMORY_NOTES: list[Note] = []


def clear_memory_notes() -> None:
    _MEMORY_NOTES.clear()


def save_to_notes_tool(
    content: str,
    paper_id: str | None = None,
    tag: str | None = None,
    title: str | None = None,
    source: str | None = None,
    url: str | None = None,
) -> dict:
    note = Note(
        note_id=str(uuid4()),
        content=content,
        paper_id=paper_id,
        title=title,
        tag=tag,
        source=source,
        url=url,
        created_at=datetime.now(UTC).isoformat(),
    )
    warnings: list[str] = []

    if _supabase_configured():
        try:
            from supabase import create_client

            client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
            table = os.getenv("SUPABASE_NOTES_TABLE", "research_notes")
            insert_payload = {
                "id": note.note_id,
                "paper_id": note.paper_id,
                "title": note.title,
                "content": note.content,
                "tag": note.tag,
                "source": note.source,
                "url": note.url,
                "created_at": note.created_at,
            }
            client.table(table).insert(insert_payload).execute()
            return {"storage": "supabase", "note": note.model_dump(), "warnings": warnings}
        except Exception as exc:
            warnings.append(f"Supabase note save failed; used memory fallback: {exc}")
    else:
        warnings.append("Supabase credentials are not configured; saved note to in-memory storage.")

    _MEMORY_NOTES.append(note)
    return {"storage": "memory", "note": note.model_dump(), "warnings": warnings}


def search_notes_tool(query: str, top_k: int = 5) -> dict:
    warnings: list[str] = []
    if _supabase_configured():
        try:
            notes = _search_supabase_notes(query, top_k)
            return {"storage": "supabase", "notes": notes, "warnings": warnings}
        except Exception as exc:
            warnings.append(f"Supabase note search failed; used memory fallback: {exc}")

    warnings.append("Supabase credentials are not configured; using in-memory note search.")
    return {
        "storage": "memory",
        "notes": _search_memory_notes(query, top_k),
        "warnings": warnings,
    }


def _search_supabase_notes(query: str, top_k: int) -> list[dict]:
    from supabase import create_client

    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    table = os.getenv("SUPABASE_NOTES_TABLE", "research_notes")
    response = client.table(table).select("*").limit(max(top_k * 5, top_k)).execute()
    rows = getattr(response, "data", []) or []
    scored = []
    query_terms = _terms(query)
    for row in rows:
        content = row.get("content") or ""
        haystack = f"{content} {row.get('title') or ''} {row.get('tag') or ''} {row.get('paper_id') or ''}"
        score = len(query_terms & _terms(haystack))
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [_note_result_from_row(row, score, "supabase") for score, row in scored[:top_k]]


def _search_memory_notes(query: str, top_k: int) -> list[dict]:
    query_terms = _terms(query)
    scored = []
    for note in _MEMORY_NOTES:
        note_terms = _terms(f"{note.content} {note.title or ''} {note.tag or ''} {note.paper_id or ''}")
        score = len(query_terms & note_terms)
        if score > 0:
            scored.append((score, note))
    scored.sort(key=lambda item: item[0], reverse=True)
    deduped = _dedupe_scored_notes(scored)
    return [_note_result(note, score, "memory") for score, note in deduped[:top_k]]


def _note_result(note: Note, score: int, storage: str) -> dict:
    return {
        "note_id": note.note_id,
        "paper_id": note.paper_id,
        "title": note.title,
        "content": note.content,
        "content_preview": _preview(note.content),
        "tag": note.tag,
        "source": note.source,
        "url": note.url,
        "score": score,
        "storage": storage,
        "created_at": note.created_at,
    }


def _note_result_from_row(row: dict, score: int, storage: str) -> dict:
    content = row.get("content") or ""
    return {
        "note_id": str(row.get("id") or row.get("note_id") or ""),
        "paper_id": row.get("paper_id"),
        "title": row.get("title"),
        "content": content,
        "content_preview": _preview(content),
        "tag": row.get("tag"),
        "source": row.get("source"),
        "url": row.get("url"),
        "score": score,
        "storage": storage,
        "created_at": row.get("created_at"),
    }


def _dedupe_scored_notes(scored: list[tuple[int, Note]]) -> list[tuple[int, Note]]:
    seen: set[tuple[str | None, str | None, str]] = set()
    deduped: list[tuple[int, Note]] = []
    for score, note in scored:
        key = (note.paper_id, note.title, " ".join(note.content.split()))
        if key in seen:
            continue
        seen.add(key)
        deduped.append((score, note))
    return deduped


def _supabase_configured() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


def _terms(text: str) -> set[str]:
    normalized = "".join(char.lower() if char.isalnum() else " " for char in text)
    return {part for part in normalized.split() if len(part) > 2}


def _preview(text: str, limit: int = 240) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    return f"{clean[: limit - 3].rstrip()}..."
