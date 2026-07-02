import type { Citation } from "@/lib/types";

interface CitationsPanelProps {
  citations: Citation[];
}

export function CitationsPanel({ citations }: CitationsPanelProps) {
  return (
    <section className="panel-surface rounded-lg p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="micro-label text-slate-500">Formatted output</p>
          <h2 className="mt-1 text-2xl font-semibold">Bibliography</h2>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{citations.length} generated</span>
      </div>

      {citations.length === 0 ? (
        <p className="mt-4 rounded-md border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">Formatted IEEE, APA, or BibTeX citations will appear after a workflow run.</p>
      ) : (
        <div className="mt-4 grid gap-0 divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
          {citations.map((citation) => (
            <article className="p-3" key={`${citation.paper_id}-${citation.style}`}>
              <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
                <span className="font-semibold uppercase tracking-[0.16em] text-slate-500">{citation.style}</span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-600">{citation.paper_id}</span>
              </div>
              {citation.style === "BibTeX" ? (
                <pre className="overflow-auto rounded-md bg-slate-950 p-3 text-xs leading-5 text-slate-100">{citation.citation_text}</pre>
              ) : (
                <p className="text-sm leading-6 text-slate-700">{citation.citation_text}</p>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
