from langgraph.graph import END, START, StateGraph

from app.agent.nodes import (
    extract_summary_node,
    fetch_paper_details_node,
    format_citations_node,
    generate_final_review_node,
    plan_research_task,
    save_notes_node,
    search_notes_node,
    search_papers_node,
    verify_evidence_node,
)
from app.agent.state import ResearchGraphState
from app.models.schemas import LiteratureReview, ResearchRequest, ResearchResponse


def build_research_graph():
    workflow = StateGraph(ResearchGraphState)
    workflow.add_node("plan_research_task", plan_research_task)
    workflow.add_node("search_notes_node", search_notes_node)
    workflow.add_node("search_papers_node", search_papers_node)
    workflow.add_node("fetch_paper_details_node", fetch_paper_details_node)
    workflow.add_node("extract_summary_node", extract_summary_node)
    workflow.add_node("verify_evidence_node", verify_evidence_node)
    workflow.add_node("format_citations_node", format_citations_node)
    workflow.add_node("save_notes_node", save_notes_node)
    workflow.add_node("generate_final_review_node", generate_final_review_node)

    workflow.add_edge(START, "plan_research_task")
    workflow.add_edge("plan_research_task", "search_notes_node")
    workflow.add_edge("search_notes_node", "search_papers_node")
    workflow.add_edge("search_papers_node", "fetch_paper_details_node")
    workflow.add_edge("fetch_paper_details_node", "extract_summary_node")
    workflow.add_edge("extract_summary_node", "verify_evidence_node")
    workflow.add_edge("verify_evidence_node", "format_citations_node")
    workflow.add_edge("format_citations_node", "save_notes_node")
    workflow.add_edge("save_notes_node", "generate_final_review_node")
    workflow.add_edge("generate_final_review_node", END)
    return workflow.compile()


def run_research_graph(request: ResearchRequest) -> ResearchResponse:
    initial_state: ResearchGraphState = {
        "question": request.question,
        "max_results": request.max_results,
        "citation_style": request.citation_style,
        "searched_papers": [],
        "selected_papers": [],
        "prior_notes": [],
        "reused_notes": [],
        "extracted_findings": [],
        "citations": [],
        "evidence_items": [],
        "low_confidence_claims": [],
        "tool_call_logs": [],
        "warnings": [],
        "search_source_summary": {},
        "fallback_summary": [],
        "memory_storage": None,
        "cache_used": False,
        "steps": [],
        "final_review": LiteratureReview(summary=""),
        "metadata": {},
    }
    final_state = build_research_graph().invoke(initial_state)
    return ResearchResponse(
        question=request.question,
        steps=final_state.get("steps", []),
        tool_call_logs=final_state.get("tool_call_logs", []),
        papers=final_state.get("selected_papers", []),
        evidence_items=final_state.get("evidence_items", []),
        prior_notes=final_state.get("prior_notes", []),
        reused_notes=final_state.get("reused_notes", []),
        search_source_summary=final_state.get("search_source_summary", {}),
        fallback_summary=final_state.get("fallback_summary", []),
        memory_storage=final_state.get("memory_storage"),
        cache_used=final_state.get("cache_used", False),
        literature_review=final_state.get("final_review", LiteratureReview(summary="")),
        citations=final_state.get("citations", []),
        warnings=final_state.get("warnings", []),
    )
