import asyncio
from datetime import UTC, datetime
from threading import Thread
from typing import Any, Awaitable, Callable

from app.agent.prompts import FALLBACK_METHOD_NOTE
from app.agent.state import ResearchGraphState
from app.core.config import get_settings
from app.llm.deepseek_client import DeepSeekClient
from app.mcp_client.client import get_research_tool_client
from app.models.schemas import AgentStep, Citation, EvidenceItem, Finding, LiteratureReview, Paper, ResearchNote, ToolCallLog
from app.services.verification_service import verify_findings


def plan_research_task(state: ResearchGraphState) -> dict[str, Any]:
    planned_sources = ["demo"] if get_settings().demo_mode else ["arxiv", "semantic_scholar"]
    return {
        "steps": _with_step(
            state,
            AgentStep(
                step_name="plan_research_task",
                status="success",
                summary="Prepared a scoped academic search and evidence review plan.",
                input={"question": state["question"], "max_results": state["max_results"]},
                output_preview={"planned_sources": planned_sources, "citation_style": state["citation_style"]},
            ),
        )
    }


def search_notes_node(state: ResearchGraphState) -> dict[str, Any]:
    client = get_research_tool_client()
    tool_input = {"query": state["question"], "top_k": 3}
    result, log = _call_tool(
        state,
        step_name="search_notes",
        tool_name="search_notes",
        tool_input=tool_input,
        call=lambda: client.search_notes(**tool_input),
    )
    warnings = _unique([*state.get("warnings", []), *result.get("warnings", [])])
    if log.status == "error" and log.error_message:
        warnings.append(f"search_notes failed: {log.error_message}")
    notes = _note_models(result.get("notes", []))
    storage = result.get("storage") or state.get("memory_storage")

    return {
        "prior_notes": notes,
        "reused_notes": notes,
        "memory_storage": storage,
        "warnings": warnings,
        "tool_call_logs": _with_log(state, log),
        "steps": _with_step(
            state,
            AgentStep(
                step_name="search_notes",
                status="success" if log.status == "error" else log.status,
                tool_name="search_notes",
                summary=f"Found {len(notes)} reusable research notes.",
                input=tool_input,
                output_preview={"note_count": len(notes), "storage": storage},
                duration_ms=log.duration_ms,
                fallback_used=log.fallback_used,
            ),
        ),
    }


def search_papers_node(state: ResearchGraphState) -> dict[str, Any]:
    client = get_research_tool_client()
    tool_input = {
        "query": state["question"],
        "max_results": state["max_results"],
        "source": "auto",
    }
    result, log = _call_tool(
        state,
        step_name="search_papers",
        tool_name="search_papers",
        tool_input=tool_input,
        call=lambda: client.search_papers(**tool_input),
    )
    papers = [Paper.model_validate(paper) for paper in result.get("papers", [])]
    warnings = _unique([*state.get("warnings", []), *result.get("warnings", [])])
    fallback_summary = list(state.get("fallback_summary", []))
    if result.get("fallback_used"):
        if result.get("source") == "demo":
            fallback_summary.append("Demo mode used local fixture papers instead of external academic APIs.")
        else:
            fallback_summary.append(f"Paper search used fallback path from source={result.get('source')}.")
    if result.get("cache_used"):
        fallback_summary.append("Paper search used cached results.")

    return {
        "searched_papers": papers,
        "warnings": warnings,
        "search_source_summary": result.get("search_source_summary", state.get("search_source_summary", {})),
        "fallback_summary": _unique(fallback_summary),
        "cache_used": bool(result.get("cache_used", False)),
        "tool_call_logs": _with_log(state, log),
        "steps": _with_step(
            state,
            AgentStep(
                step_name="search_papers",
                status=log.status,
                tool_name="search_papers",
                summary=f"Retrieved {len(papers)} candidate papers.",
                input=tool_input,
                output_preview={
                    "paper_count": len(papers),
                    "source": result.get("source"),
                    "cache_used": bool(result.get("cache_used", False)),
                },
                duration_ms=log.duration_ms,
                fallback_used=log.fallback_used,
            ),
        ),
    }


