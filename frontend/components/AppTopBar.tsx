import type { ResearchResponse } from "@/lib/types";

interface AppTopBarProps {
  response: ResearchResponse | null;
  error: string | null;
  isLoading: boolean;
}

export function AppTopBar({ response, error, isLoading }: AppTopBarProps) {
  const sourceSummary = response?.search_source_summary ?? {};
  const demoCount = Number(sourceSummary.demo ?? 0);
  const status = error ? "Attention" : isLoading ? "Running" : response ? "Generated" : "Ready";

  return (
    <header className="panel-surface rounded-lg px-3 py-2.5 sm:px-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1">
          <h1 className="text-xl font-semibold tracking-normal text-slate-950 sm:text-2xl">Research Pilot</h1>
          <span className={statusClass(status)}>{status}</span>
          {demoCount > 0 ? <span className="text-xs font-semibold text-amber-800">Demo {demoCount}</span> : <span className="text-xs font-semibold text-cyan-800">Local first</span>}
          {response?.memory_storage ? <span className="hidden text-xs font-medium text-slate-500 sm:inline">Memory {response.memory_storage}</span> : null}
        </div>

        <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500">
          <CompactMetric label="papers" value={response?.papers.length ?? 0} />
          <CompactMetric label="claims" value={response?.evidence_items.length ?? 0} />
          <CompactMetric label="citations" value={response?.citations.length ?? 0} />
          <CompactMetric label="calls" value={response?.tool_call_logs.length ?? 0} />
        </div>
      </div>
    </header>
  );
}

function CompactMetric({ label, value }: { label: string; value: number }) {
  return (
    <span>
      <span className="font-semibold text-slate-950">{value}</span> {label}
    </span>
  );
}

function statusClass(status: string) {
  const base = "rounded-full px-2.5 py-1 text-[11px] font-semibold";
  if (status === "Generated") return `${base} bg-emerald-50 text-emerald-700`;
  if (status === "Running") return `${base} bg-cyan-50 text-cyan-800`;
  if (status === "Attention") return `${base} bg-red-50 text-red-700`;
  return `${base} bg-slate-100 text-slate-600`;
}
