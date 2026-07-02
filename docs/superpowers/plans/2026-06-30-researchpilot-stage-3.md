# ResearchPilot Stage 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve ResearchPilot engineering depth with persistent MCP sessions, real Semantic Scholar fallback, pgvector-ready note memory, search cache fallback, response extensions, and documentation.

**Architecture:** Preserve the Stage 2 monorepo and adapter boundary. Add a persistent MCP client that owns a reusable stdio session on a background event loop, upgrade paper search to arXiv plus Semantic Scholar with cache fallback, make notes richer and pgvector-ready, add a notes-search graph node, and surface new metadata in the dashboard.

**Tech Stack:** Python, FastAPI, LangGraph, official MCP Python SDK, Supabase Python, httpx, pytest, Next.js App Router, React, TypeScript, Tailwind CSS.

---

### Task 1: RED Tests For Stage 3

**Files:**
- Modify: `backend/tests/test_mcp_client_adapter.py`
- Modify: `backend/tests/test_graph_routing.py`
- Modify: `backend/tests/test_research_api.py`
- Create: `mcp_server/tests/test_semantic_scholar_client.py`
- Modify: `mcp_server/tests/test_search_papers_tool.py`
- Modify: `mcp_server/tests/test_notes_tool.py`

- [x] Add factory tests for `local`, `mcp_single`, and `mcp_persistent`.
- [x] Add persistent startup failure fallback test.
- [x] Add workflow/API assertions for `prior_notes`, `fallback_summary`, `memory_storage`, and `cache_used`.
- [x] Add mocked Semantic Scholar normalization and fallback tests.
- [x] Add richer note metadata tests while preserving old input shape.
- [x] Add cache hit, cache fallback, and expired cache tests.
- [x] Run pytest and confirm failures before implementation.

### Task 2: Persistent MCP Adapter

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/mcp_client/client.py`
- Modify: `backend/app/main.py`

- [x] Support `RESEARCH_TOOL_CLIENT_MODE=local|mcp_single|mcp_persistent` with backward-compatible Stage 2 env aliases.
- [x] Add `PersistentMCPToolClient` with a reusable stdio `ClientSession` on a background event loop.
- [x] Add clean shutdown helper for the singleton persistent client.
- [x] Preserve fallback-to-local behavior and `_meta.fallback_used`.

### Task 3: Search, Cache, Semantic Scholar

**Files:**
- Modify: `mcp_server/clients/semantic_scholar_client.py`
- Modify: `mcp_server/tools/search_papers.py`

- [x] Implement Semantic Scholar Graph API search with normalized paper schema.
- [x] Add in-memory TTL cache keyed by query/source/max_results.
- [x] Implement `auto` merge, fallback, dedupe, cache fallback, and response summary metadata.

### Task 4: Notes And Graph Memory

**Files:**
- Modify: `mcp_server/models/schemas.py`
- Modify: `mcp_server/tools/notes.py`
- Create: `backend/app/services/note_service.py`
- Modify: `backend/app/agent/state.py`
- Modify: `backend/app/agent/graph.py`
- Modify: `backend/app/agent/nodes.py`
- Modify: `supabase/schema.sql`

- [x] Add richer note schema and Supabase/pgvector-ready SQL.
- [x] Add `search_notes_node` before external paper search.
- [x] Add `prior_notes`, `reused_notes`, `search_source_summary`, `fallback_summary`, `memory_storage`, and `cache_used` to response.
- [x] Ensure note search failures do not block the workflow.

### Task 5: Frontend And Docs

**Files:**
- Modify: `frontend/lib/types.ts`
- Modify: `frontend/components/StatusPanels.tsx`
- Modify: `frontend/app/research/page.tsx`
- Modify: `README.md`
- Modify: `.env.example`

- [x] Add Stage 3 response fields to TypeScript types.
- [x] Render prior notes, search source summary, fallback summary, memory storage, and cache used.
- [x] Update README with Stage 3 operations and limitations.

### Task 6: Verification

**Files:**
- No production edits.

- [x] Run `.venv/bin/python -m pytest -q`.
- [x] Run `npm run typecheck`.
- [x] Smoke-test MCP stdio tools if changed.
- [x] Smoke-test `GET /health`, `POST /api/research/run`, and `GET /research`.
