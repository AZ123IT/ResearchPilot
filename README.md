# ResearchPilot

ResearchPilot is a local AI agent workflow for academic literature review. It turns a research question into an inspectable multi-step run: planning, memory lookup, paper search, metadata fetch, finding extraction, evidence verification, citation formatting, note saving, and a structured dashboard output.

The project is designed as a portfolio-friendly example of an evidence-first research agent, not a generic RAG chat box.

## Highlights

- **Multi-step agent workflow:** LangGraph coordinates planning, paper search, detail lookup, summary extraction, evidence checking, citation formatting, and note saving.
- **MCP-style tool boundary:** research tools are packaged behind a local MCP server interface, with direct local, single-call MCP, and persistent MCP client modes.
- **Real academic search:** arXiv is used by default, with optional Semantic Scholar fallback and short-lived in-memory cache.
- **LLM-assisted synthesis:** DeepSeek can extract candidate findings from retrieved abstracts when `DEEPSEEK_API_KEY` is configured.
- **Evidence-first output:** claims are linked to source papers, abstract snippets, confidence labels, warnings, and formatted citations.
- **Inspectable UI:** the Next.js dashboard shows the research strategy, claim audit, literature review, sources, bibliography, and tool-call timeline.

## Demo Screenshots

Example question:

```text
How do retrieval augmented generation systems evaluate faithfulness?
```

### Agent Workflow And Claim Audit

![ResearchPilot agent workflow and claim audit](docs/screenshots/1.png)

### Literature Review

![ResearchPilot literature review](docs/screenshots/2.png)

### Sources And Citations

![ResearchPilot sources and citations](docs/screenshots/3.png)

### Bibliography

![ResearchPilot bibliography](docs/screenshots/4.png)

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Pydantic, LangGraph
- **Agent tooling:** custom MCP-style research server and tool client adapters
- **Academic sources:** arXiv, optional Semantic Scholar
- **LLM provider:** DeepSeek Chat API
- **Memory:** in-memory fallback by default, optional Supabase/Postgres note storage
- **Testing:** pytest, Next.js TypeScript typecheck

## Architecture

```text
Next.js dashboard (/research)
  -> POST /api/research/run
FastAPI backend
  -> LangGraph StateGraph
      plan_research_task
      search_notes
      search_papers
      adaptive_search when evidence coverage is thin
      fetch_paper_details
      extract_summary
      verify_evidence
      format_citations
      save_notes
      generate_final_review
  -> ResearchToolClient adapter
      local
      mcp_single
      mcp_persistent
  -> Research MCP server
      search_papers
      fetch_paper_detail
      format_citation
      save_to_notes
      search_notes
  -> arXiv, optional Semantic Scholar, optional DeepSeek, optional Supabase
```

## Why This Is Not A Normal RAG Chatbot

Most RAG demos hide the retrieval and reasoning steps behind one chat response. ResearchPilot exposes the run as structured state:

- the planned research strategy,
- every tool call and duration,
- which papers were retrieved,
- which claims were supported or weak,
- which citations were generated,
- and which fallback paths were used.

This makes the system easier to debug, explain, and evaluate.

## Quick Start

Run these commands from the project root.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt -r mcp_server/requirements.txt
cd frontend
npm install
cd ..
cp .env.example .env
```

Edit `.env`:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
RESEARCHPILOT_DEMO_MODE=false
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Start the backend:

```bash
scripts/run_backend.sh
```

For a deterministic fixture-only presentation without external academic APIs:

```bash
RESEARCHPILOT_DEMO_MODE=true scripts/run_backend.sh
```

Start the frontend in a second terminal:

```bash
scripts/run_frontend.sh
```

Open:

```text
http://127.0.0.1:3000/research
```

Run all local checks:

```bash
scripts/test_all.sh
```

## Environment Variables

See `.env.example`.

| Variable | Required | Purpose |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | Optional | Enables LLM-based finding extraction. If absent, deterministic abstract extraction is used. |
| `DEEPSEEK_BASE_URL` | Optional | DeepSeek-compatible API base URL. |
| `DEEPSEEK_MODEL` | Optional | Chat model name, defaults to `deepseek-chat`. |
| `RESEARCHPILOT_DEMO_MODE` | Optional | Set `true` for local fixture papers; set `false` for real academic search. |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional | Improves Semantic Scholar rate limits. Public search can work without it. |
| `SUPABASE_URL` | Optional | Enables persistent note memory. |
| `SUPABASE_SERVICE_ROLE_KEY` | Optional | Enables persistent note memory writes. |
| `RESEARCH_TOOL_CLIENT_MODE` | Optional | `local`, `mcp_single`, or `mcp_persistent`. |
| `NEXT_PUBLIC_API_BASE_URL` | Optional | Frontend API base URL. |

Do not commit `.env`.

## MCP Tool Modes

The backend can call the research tools in three modes:

- `local`: direct Python function calls, best for local development and tests.
- `mcp_single`: starts an MCP stdio server per tool call.
- `mcp_persistent`: keeps one MCP stdio session alive for a run.

Example persistent mode:

```env
RESEARCH_TOOL_CLIENT_MODE=mcp_persistent
MCP_SERVER_COMMAND=.venv/bin/python
MCP_SERVER_ARGS=mcp_server/server.py
MCP_SERVER_CWD=/absolute/path/to/researchpilot
MCP_FALLBACK_TO_LOCAL=true
```

MCP stdio helper:

```bash
scripts/run_mcp_server.sh
```

## Testing

Run backend tests and frontend typecheck together:

```bash
scripts/test_all.sh
```

Backend only:

```bash
.venv/bin/python -m pytest -q
```

Frontend only:

```bash
cd frontend
npm run typecheck
```

## Current Limitations

- Evidence verification is abstract-level, not full-PDF section-level verification.
- arXiv keyword search can retrieve weakly related papers; the dashboard surfaces this through confidence labels and limitations instead of hiding it.
- Supabase memory is optional. Without credentials, notes use in-memory fallback.
- The pgvector schema is prepared for future embedding search, but this project does not yet generate embeddings.
- The app is built for local portfolio demonstration, not production authentication or multi-user deployment.

## Resume Summary

**ResearchPilot: MCP academic research assistant / AI agent workflow**

- Built a local full-stack AI research assistant with Next.js, FastAPI, LangGraph, Pydantic, and custom MCP-style tools.
- Implemented paper search, metadata lookup, finding extraction, evidence verification, citation formatting, memory reuse, and structured literature review generation.
- Designed an evidence-first dashboard with workflow trace, tool-call logs, claim audit, confidence labels, source papers, and IEEE/APA/BibTeX citations.
- Added demo mode, fallback handling, local memory fallback, arXiv/Semantic Scholar search orchestration, automated tests, and reproducible startup scripts.
