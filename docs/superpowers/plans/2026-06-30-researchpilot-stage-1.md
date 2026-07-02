# ResearchPilot Stage 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable Stage 1 MVP for ResearchPilot with MCP tools, a LangGraph backend workflow, tests, and a frontend skeleton.

**Architecture:** The MCP server exposes testable academic research tools and keeps external API access inside clients. The FastAPI backend invokes a LangGraph `StateGraph` that calls the tool layer, verifies findings against abstracts, formats citations, saves supported notes, and returns structured JSON. The frontend remains a minimal Next.js skeleton with shared response types for Stage 2 UI work.

**Tech Stack:** Python 3.11+, FastAPI, LangGraph, official MCP Python SDK, Pydantic, httpx, pytest, Supabase-ready Postgres/pgvector, Next.js, TypeScript, Tailwind CSS.

---

### Task 1: Test Contract

**Files:**
- Create: `backend/tests/test_citation_service.py`
- Create: `backend/tests/test_verification_service.py`
- Create: `backend/tests/test_graph_routing.py`
- Create: `backend/tests/test_research_api.py`
- Create: `mcp_server/tests/test_search_papers_tool.py`
- Create: `mcp_server/tests/test_fetch_paper_detail_tool.py`
- Create: `mcp_server/tests/test_format_citation_tool.py`
- Create: `mcp_server/tests/test_notes_tool.py`

- [x] Write failing tests for citation formatting, verification, MCP tools, graph routing, and API output.
- [x] Run `python3 -m pytest backend/tests mcp_server/tests -q`.
- [x] Confirm RED state fails because implementation modules are missing.

### Task 2: Backend and MCP MVP

**Files:**
- Create: `backend/app/**`
- Create: `mcp_server/**`
- Create: `pytest.ini`

- [x] Add Pydantic schemas, citation and verification services.
- [x] Add arXiv client, MCP tool functions, note memory fallback, and `FastMCP` server entrypoint.
- [x] Add LangGraph nodes and sequential graph edges from planning through final review.
- [x] Add FastAPI `/api/research/run`.
- [x] Run `.venv/bin/python -m pytest -q`.
- [x] Fix citation punctuation and rerun until GREEN.

### Task 3: Project Artifacts

**Files:**
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `supabase/schema.sql`
- Create: `README.md`
- Create: `frontend/**`

- [x] Add pgvector-ready notes schema and environment variable template.
- [x] Add README with architecture, setup, testing, resume highlights, and future work.
- [x] Add Next.js skeleton, API client, shared TypeScript types, and placeholder components.