def fetch_paper_details_node(state: ResearchGraphState) -> dict[str, Any]:
    client = get_research_tool_client()
    selected: list[Paper] = []
    logs = list(state.get("tool_call_logs", []))
    warnings = list(state.get("warnings", []))

    for paper in state.get("searched_papers", []):
        tool_input = {"paper_id": paper.paper_id, "source": paper.source}
        result, log = _call_tool(
            state,
            step_name="fetch_paper_details",
            tool_name="fetch_paper_detail",
            tool_input=tool_input,
            call=lambda paper_id=paper.paper_id, source=paper.source: client.fetch_paper_detail(paper_id, source),
        )
        logs.append(log)
        warnings.extend(result.get("warnings", []))
        if result.get("paper"):
            selected.append(Paper.model_validate(result["paper"]))
        else:
            selected.append(paper)
            if log.status == "error":
                warnings.append(f"Used search result metadata for {paper.paper_id} after detail lookup failed.")

    step_status = _aggregate_status(logs[len(state.get("tool_call_logs", [])) :])
    duration_ms = _sum_duration(logs[len(state.get("tool_call_logs", [])) :])
    fallback_used = any(log.fallback_used for log in logs[len(state.get("tool_call_logs", [])) :])

    return {
        "selected_papers": selected,
        "warnings": _unique(warnings),
        "tool_call_logs": logs,
        "steps": _with_step(
            state,
            AgentStep(
                step_name="fetch_paper_details",
                status=step_status,
                tool_name="fetch_paper_detail",
                summary=f"Fetched detail records for {len(selected)} papers.",
                input={"paper_ids": [paper.paper_id for paper in state.get("searched_papers", [])]},
                output_preview={"selected_count": len(selected)},
                duration_ms=duration_ms,
                fallback_used=fallback_used,
            ),
        ),
    }


def extract_summary_node(state: ResearchGraphState) -> dict[str, Any]:
    papers = list(state.get("selected_papers", []))
    warnings = list(state.get("warnings", []))
    findings: list[Finding]
    method_note = FALLBACK_METHOD_NOTE
    fallback_used = False

    if get_settings().deepseek_api_key and papers:
        try:
            findings = DeepSeekClient().extract_findings(state["question"], papers)
            method_note = "Findings were generated by DeepSeek from supplied paper abstracts."
        except Exception as exc:
            fallback_used = True
            warnings.append(f"DeepSeek extraction failed; used deterministic fallback: {exc}")
            findings = _fallback_findings(papers, state["question"])
    else:
        fallback_used = True
        warnings.append("DeepSeek API key is not configured; using deterministic abstract-based fallback.")
        findings = _fallback_findings(papers, state["question"])

    return {
        "extracted_findings": findings,
        "warnings": _unique(warnings),
        "steps": _with_step(
            state,
            AgentStep(
                step_name="extract_summary",
                status="success",
                summary="Extracted candidate findings from paper abstracts.",
                input={"paper_count": len(papers)},
                output_preview={"finding_count": len(findings), "method": method_note},
                fallback_used=fallback_used,
            ),
        ),
        "metadata": {**state.get("metadata", {}), "summary_method": method_note},
    }


def verify_evidence_node(state: ResearchGraphState) -> dict[str, Any]:
    papers = list(state.get("selected_papers", []))
    verified = verify_findings(list(state.get("extracted_findings", [])), papers)
    evidence_items = [
        EvidenceItem(
            claim=finding.text,
            paper_id=_paper_id_for_title(finding.evidence_paper_title, papers),
            paper_title=finding.evidence_paper_title or "",
            abstract_snippet=finding.evidence_snippet or "",
            confidence=finding.confidence,
        )
        for finding in verified
        if finding.evidence_paper_title and finding.evidence_snippet
    ]
    low_confidence = [finding.text for finding in verified if finding.confidence == "low"]

    return {
        "extracted_findings": verified,
        "evidence_items": evidence_items,
        "low_confidence_claims": low_confidence,
        "steps": _with_step(
            state,
            AgentStep(
                step_name="verify_evidence",
                status="success",
                summary="Checked findings against available abstracts with keyword overlap.",
                input={"finding_count": len(verified), "paper_count": len(papers)},
                output_preview={
                    "supported_claims": len(evidence_items),
                    "low_confidence_claims": len(low_confidence),
                },
            ),
        ),
    }


