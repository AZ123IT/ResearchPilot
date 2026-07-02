from typing import Any, Literal

from pydantic import BaseModel, Field


CitationStyle = Literal["IEEE", "APA", "BibTeX"]


class Paper(BaseModel):
    paper_id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    published_date: str = ""
    source: str
    url: str
    citation_count: int | None = None


class Finding(BaseModel):
    text: str
    confidence: Literal["high", "medium", "low"] = "low"
    evidence_paper_title: str | None = None
    evidence_snippet: str | None = None


class EvidenceItem(BaseModel):
    claim: str
    paper_id: str
    paper_title: str
    abstract_snippet: str
    confidence: Literal["high", "medium", "low"] | None = None


class Citation(BaseModel):
    paper_id: str
    style: CitationStyle
    citation_text: str


class ResearchNote(BaseModel):
    note_id: str
    paper_id: str | None = None
    title: str | None = None
    content_preview: str
    tag: str | None = None
    source: str | None = None
    url: str | None = None
    score: float = 0
    storage: str = "memory"
    created_at: str | None = None


class AgentStep(BaseModel):
    step_name: str
    status: Literal["success", "warning", "error"]
    tool_name: str | None = None
    summary: str
    input: dict[str, Any] = Field(default_factory=dict)
    output_preview: dict[str, Any] = Field(default_factory=dict)
    duration_ms: float | None = None
    fallback_used: bool = False


class ToolCallLog(BaseModel):
    step_name: str = ""
    tool_name: str
    status: Literal["success", "warning", "error"]
    input: dict[str, Any] = Field(default_factory=dict)
    output_preview: dict[str, Any] = Field(default_factory=dict)
    started_at: str | None = None
    finished_at: str | None = None
    duration_ms: float = 0
    error_message: str | None = None
    fallback_used: bool = False
    error: str | None = None


class LiteratureReview(BaseModel):
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    reused_notes: list[ResearchNote] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    low_confidence_claims: list[str] = Field(default_factory=list)


class ResearchRequest(BaseModel):
    question: str = Field(min_length=3)
    max_results: int = Field(default=5, ge=1, le=20)
    citation_style: CitationStyle = "IEEE"


class ResearchResponse(BaseModel):
    question: str
    steps: list[AgentStep] = Field(default_factory=list)
    tool_call_logs: list[ToolCallLog] = Field(default_factory=list)
    papers: list[Paper] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    prior_notes: list[ResearchNote] = Field(default_factory=list)
    reused_notes: list[ResearchNote] = Field(default_factory=list)
    search_source_summary: dict[str, Any] = Field(default_factory=dict)
    fallback_summary: list[str] = Field(default_factory=list)
    memory_storage: str | None = None
    cache_used: bool = False
    literature_review: LiteratureReview
    citations: list[Citation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
