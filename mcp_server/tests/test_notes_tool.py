from tools.notes import clear_memory_notes, save_to_notes_tool, search_notes_tool


def test_notes_fall_back_to_memory_storage_without_supabase(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    clear_memory_notes()

    saved = save_to_notes_tool("Useful note about RAG faithfulness", "p1", "rag")
    matches = search_notes_tool("faithfulness", 5)

    assert saved["storage"] == "memory"
    assert saved["note"]["content"] == "Useful note about RAG faithfulness"
    assert len(matches["notes"]) == 1
    assert matches["notes"][0]["paper_id"] == "p1"


def test_notes_tool_supports_richer_metadata(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    clear_memory_notes()

    saved = save_to_notes_tool(
        "Detailed note about RAG faithfulness",
        paper_id="p2",
        tag="rag",
        title="Faithful RAG",
        source="arxiv",
        url="https://arxiv.org/abs/p2",
    )
    matches = search_notes_tool("faithfulness", 5)

    assert saved["note"]["note_id"]
    assert saved["note"]["title"] == "Faithful RAG"
    assert matches["notes"][0]["content_preview"] == "Detailed note about RAG faithfulness"
    assert matches["notes"][0]["storage"] == "memory"
    assert matches["notes"][0]["score"] > 0


def test_memory_note_search_deduplicates_repeated_saved_notes(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    clear_memory_notes()

    for _ in range(2):
        save_to_notes_tool(
            "Tool-using agents expose planning and tool-call logs for research automation.",
            paper_id="demo-tool-agents-2025",
            tag="auto-literature-review",
            title="Tool-Using Agents for Research Automation",
            source="demo",
            url="https://example.local/researchpilot/demo-tool-agents-2025",
        )

    matches = search_notes_tool("tool calling research automation", 5)

    assert len(matches["notes"]) == 1
    assert matches["notes"][0]["title"] == "Tool-Using Agents for Research Automation"
