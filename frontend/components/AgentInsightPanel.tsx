import type { AdaptiveSearchReport, EvidenceCoverageItem, ResearchPlanStep, ResearchResponse } from "@/lib/types";

interface AgentInsightPanelProps {
  response: ResearchResponse | null;
  isLoading: boolean;
}

export function AgentInsightPanel({ response, isLoading }: AgentInsightPanelProps) {
  const plan = response?.research_plan ?? [];
  const coverage = response?.evidence_coverage ?? [];
  const adaptiveSearch = response?.adaptive_search ?? null;

  return (
    <section className="panel-surface rounded-lg p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="micro-label text-slate-500">Agent workflow</p>
          <h2 className="mt-1 text-2xl font-semibold">Research strategy and audit</h2>
        </div>
        {response ? <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-800">{adaptiveSearch?.search_rounds ?? 1} search round{adaptiveSearch?.search_rounds === 1 ? "" : "s"}</span> : null}
      </div>

      {!response && !isLoading ? (
        <div className="mt-5 rounded-md border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-500">No run yet.</div>
      ) : null}

      {isLoading ? (
        <div className="mt-5 grid gap-3 md:grid-cols-[1.3fr_0.7fr]">
          <div className="h-32 animate-pulse rounded-lg bg-slate-100" />
          <div className="h-32 animate-pulse rounded-lg bg-slate-100" />
        </div>
      ) : null}

      {response ? (
        <div className="mt-5 grid gap-4">
          <PlanStrip plan={plan} />

          <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
            <AdaptiveSearchCard adaptiveSearch={adaptiveSearch} />
            <CoverageAudit coverage={coverage} />
          </div>
        </div>
      ) : null}
    </section>
  );
}

function PlanStrip({ plan }: { plan: ResearchPlanStep[] }) {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between gap-3">
        <h3 className="micro-label text-slate-500">Research plan</h3>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{plan.length} steps</span>
      </div>
      <ol className="flex flex-wrap gap-2">
        {plan.map((step, index) => (
          <li className="flex min-w-0 items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2" key={step.step_id} title={step.rationale}>
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-950 text-xs font-semibold text-white">{index + 1}</span>
            <span className="text-sm font-semibold text-slate-950">{step.title}</span>
            <span className={planStatusClass(step.status)}>{step.status}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}

function AdaptiveSearchCard({ adaptiveSearch }: { adaptiveSearch: AdaptiveSearchReport | null }) {
  if (!adaptiveSearch) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h3 className="micro-label text-slate-500">Adaptive search</h3>
        <p className="mt-3 text-sm text-slate-500">No run yet.</p>
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="micro-label text-slate-500">Adaptive search</h3>
        <span className={adaptiveSearch.triggered ? "rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-800" : "rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600"}>
          {adaptiveSearch.triggered ? `+${adaptiveSearch.added_papers} papers` : "Not needed"}
        </span>
      </div>
      <dl className="mt-3 grid gap-3 text-sm leading-6">
        <div>
          <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">Initial query</dt>
          <dd className="mt-1 text-slate-800">{adaptiveSearch.initial_query}</dd>
        </div>
        {adaptiveSearch.triggered ? (
          <div>
            <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">Refined query</dt>
            <dd className="mt-1 text-slate-800">{adaptiveSearch.refined_query}</dd>
          </div>
        ) : null}
        {adaptiveSearch.reason ? <p className="rounded-md bg-cyan-50 px-3 py-2 text-xs leading-5 text-cyan-900">{adaptiveSearch.reason}</p> : null}
      </dl>
    </section>
  );
}

function CoverageAudit({ coverage }: { coverage: EvidenceCoverageItem[] }) {
  const supportedCount = coverage.filter((item) => item.support_status === "supported").length;
  const visibleCoverage = coverage.slice(0, 3);
  const hiddenCount = coverage.length - visibleCoverage.length;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="micro-label text-slate-500">Claim audit</h3>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{supportedCount}/{coverage.length} supported</span>
      </div>
      {coverage.length ? (
        <ul className="mt-3 grid gap-2">
          {visibleCoverage.map((item, index) => (
            <li className="rounded-md border border-slate-100 bg-slate-50 px-3 py-3" key={`${item.claim}-${index}`}>
              <div className="flex flex-wrap items-center gap-2">
                <span className={coverageClass(item.support_status)}>{item.support_status}</span>
                {item.confidence ? <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-semibold text-slate-600">{item.confidence}</span> : null}
                <span className="text-[11px] font-semibold text-slate-500">{item.source_count} source{item.source_count === 1 ? "" : "s"}</span>
              </div>
              <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-700">{item.claim}</p>
              {item.paper_titles.length ? <p className="mt-2 truncate text-[11px] font-semibold text-slate-500">{item.paper_titles.join(", ")}</p> : null}
            </li>
          ))}
          {hiddenCount > 0 ? <li className="px-1 pt-1 text-xs font-semibold text-slate-500">{hiddenCount} more audited claims in the review below.</li> : null}
        </ul>
      ) : (
        <p className="mt-3 rounded-md border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">No claims audited.</p>
      )}
    </section>
  );
}

function planStatusClass(status: ResearchPlanStep["status"]) {
  if (status === "completed") return "rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700";
  if (status === "skipped") return "rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-800";
  return "rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600";
}

function coverageClass(status: EvidenceCoverageItem["support_status"]) {
  if (status === "supported") return "rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700";
  if (status === "weak") return "rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-800";
  return "rounded-full bg-red-50 px-2 py-0.5 text-[11px] font-semibold text-red-700";
}
