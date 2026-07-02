import type { Citation, EvidenceItem, Paper } from "@/lib/types";

interface SourcesTableProps {
  papers: Paper[];
  evidenceItems: EvidenceItem[];
  citations: Citation[];
}

export function SourcesTable({ papers, evidenceItems, citations }: SourcesTableProps) {
  const citationByPaper = new Map(citations.map((citation) => [citation.paper_id, citation]));
  const evidenceByPaper = new Map(evidenceItems.map((evidence) => [evidence.paper_id, evidence]));

  return (
    <section className="panel-surface rounded-lg p-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="micro-label text-slate-500">Evidence base</p>
          <h2 className="mt-1 text-2xl font-semibold">Sources and citations</h2>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{papers.length} papers</span>
      </div>

      {papers.length === 0 ? (
        <p className="mt-4 rounded-md border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
          Sources, evidence labels, and formatted citations will appear after a run.
        </p>
      ) : (
        <>
        <div className="mt-4 grid gap-3 md:hidden">
          {papers.map((paper) => {
            const evidence = evidenceByPaper.get(paper.paper_id);
            const citation = citationByPaper.get(paper.paper_id);

            return (
              <article className="rounded-md border border-slate-200 bg-white p-3" key={paper.paper_id}>
                <div className="flex flex-wrap items-center gap-2">
                  <span className={sourceClass(paper.source)}>{paper.source}</span>
                  {evidence?.confidence ? <span className={confidenceClass(evidence.confidence)}>{evidence.confidence}</span> : null}
                </div>
                <a className="mt-2 block text-sm font-semibold leading-5 text-slate-950 hover:text-cyan-800" href={paper.url} rel="noreferrer" target="_blank">
                  {paper.title}
                </a>
                <p className="mt-1 line-clamp-3 text-xs leading-5 text-slate-600">{paper.abstract}</p>
                {citation ? <p className="mt-3 border-l-2 border-slate-200 pl-3 text-xs leading-5 text-slate-600">{citation.citation_text}</p> : null}
              </article>
            );
          })}
        </div>

        <div className="mt-4 hidden overflow-x-auto md:block">
          <table className="min-w-[760px] border-separate border-spacing-0 text-left text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-[0.12em] text-slate-500">
                <th className="border-b border-slate-200 pb-2 pr-4 font-semibold">Paper</th>
                <th className="border-b border-slate-200 pb-2 pr-4 font-semibold">Source</th>
                <th className="border-b border-slate-200 pb-2 pr-4 font-semibold">Evidence</th>
                <th className="border-b border-slate-200 pb-2 font-semibold">Citation</th>
              </tr>
            </thead>
            <tbody>
              {papers.map((paper) => {
                const evidence = evidenceByPaper.get(paper.paper_id);
                const citation = citationByPaper.get(paper.paper_id);

                return (
                  <tr className="align-top" key={paper.paper_id}>
                    <td className="border-b border-slate-100 py-4 pr-4">
                      <a className="font-semibold leading-5 text-slate-950 hover:text-cyan-800" href={paper.url} rel="noreferrer" target="_blank">
                        {paper.title}
                      </a>
                      <p className="mt-1 line-clamp-2 max-w-xl text-xs leading-5 text-slate-600">{paper.abstract}</p>
                    </td>
                    <td className="border-b border-slate-100 py-4 pr-4">
                      <span className={sourceClass(paper.source)}>{paper.source}</span>
                      <p className="mt-2 text-xs text-slate-500">{paper.published_date || "date unavailable"}</p>
                      <p className="text-xs text-slate-500">{paper.citation_count ?? "n/a"} citations</p>
                    </td>
                    <td className="border-b border-slate-100 py-4 pr-4">
                      {evidence?.confidence ? <span className={confidenceClass(evidence.confidence)}>{evidence.confidence}</span> : <span className="text-xs text-slate-500">not linked</span>}
                    </td>
                    <td className="border-b border-slate-100 py-4">
                      {citation ? (
                        <p className="line-clamp-3 max-w-md text-xs leading-5 text-slate-600">{citation.citation_text}</p>
                      ) : (
                        <span className="text-xs text-slate-500">not generated</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        </>
      )}
    </section>
  );
}

function sourceClass(source: string) {
  if (source === "demo") return "rounded-full bg-amber-50 px-2 py-1 text-xs font-semibold uppercase text-amber-800";
  if (source === "semantic_scholar") return "rounded-full bg-blue-50 px-2 py-1 text-xs font-semibold uppercase text-blue-800";
  return "rounded-full bg-cyan-50 px-2 py-1 text-xs font-semibold uppercase text-cyan-800";
}

function confidenceClass(confidence: string) {
  if (confidence === "high") return "rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700";
  if (confidence === "medium") return "rounded-full bg-cyan-50 px-2 py-1 text-xs font-semibold text-cyan-800";
  return "rounded-full bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-800";
}
