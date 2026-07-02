# ResearchPilot Stage 4 Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn ResearchPilot from a working MVP into a polished, reliable local demo suitable for screenshots, interviews, resume discussion, and later GitHub upload.

**Architecture:** Keep the Stage 3 graph and tool-client boundary intact. Add demo mode inside the MCP search tool so LangGraph, adapter calls, tool logs, citations, note saving, and frontend rendering still exercise the real workflow. Improve deterministic backend output and warnings, then polish the existing Tailwind dashboard without adding a UI library.

**Tech Stack:** Python, FastAPI, LangGraph, MCP Python SDK, pytest, Next.js App Router, React, TypeScript, Tailwind CSS, shell scripts.

---

### Task 1: Demo Mode Tests And Data

**Files:**
- Create: `mcp_server/data/demo_papers.json`
- Create: `mcp_server/data/__init__.py`
- Modify: `mcp_server/tools/search_papers.py`
- Modify: `mcp_server/tests/test_search_papers_tool.py`
- Modify: `backend/tests/test_research_api.py`

- [x] Add failing MCP test that `RESEARCHPILOT_DEMO_MODE=true` returns stable `source="demo"` papers with a demo warning and no external clients.
- [x] Add failing API test that demo mode completes the full workflow and includes cache/fallback/source summary fields.
- [x] Add a compact local demo paper fixture covering RAG faithfulness, tool-using agents, and academic research automation.
- [x] Implement demo-mode branch inside `search_papers_tool` before external search.
- [x] Keep demo data clearly labeled as `demo` and do not pretend it is arXiv or Semantic Scholar.

### Task 2: Backend Output Quality And Warnings

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/agent/nodes.py`
- Modify: `backend/app/agent/prompts.py`
- Modify: `backend/tests/test_graph_routing.py`
- Modify: `backend/tests/test_research_api.py`

- [x] Add failing test that deterministic fallback review includes professional methods, limitations, supported findings, and low-confidence claims when evidence is weak.
- [x] Add `demo_mode` setting and warning copy for missing DeepSeek key, demo mode, cache fallback, and fallback summaries.
- [x] Improve deterministic findings so they derive concise claims from titles/abstracts with source context rather than placeholder-sounding first sentences.
- [x] Improve final review summary, methods, and limitations for interview/demo readability.
- [x] Keep low-confidence behavior strict when abstract evidence is weak.

### Task 3: Frontend Dashboard Polish

**Files:**
- Modify: `frontend/app/research/page.tsx`
- Modify: `frontend/app/globals.css`
- Modify: `frontend/components/AgentTimeline.tsx`
- Modify: `frontend/components/ResearchForm.tsx`
- Modify: `frontend/components/StatusPanels.tsx`
- Modify: `frontend/components/LiteratureReview.tsx`
- Modify: `frontend/components/PaperCard.tsx`
- Modify: `frontend/components/CitationsPanel.tsx`
- Modify: `frontend/components/ToolCallLog.tsx`
- Modify: `frontend/lib/types.ts`

- [x] Add clearer labels for MCP tool calls, LangGraph steps, evidence confidence, memory storage, cache use, and fallback use.
- [x] Improve empty/loading states so screenshot mode looks intentional before and during a run.
- [x] Tighten responsive layouts for laptop, medium, and mobile widths.
- [x] Preserve Tailwind-only implementation and avoid heavy new UI dependencies.
- [x] Run `npm run typecheck` after UI changes.

### Task 4: Local Run Scripts And Docs

**Files:**
- Create: `scripts/run_backend.sh`
- Create: `scripts/run_frontend.sh`
- Create: `scripts/run_mcp_server.sh`
- Create: `scripts/test_all.sh`
- Modify: `.env.example`
- Modify: `README.md`
- Create/Modify: `backend/tests/test_readme_commands.py`

- [x] Add safe scripts that use `.venv`, set local `PYTHONPATH`, and contain no secrets.
- [x] Document demo mode, scripts, and local run commands.
- [x] Add README interview explanation with pitch, MCP, LangGraph, tool calling, verification, fallbacks, testing, and future work.
- [x] Add five polished resume bullets without fake performance numbers.
- [x] Add a lightweight test that README-mentioned script paths exist.

### Task 5: Verification

**Files:**
- No production edits.

- [x] Run `.venv/bin/python -m pytest -q`.
- [x] Run `npm run typecheck` inside `frontend`.
- [x] Smoke-test `GET /health`.
- [x] Smoke-test `POST /api/research/run` with `RESEARCHPILOT_DEMO_MODE=true`.
- [x] Leave local servers in a usable state if possible and report URLs.
