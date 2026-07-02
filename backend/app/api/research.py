from fastapi import APIRouter

from app.agent.graph import run_research_graph
from app.models.schemas import ResearchRequest, ResearchResponse


router = APIRouter(prefix="/api/research", tags=["research"])


@router.post("/run", response_model=ResearchResponse)
def run_research(request: ResearchRequest) -> ResearchResponse:
    return run_research_graph(request)