def format_citations_node(state: ResearchGraphState) -> dict[str, Any]:
    client = get_research_tool_client()
    citations: list[Citation] = []
    logs = list(state.get("tool_call_logs", []))
    warnings = list(state.get("warnings", []))

    for paper in state.get("selected_papers", []):
        paper_payload = paper.model_dump()
        tool_input = {"paper": paper_payload, "style": state["citation_style"]}
        result, log = _call_tool(
            state,
            step_name="format_citations",
            tool_name="format_citation",
            tool_input=tool_input,
            call=lambda payload=paper_payload: client.format_citation(payload, state["citation_style"]),
        )
        logs.append(log)
        warnings.extend(result.get("warnings", []))
        if result.get("citation_text"):
            citations.append(
                Citation(
                    paper_id=result.get("paper_id", paper.paper_id),
                    style=result.get("style", state["citation_style"]),
                    citation_text=result["citation_text"],
                )
            )

    new_logs = logs[len(state.get("tool_call_logs", [])) :]
    return {
        "citations": citations,
        "warnings": _unique(warnings),
        "tool_call_logs": logs,
        "steps": _with_step(
            state,
            AgentStep(
                step_name="format_citations",
                status=_aggregate_status(new_logs),
                tool_name="format_citation",
                summary=f"Formatted {len(citations)} citations.",
                input={"style": state["citation_style"]},
                output_preview={"citation_count": len(citations)},
                duration_ms=_sum_duration(new_logs),
                fallback_used=any(log.fallback_used for log in new_logs),
            ),
        ),
    }


def save_notes_node(state: ResearchGraphState) -> dict[str, Any]:
    client = get_research_tool_client()
    warnings = list(state.get("warnings", []))
    logs = list(state.get("tool_call_logs", []))
    saved_count = 0

    for finding in state.get("extracted_findings", []):
        if finding.confidence == "low":
            continue
        paper_id = _paper_id_for_title(finding.evidence_paper_title, state.get("selected_papers", []))
        tool_input = {"content": finding.text, "paper_id": paper_id or None, "tag": "auto-literature-review"}
        evidence_paper = _paper_for_title(finding.evidence_paper_title, state.get("selected_papers", []))
        tool_input.update(
            {
                "title": evidence_paper.title if evidence_paper else finding.evidence_paper_title,
                "source": evidence_paper.source if evidence_paper else None,
                "url": evidence_paper.url if evidence_paper else None,
            }
        )
        result, log = _call_tool(
            state,
            step_name="save_notes",
            tool_name="save_to_notes",
            tool_input=tool_input,
            call=lambda payload=tool_input: client.save_to_notes(
                payload["content"],
                payload["paper_id"],
                payload["tag"],
                payload["title"],
                payload["source"],
                payload["url"],
            ),
        )
        warnings.extend(result.get("warnings", []))
        logs.append(log)
        if log.status != "error":
            saved_count += 1

    new_logs = logs[len(state.get("tool_call_logs", [])) :]
    return {
        "warnings": _unique(warnings),
        "tool_call_logs": logs,
        "steps": _with_step(
            state,
            AgentStep(
                step_name="save_notes",
                status=_aggregate_status(new_logs),
                tool_name="save_to_notes",
                summary=f"Saved {saved_count} supported findings to research memory.",
                output_preview={"saved_count": saved_count},
                duration_ms=_sum_duration(new_logs),
                fallback_used=any(log.fallback_used for log in new_logs),
            ),
        ),
    }


