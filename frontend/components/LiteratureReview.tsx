import type { EvidenceItem, ResearchResponse } from "@/lib/types";

interface LiteratureReviewProps {
  response: ResearchResponse | null;
  isLoading: boolean;
}

export function LiteratureReview({ response, isLoading }: LiteratureReviewProps) {
  const review = response?.literature_review;
  const evidenceByClaim = new Map((response?.evidence_items ?? []).map((item) => [item.claim, item]));

  return (
    <section className="panel-surface rounded-lg p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="micro-label text-slate-500">Structured review</p>
          <h2 className="mt-1 text-3xl font-semibold">Literature review</h2>
        </div>
        {response ? <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">Generated</span> : null}
      </div>

      {!response && !isLoading ? (
        <div className="mt-6 rounded-md border border-dashed border-slate-300 bg-slate-50 p-6 text-sm leading-6 text-slate-600">
          Run a question to generate a review with evidence-linked findings, methods, limitations, and citations.
        </div>
      ) : null}

      {isLoading ? <div className="mt-6 animate-pulse rounded-md bg-slate-100 p-6 text-sm text-slate-500">Running search, memory lookup, citation formatting, and evidence checks...</div> : null}

      {review ? (
        <div className="mt-5 grid gap-6">
          <section className="rounded-lg border border-cyan-100 bg-cyan-50 px-4 py-4">
            <p className="micro-label text-cyan-800">Executive summary</p>
            <p className="mt-2 text-base leading-7 text-slate-800">{review.summary}</p>
          </section>

          <section>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h3 className="micro-label text-slate-500">Evidence-backed findings</h3>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{review.findings.length} claims</span>
            </div>
            {review.findings.length ? (
              <ol className="mt-3 grid gap-0 divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
                {review.findings.map((finding, index) => (
                  <FindingItem evidence={evidenceByClaim.get(finding.text)} finding={finding.text} index={index + 1} key={`${finding.text}-${index}`} />
                ))}
              </ol>
            ) : (
              <p className="mt-3 text-sm text-slate-500">No supported findings were generated.</p>
            )}
          </section>

          <div className="grid gap-4 lg:grid-cols-2">
            <ReviewList title="Methods">
              {review.methods.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ReviewList>
            <ReviewList title="Limitations">
              {review.limitations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ReviewList>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function FindingItem({ finding, evidence, index }: { finding: string; evidence?: EvidenceItem; index: number }) {
  return (
    <li className="grid gap-3 p-4 sm:grid-cols-[36px_1fr]">
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-950 text-sm font-semibold text-white">{index}</span>
      <div className="min-w-0">
        <p className="text-sm leading-6 text-slate-800">{finding}</p>
      {evidence ? (
        <div className="mt-3 text-xs leading-5 text-slate-600">
          <div className="flex flex-wrap items-center gap-2 border-l-2 border-cyan-600 pl-3">
            <span className="font-semibold text-slate-800">{evidence.paper_title}</span>
            {evidence.confidence ? <span className={confidenceClass(evidence.confidence)}>Evidence confidence: {evidence.confidence}</span> : null}
          </div>
          <p className="mt-2 pl-3">{evidence.abstract_snippet}</p>
        </div>
      ) : null}
      </div>
    </li>
  );
}

function confidenceClass(confidence: string) {
  if (confidence === "high") return "bg-emerald-50 px-2 py-0.5 font-semibold text-emerald-700";
  if (confidence === "medium") return "bg-cyan-50 px-2 py-0.5 font-semibold text-cyan-800";
  return "bg-amber-50 px-2 py-0.5 font-semibold text-amber-800";
}

function ReviewList({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="micro-label text-slate-500">{title}</h3>
      <ul className="mt-3 grid gap-2 text-sm leading-6 text-slate-700">{children}</ul>
    </section>
  );
}
