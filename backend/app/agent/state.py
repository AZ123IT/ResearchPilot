from typing import Any

from typing_extensions import TypedDict

from app.models.schemas import AgentStep, Citation, EvidenceItem, Finding, LiteratureReview, Paper, ResearchNote, ToolCallLog


class ResearchGraphState(TypedDict, total=False):
    question: str
    max_results: int
    citation_style: str
    searched_papers: list[Paper]
    selected_papers: list[Paper]
    prior_notes: list[ResearchNote]
    reused_notes: list[ResearchNote]
    extracted_findings: list[Finding]
    citations: list[Citation]
    evidence_items: list[EvidenceItem]
    low_confidence_claims: list[str]
    tool_call_logs: list[ToolCallLog]
    warnings: list[str]
    search_source_summary: dict[str, Any]
    fallback_summary: list[str]
    memory_storage: str | None
    cache_used: bool
    steps: list[AgentStep]
    final_review: LiteratureReview
    metadata: dict[str, Any]
