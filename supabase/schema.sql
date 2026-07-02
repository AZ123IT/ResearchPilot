create extension if not exists vector;
create extension if not exists pgcrypto;

create table if not exists research_notes (
  id uuid primary key default gen_random_uuid(),
  paper_id text,
  title text,
  content text not null,
  tag text,
  source text,
  url text,
  embedding vector(1536),
  created_at timestamptz not null default now()
);

create index if not exists research_notes_tag_idx on research_notes(tag);
create index if not exists research_notes_paper_id_idx on research_notes(paper_id);
create index if not exists research_notes_created_at_idx on research_notes(created_at desc);

-- Future pgvector similarity index, enable after embeddings are populated:
-- create index research_notes_embedding_hnsw_idx
--   on research_notes using hnsw (embedding vector_cosine_ops);
