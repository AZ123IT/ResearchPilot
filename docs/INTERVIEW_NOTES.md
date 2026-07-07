# ResearchPilot Interview Notes

## One-Minute Pitch

ResearchPilot is a local AI research assistant that turns an academic question into an inspectable workflow. It searches papers, checks prior notes, verifies findings against abstracts, formats citations, saves reusable notes, and shows every LangGraph step and MCP tool call in a dashboard.

## Why This Is Not A Normal RAG Chatbot

Most RAG demos hide the retrieval and generation process behind one chat response. ResearchPilot exposes the workflow: search, detail lookup, evidence verification, citation formatting, memory, fallback behavior, and confidence labels are all visible.

## Why MCP Server Matters

The MCP server packages research capabilities behind a protocol boundary. The backend can call tools directly for tests, call a fresh MCP stdio server per request, or reuse a persistent MCP session. That makes the tool layer portable and easier to reason about than route-handler-only logic.

## Why LangGraph Is Used

LangGraph makes the control flow explicit. Each node has a clear responsibility, and the final response can show exactly what happened. This is useful for debugging, evaluation, screenshots, and interview explanation.

## Persistent MCP Session

Persistent MCP mode avoids starting a new server process for every tool call. The backend owns a background event loop, starts one MCP stdio session, queues tool calls onto it, and shuts it down cleanly on FastAPI lifespan shutdown. If startup fails, local fallback can keep the workflow running.

## Fallback And Cache

Search begins with arXiv in normal mode. If arXiv fails or returns too few papers, Semantic Scholar can fill gaps. Successful results are cached briefly. Demo mode uses local fixture papers for a stable presentation and labels them honestly as `demo`.

## Evidence-First Verification

The system does not promote unsupported generated claims to facts. It checks finding text against paper abstracts, attaches evidence snippets, and surfaces low-confidence claims. This reduces silent hallucination in the final review.

## Tests Written

The test suite covers:

- Citation formatting.
- Evidence verification.
- MCP search, detail, citation, and note tools.
- Semantic Scholar response normalization.
- Demo mode and cache fallback.
- MCP client mode selection and persistent fallback.
- Graph routing and API response shape.
- README/script reproducibility references.
- Demo fixture required fields.

## Limitations

- Uses abstracts, not full paper PDFs.
- Keyword overlap is a lightweight verification heuristic, not a complete factuality model.
- Supabase schema is pgvector-ready, but embeddings are not generated yet.
- Demo papers are fixture data for stable local presentation, not live search results.
- No deployment, auth, CI/CD, or GitHub remote setup is included in this local release candidate.

## Future Improvements

- Full PDF ingestion with section-level evidence.
- pgvector similarity search over generated embeddings.
- Streaming workflow events.
- Better ranking across arXiv and Semantic Scholar.
- Production auth and deployment once the local demo is stable.
