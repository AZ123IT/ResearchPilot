# ResearchPilot Stage 5 Release Candidate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare ResearchPilot as a final local release candidate before future GitHub upload and resume use.

**Architecture:** Preserve the Stage 4 backend, MCP, LangGraph, demo mode, and dashboard behavior. Make small audit-driven fixes, add release-candidate documentation, strengthen reproducibility tests, and rerun full local verification.

**Tech Stack:** Python, FastAPI, LangGraph, MCP Python SDK, pytest, Next.js, TypeScript, Tailwind CSS, shell scripts, Markdown docs.

---

### Task 1: Audit And Tests

**Files:**
- Modify: `backend/tests/test_readme_commands.py`

- [x] Inspect source, docs, scripts, tests, and frontend files while excluding generated dependency/build folders.
- [x] Add tests for Quick Start commands and Stage 5 docs.
- [x] Add test for `demo_papers.json` required fields.
- [x] Run targeted tests and confirm they fail before docs are added.

### Task 2: Safe Audit Fixes

**Files:**
- Modify: `mcp_server/tools/fetch_paper_detail.py`
- Modify: `README.md`

- [x] Replace stale Semantic Scholar detail warning copy.
- [x] Remove machine-specific commands from main README setup sections.
- [x] Update limitations wording so it reflects the current release candidate, not an older stage.

### Task 3: Release Candidate Documentation

**Files:**
- Create: `docs/ARCHITECTURE.md`
- Create: `docs/INTERVIEW_NOTES.md`
- Create: `docs/DEMO_SCRIPT.md`
- Modify: `README.md`

- [x] Add architecture documentation.
- [x] Add interview notes.
- [x] Add demo script.
- [x] Add README Quick Start near the top.
- [x] Keep GitHub upload and local Git initialization as optional user actions only.

### Task 4: Verification

**Files:**
- No production edits.

- [x] Run `.venv/bin/python -m pytest -q`.
- [x] Run `npm run typecheck` in `frontend`.
- [x] Run `./scripts/test_all.sh`.
- [x] Smoke-test `GET /health`.
- [x] Smoke-test `POST /api/research/run` with `RESEARCHPILOT_DEMO_MODE=true`.
- [x] Smoke-test `GET /research`.