def generate_final_review_node(state: ResearchGraphState) -> dict[str, Any]:
    findings = list(state.get("extracted_findings", []))
    supported = [finding for finding in findings if finding.confidence in {"high", "medium"}]
    papers = list(state.get("selected_papers", []))
    reused_notes = list(state.get("reused_notes", []))
    source_label = _source_label(papers)
    low_confidence_count = len(state.get("low_confidence_claims", []))
    question_text = _sentence_text(state["question"])
    summary = (
        f"Reviewed {len(papers)} {source_label} for: {question_text} "
        f"Found {len(supported)} evidence-backed claims"
        f"{f' and flagged {low_confidence_count} low-confidence claims' if low_confidence_count else ''}."
        if papers
        else f"No papers were available to review for: {question_text}"
    )
    if reused_notes:
        summary = f"{summary} Reused {len(reused_notes)} prior research notes."
    limitations = [
        "The workflow uses abstracts rather than full paper PDFs, so section-level evidence is not available.",
        "External metadata sources may omit abstracts, publication dates, or citation counts.",
    ]
    if any(paper.source == "demo" for paper in papers):
        limitations.append("Demo mode uses local fixture papers for stable local presentation and does not represent live external search.")
    if not get_settings().deepseek_api_key:
        limitations.append("No DeepSeek API key was configured, so findings were generated by deterministic abstract extraction.")
    review = LiteratureReview(
        summary=summary,
        key_findings=[finding.text for finding in supported],
        findings=findings,
        reused_notes=reused_notes,
        methods=[
            state.get("metadata", {}).get("summary_method", FALLBACK_METHOD_NOTE),
            "LangGraph runs planning, note search, paper search, detail lookup, evidence verification, citation formatting, and memory save steps.",
            "Evidence confidence is estimated with abstract keyword overlap; weak claims remain visible as low-confidence output.",
        ],
        limitations=limitations,
        low_confidence_claims=list(state.get("low_confidence_claims", [])),
    )

    return {
        "final_review": review,
        "steps": _with_step(
            state,
            AgentStep(
                step_name="generate_final_review",
                status="success",
                summary="Generated a structured literature review response.",
                output_preview={"key_findings": len(review.key_findings)},
            ),
        ),
    }


def _call_tool(
    state: ResearchGraphState,
    step_name: str,
    tool_name: str,
    tool_input: dict[str, Any],
    call: Callable[[], Awaitable[dict]],
) -> tuple[dict, ToolCallLog]:
    started = datetime.now(UTC)
    error_message = None
    fallback_used = False
    try:
        result = _run_async(call())
        metadata = result.pop("_meta", {}) if isinstance(result, dict) else {}
        fallback_used = bool(metadata.get("fallback_used", False))
        status = "warning" if result.get("warnings") or fallback_used else "success"
    except Exception as exc:
        result = {}
        status = "error"
        error_message = str(exc)

    finished = datetime.now(UTC)
    duration_ms = round((finished - started).total_seconds() * 1000, 2)
    log = ToolCallLog(
        step_name=step_name,
        tool_name=tool_name,
        status=status,
        input=_sanitize(tool_input),
        output_preview=_preview(result),
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        duration_ms=duration_ms,
        error_message=error_message,
        error=error_message,
        fallback_used=fallback_used,
    )
    return result, log


def _run_async(awaitable: Awaitable[dict]) -> dict:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(awaitable)

    holder: dict[str, Any] = {}

    def runner() -> None:
        try:
            holder["result"] = asyncio.run(awaitable)
        except Exception as exc:  # pragma: no cover - defensive path for async hosts
            holder["error"] = exc

    thread = Thread(target=runner)
    thread.start()
    thread.join()
    if "error" in holder:
        raise holder["error"]
    return holder["result"]


def _fallback_findings(papers: list[Paper], question: str) -> list[Finding]:
    findings = []
    for paper in papers:
        best_sentence = _best_abstract_sentence(paper.abstract, question)
        if best_sentence:
            findings.append(Finding(text=f"{paper.title}: {best_sentence}"))
        else:
            findings.append(Finding(text=f"{paper.title}: the available metadata does not include enough abstract evidence for a supported claim."))
    return findings


