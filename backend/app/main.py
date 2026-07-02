from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.research import router as research_router
from app.mcp_client.client import close_research_tool_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_research_tool_client()


app = FastAPI(
    title="Research Pilot API",
    description="MCP-based multi-step academic research assistant backend.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(research_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
