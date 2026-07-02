import { FormEvent, useState } from "react";

import type { CitationStyle, ResearchRequest } from "@/lib/types";

interface ResearchFormProps {
  defaultValue: ResearchRequest;
  isLoading: boolean;
  onSubmit: (request: ResearchRequest) => Promise<void> | void;
}

export function ResearchForm({ defaultValue, isLoading, onSubmit }: ResearchFormProps) {
  const [question, setQuestion] = useState(defaultValue.question);
  const [maxResults, setMaxResults] = useState(defaultValue.max_results);
  const [citationStyle, setCitationStyle] = useState<CitationStyle>(defaultValue.citation_style);
  const [validationError, setValidationError] = useState<string | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      setValidationError("Enter a research question.");
      return;
    }
    if (maxResults < 1 || maxResults > 10) {
      setValidationError("Max results must be between 1 and 10.");
      return;
    }
    setValidationError(null);
    void onSubmit({
      question: trimmed,
      max_results: maxResults,
      citation_style: citationStyle,
    });
  }

  return (
    <form className="panel-surface grid gap-3 rounded-lg p-3 sm:p-4" onSubmit={handleSubmit}>
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_260px]">
        <div className="grid gap-2">
          <label className="grid gap-2 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500" htmlFor="question">
            Question
            <textarea
              className="min-h-20 resize-y rounded-md border border-slate-200 bg-white p-3 text-sm leading-6 outline-none transition focus:border-cyan-700 focus:ring-2 focus:ring-cyan-100"
              id="question"
              name="question"
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="What are recent methods for improving RAG faithfulness?"
              value={question}
            />
          </label>
        </div>

        <div className="grid gap-2 content-start">
          <div className="grid grid-cols-2 gap-2">
            <label className="grid gap-1.5 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500" htmlFor="max_results">
              Results
              <input
                className="rounded-md border border-slate-200 bg-white p-2 text-sm outline-none transition focus:border-cyan-700 focus:ring-2 focus:ring-cyan-100"
                id="max_results"
                max={10}
                min={1}
                name="max_results"
                onChange={(event) => setMaxResults(Number(event.target.value))}
                type="number"
                value={maxResults}
              />
            </label>
            <label className="grid gap-1.5 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500" htmlFor="citation_style">
              Style
              <select
                className="rounded-md border border-slate-200 bg-white p-2 text-sm outline-none transition focus:border-cyan-700 focus:ring-2 focus:ring-cyan-100"
                id="citation_style"
                name="citation_style"
                onChange={(event) => setCitationStyle(event.target.value as CitationStyle)}
                value={citationStyle}
              >
                <option value="IEEE">IEEE</option>
                <option value="APA">APA</option>
                <option value="BibTeX">BibTeX</option>
              </select>
            </label>
          </div>

          {validationError ? <p className="border-l-4 border-red-500 bg-red-50 px-3 py-2 text-sm text-red-700">{validationError}</p> : null}

          <button
            className="rounded-md bg-cyan-800 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-cyan-900 disabled:cursor-not-allowed disabled:bg-slate-400"
            disabled={isLoading}
            type="submit"
          >
            {isLoading ? "Running..." : "Run workflow"}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 border-t border-slate-100 pt-3">
        {[
          "What are recent methods for improving RAG faithfulness?",
          "How do multi-agent systems use tool calling for research automation?",
          "What are common evaluation metrics for retrieval augmented generation?",
        ].map((sample) => (
          <button
            className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-left text-xs leading-5 text-slate-600 transition hover:border-cyan-500 hover:bg-cyan-50"
            key={sample}
            onClick={() => setQuestion(sample)}
            type="button"
          >
            {sample}
          </button>
        ))}
      </div>
    </form>
  );
}
