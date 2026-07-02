export type CitationStyle = "IEEE" | "APA" | "BibTeX";

export interface ResearchRequest {
  question: string;
  max_results: number;
  citation_style: CitationStyle;
}

export interface Paper {
  paper_id: string;
  title: string;
  authors: string[];
  abstract: string;
  published_date: string;
  source: string;
  url: string;
  citation_count: number | null;
}

export interface AgentStep {
  step_name: string;
  status: "success" | "warning" | "error";
  tool_name: string | null;
  summary: string;
  input: Record<string, unknown>;
  output_preview: Record<string, unknown>;
  duration_ms: number | null;
  fallback_used: boolean;
}

export interface ToolCallLog {
  step_name: string;
  tool_name: string;
  status: "success" | "warning" | "error";
  input: Record<string, unknown>;
  output_preview: Record<string, unknown>;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number;
  error_message: string | null;
  fallback_used: boolean;
  error: string | null;
}

export interface Finding {
  text: string;
  confidence: "high" | "medium" | "low";
  evidence_paper_title: string | null;
  evidence_snippet: string | null;
}

export interface EvidenceItem {
  claim: string;
  paper_id: string;
  paper_title: string;
  abstract_snippet: string;
  confidence: "high" | "medium" | "low" | null;
}

export interface ResearchNote {
  note_id: string;
  paper_id: string | null;
  title: string | null;
  content_preview: string;
  tag: string | null;
  source: string | null;
  url: string | null;
  score: number;
  storage: string;
  created_at: string | null;
}

export interface LiteratureReview {
  summary: string;
  key_findings: string[];
  findings: Finding[];
  reused_notes: ResearchNote[];
  methods: string[];
  limitations: string[];
  low_confidence_claims: string[];
}

export interface Citation {
  paper_id: string;
  style: CitationStyle;
  citation_text: string;
}

export interface ResearchResponse {
  question: string;
  steps: AgentStep[];
  tool_call_logs: ToolCallLog[];
  papers: Paper[];
  evidence_items: EvidenceItem[];
  prior_notes: ResearchNote[];
  reused_notes: ResearchNote[];
  search_source_summary: Record<string, unknown>;
  fallback_summary: string[];
  memory_storage: string | null;
  cache_used: boolean;
  literature_review: LiteratureReview;
  citations: Citation[];
  warnings: string[];
}
