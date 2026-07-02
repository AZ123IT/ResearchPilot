from tools.notes import save_to_notes_tool, search_notes_tool


class NoteService:
    """Backend-facing wrapper around the MCP note tool implementation."""

    def save_note(
        self,
        content: str,
        paper_id: str | None = None,
        tag: str | None = None,
        title: str | None = None,
        source: str | None = None,
        url: str | None = None,
    ) -> dict:
        return save_to_notes_tool(
            content=content,
            paper_id=paper_id,
            tag=tag,
            title=title,
            source=source,
            url=url,
        )

    def search_notes(self, query: str, top_k: int = 5) -> dict:
        return search_notes_tool(query=query, top_k=top_k)
