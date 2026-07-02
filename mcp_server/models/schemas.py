from pydantic import BaseModel, Field


class Paper(BaseModel):
    paper_id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    published_date: str = ""
    source: str
    url: str
    citation_count: int | None = None


class Note(BaseModel):
    note_id: str
    content: str
    paper_id: str | None = None
    title: str | None = None
    tag: str | None = None
    source: str | None = None
    url: str | None = None
    created_at: str
