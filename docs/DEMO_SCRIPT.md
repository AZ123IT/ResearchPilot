# Research Pilot Demo Guide

## Start Backend In Demo Mode

From the project root:

```bash
RESEARCHPILOT_DEMO_MODE=true scripts/run_backend.sh
```

Backend URL:

```text
http://127.0.0.1:8000
```

## Start Frontend

In a second terminal from the project root:

```bash
scripts/run_frontend.sh
```

Dashboard URL:

```text
http://127.0.0.1:3000/research
```

## Recommended Demo Question

```text
What are recent methods for improving RAG faithfulness?
```

## What To Check

- The page is a workflow dashboard, not a chat app.
- The top metric row shows step count, MCP call count, and cache state.
- The left reliability panels show memory mode, demo source count, fallback summary, and warnings.
- The literature review separates findings, evidence snippets, methods, limitations, and reused notes.
- Evidence confidence labels show which findings are backed by abstract snippets.
- Paper cards label fixture data as `DEMO`.
- The citation panel shows generated IEEE, APA, or BibTeX citations.
- The right timeline shows each LangGraph step.
- The tool-call log shows MCP tool names, inputs, output previews, duration, warnings, and fallback labels.

## How To Explain Fallback Behavior

In normal mode, the search tool tries arXiv first, can fall back to Semantic Scholar, and can use short-lived cache results after an external failure. In demo mode, the workflow uses local fixture papers so the run is reproducible without relying on network availability. Demo mode is clearly labeled and does not pretend fixture data came from live external APIs.

## Optional API Smoke

```bash
curl -sS http://127.0.0.1:8000/health
```

```bash
curl -sS -X POST http://127.0.0.1:8000/api/research/run \
  -H 'Content-Type: application/json' \
  -d '{"question":"What are recent methods for improving RAG faithfulness?","max_results":2,"citation_style":"IEEE"}'
```