def _best_abstract_sentence(text: str, question: str) -> str:
    clean = " ".join((text or "").split())
    if not clean:
        return ""
    sentences = [part.strip() for part in clean.split(".") if part.strip()]
    if not sentences:
        return clean
    question_terms = _terms(question)
    best = max(sentences, key=lambda sentence: len(question_terms & _terms(sentence)))
    return f"{best}."


def _paper_id_for_title(title: str | None, papers: list[Paper]) -> str:
    paper = _paper_for_title(title, papers)
    return paper.paper_id if paper else ""


def _paper_for_title(title: str | None, papers: list[Paper]) -> Paper | None:
    for paper in papers:
        if paper.title == title:
            return paper
    return None


def _note_models(notes: list[dict]) -> list[ResearchNote]:
    normalized: list[ResearchNote] = []
    for note in notes:
        content_preview = note.get("content_preview") or note.get("content") or ""
        normalized.append(
            ResearchNote(
                note_id=str(note.get("note_id") or note.get("id") or ""),
                paper_id=note.get("paper_id"),
                title=note.get("title"),
                content_preview=content_preview,
                tag=note.get("tag"),
                source=note.get("source"),
                url=note.get("url"),
                score=float(note.get("score", 0) or 0),
                storage=note.get("storage", "memory"),
                created_at=note.get("created_at"),
            )
        )
    return normalized


def _source_label(papers: list[Paper]) -> str:
    if not papers:
        return "papers"
    sources = {paper.source for paper in papers}
    if sources == {"demo"}:
        return "demo papers"
    if len(sources) == 1:
        return f"{next(iter(sources))} papers"
    return "papers"


def _sentence_text(text: str) -> str:
    clean = " ".join(text.split()).strip()
    if not clean:
        return ""
    return clean if clean[-1] in ".?!" else f"{clean}."


def _terms(text: str) -> set[str]:
    return {part.lower() for part in "".join(char if char.isalnum() else " " for char in text).split() if len(part) > 3}


def _unique(items: list[str]) -> list[str]:
    seen = set()
    unique = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _with_step(state: ResearchGraphState, step: AgentStep) -> list[AgentStep]:
    return [*state.get("steps", []), step]


def _with_log(state: ResearchGraphState, log: ToolCallLog) -> list[ToolCallLog]:
    return [*state.get("tool_call_logs", []), log]


def _aggregate_status(logs: list[ToolCallLog]) -> str:
    if any(log.status == "error" for log in logs):
        return "error"
    if any(log.status == "warning" for log in logs):
        return "warning"
    return "success"


def _sum_duration(logs: list[ToolCallLog]) -> float:
    return round(sum(log.duration_ms for log in logs), 2)


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized = {}
        for key, nested in value.items():
            lowered = key.lower()
            if any(secret in lowered for secret in ("key", "token", "secret", "password")):
                sanitized[key] = "[redacted]"
            else:
                sanitized[key] = _sanitize(nested)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item) for item in value[:5]]
    if isinstance(value, str) and len(value) > 360:
        return f"{value[:357]}..."
    return value


def _preview(result: dict) -> dict[str, Any]:
    if not isinstance(result, dict):
        return {"result": str(result)[:240]}
    if "papers" in result:
        papers = result.get("papers", [])
        first = papers[0] if papers else {}
        return {
            "paper_count": len(papers),
            "first_title": first.get("title"),
            "source": result.get("source"),
            "cache_used": result.get("cache_used", False),
        }
    if "paper" in result:
        paper = result.get("paper") or {}
        return {"paper_id": paper.get("paper_id"), "title": paper.get("title")}
    if "citation_text" in result:
        return {
            "paper_id": result.get("paper_id"),
            "style": result.get("style"),
            "citation_length": len(result.get("citation_text", "")),
        }
    if "notes" in result:
        return {"storage": result.get("storage"), "note_count": len(result.get("notes", []))}
    if "storage" in result:
        return {"storage": result.get("storage"), "warning_count": len(result.get("warnings", []))}
    return _sanitize({key: value for key, value in result.items() if key != "_meta"})
