# Research Pilot Architecture

Research Pilot is a local academic research workflow dashboard. It is built to make an AI research assistant inspectable: each step, tool call, fallback path, warning, citation, and evidence confidence label is returned as structured data.

## System Overview

```text
Next.js dashboard (/research)
  -> FastAPI POST /api/research/run
  -> LangGraph research workflow
  -> ResearchToolClient adapter
  -> Local Python tools or MCP stdio server
  -> arXiv, Semantic Scholar, demo fixtures, note memory
```

The frontend is intentionally a workflow dashboard, not a chat UI. The backend owns orchestration and returns a `ResearchResponse` that includes papers, evidence items, citations, prior notes, warnings, fallback summaries, cache state, and tool logs.

## MCP Server Tools

The MCP server in `mcp_server/server.py` exposes five tools:

- `search_papers`: searches demo fixtures, arXiv, Semantic Scholar, or cache-backed fallback paths.
- `fetch_paper_detail`: fetches arXiv details, demo fixture details, or returns a warning for unsupported detail sources.
- `format_citation`: formats IEEE, APA, or BibTeX citations.
- `save_to_notes`: saves notes to Supabase when configured, otherwise in-memory storage.
- `search_notes`: searches Supabase notes when configured, otherwise in-memory notes.

## LangGraph Workflow

The graph in `backend/app/agent/graph.py` runs this sequence:

1. `plan_research_task`
2. `search_notes`
3. `search_papers`
4. `fetch_paper_details`
5. `extract_summary`
6. `verify_evidence`
7. `format_citations`
8. `save_notes`
9. `generate_final_review`

This structure makes workflow behavior visible, auditable, and easier to evaluate in the dashboard timeline.

## Tool Client Modes

The backend uses `ResearchToolClient` to keep orchestration separate from tool execution.

- `local`: calls Python tool functions directly. This is the default for deterministic local development and tests.
- `mcp_single`: starts an MCP stdio server for each tool call.
- `mcp_persistent`: starts one MCP stdio server and reuses a `ClientSession` from a background event loop.

If MCP mode fails and fallback is enabled, the backend records fallback metadata and uses the local tool implementation.

## Search Fallback

Paper search supports four practical paths:

- `demo`: local fixture papers from `mcp_server/data/demo_papers.json`, clearly labeled as demo data.
- `arxiv`: primary live academic metadata source.
- `semantic_scholar`: fallback source for public metadata and citation counts.
- `cache`: short-lived in-memory fallback when a previously successful search can be reused after an external failure.

External API behavior is mocked in tests.

## Long-Term Memory

Research notes can be stored in Supabase using the schema in `supabase/schema.sql`. The schema is pgvector-ready with an `embedding vector(1536)` column, but the current implementation does not generate embeddings yet.

When Supabase credentials are missing or Supabase fails, the note tools use in-memory fallback and return readable warnings. This keeps the local demo runnable without cloud credentials.

## Evidence Verification

Findings are checked against paper abstracts with keyword overlap. Supported findings receive evidence snippets and confidence labels. Weak or unsupported claims remain visible as low-confidence claims instead of being silently treated as facts.

This is not a replacement for full-paper review. It is a lightweight guardrail for checking whether generated claims are grounded in the retrieved abstracts.

## Frontend Dashboard

The dashboard in `frontend/app/research/page.tsx` renders:

- Research form with demo prompts.
- Search and memory reliability panels.
- Literature review with evidence snippets and confidence labels.
- Paper result cards with source labels.
- Citation panel.
- LangGraph timeline.
- MCP tool-call log with inputs and output previews.

The UI is Tailwind-only and is designed to make workflow state, source evidence, and fallback behavior easy to scan during a research run.
