# ResearchPilot Stage 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade ResearchPilot into a stronger local portfolio demo with credible MCP protocol support, richer backend logs, and a usable research dashboard.

**Architecture:** Keep the existing monorepo and LangGraph workflow. Add a tool-client adapter boundary with direct local mode for tests/dev and stdio MCP mode for protocol calls. Extend response schemas backward-compatibly, then make the Next.js `/research` page a client-side dashboard that renders the structured backend response.

**Tech Stack:** Python, FastAPI, LangGraph, official MCP Python SDK, pytest, Next.js App Router, React, TypeScript, Tailwind CSS.

---

### Task 1: Backend Contract Tests

**Files:**
- Modify: `backend/tests/test_graph_routing.py`
- Modify: `backend/tests/test_research_api.py`
- Create: `backend/tests/test_mcp_client_adapter.py`

- [x] Add tests that require enhanced `ToolCallLog` fields: `step_name`, `started_at`, `finished_at`, `duration_ms`, `error_message`, and `fallback_used`.
- [x] Add API response assertions for `evidence_items` and frontend-compatible literature review findings.
- [x] Add local adapter tests that call at least one tool through `LocalToolClient`.
- [x] Run pytest and confirm failures before production code changes.

### Task 2: MCP Adapter and Logging

**Files:**
- Modify: `backend/app/mcp_client/client.py`
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/agent/nodes.py`
- Modify: `backend/app/agent/graph.py`
- Modify: `backend/app/models/schemas.py`

- [x] Implement `ResearchToolClient`, `LocalToolClient`, and `MCPToolClient`.
- [x] Route graph tool calls through the adapter instead of direct imports.
- [x] Record timing, fallback, status, sanitized inputs, output previews, and error messages.
- [x] Include `evidence_items` in `ResearchResponse`.

### Task 3: Frontend Dashboard

**Files:**
- Modify: `frontend/app/research/page.tsx`
- Modify: `frontend/components/*.tsx`
- Modify: `frontend/lib/types.ts`
- Modify: `frontend/lib/api.ts`
- Modify: `frontend/app/globals.css`

- [x] Make `/research` a client dashboard with form state and validation.
- [x] Render timeline, tool calls, papers, citations, warnings, and low-confidence claims.
- [x] Keep TypeScript types aligned with backend response.

### Task 4: Docs and Verification

**Files:**
- Modify: `.env.example`
- Modify: `README.md`

- [x] Document MCP server stdio mode, local fallback mode, backend, frontend, and tests.
- [x] Run `.venv/bin/python -m pytest -q`.
- [x] Run `npm run typecheck`.
- [x] Smoke-test `GET /health`, `POST /api/research/run`, and `GET /research`.
