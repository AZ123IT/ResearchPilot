"use client";

import { useMemo, useState } from "react";

import type { AgentStep, ResearchNote, ResearchResponse, ToolCallLog } from "@/lib/types";

interface InspectorPanelProps {
  response: ResearchResponse | null;
  error: string | null;
  isLoading: boolean;
}

type InspectorTab = "workflow" | "calls" | "memory" | "warnings";
type TimelineStep = Omit<AgentStep, "status"> & { status: AgentStep["status"] | "pending" };

export function InspectorPanel({ response, error, isLoading }: InspectorPanelProps) {
  const [activeTab, setActiveTab] = useState<InspectorTab>("workflow");
  const [isOpen, setIsOpen] = useState(false);
  const steps = response?.steps ?? loadingSteps(isLoading);
  const calls = response?.tool_call_logs ?? [];
  const notes = useMemo(() => uniqueNotes([...(response?.prior_notes ?? []), ...(response?.reused_notes ?? [])]), [response]);
  const warnings = [
    ...(error ? [error] : []),
    ...(response?.fallback_summary ?? []),
    ...(response?.warnings ?? []),
    ...(response?.literature_review.low_confidence_claims ?? []).map((claim) => `Low confidence: ${claim}`),
  ];

  if (!isOpen) {
    return (
      <button
        aria-label="Open audit inspector"
        className="fixed bottom-20 right-3 z-40 rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-800 shadow-lg shadow-slate-900/10 transition hover:border-cyan-300 hover:text-cyan-800 sm:bottom-4 sm:right-4 sm:px-4 sm:py-3 sm:text-sm"
        onClick={() => setIsOpen(true)}
        type="button"
      >
        <span className="sm:hidden">Audit</span>
        <span className="hidden sm:inline">Audit · {steps.length} steps · {calls.length} calls</span>
      </button>
    );
  }

  return (
    <section className="panel-surface fixed inset-x-3 bottom-3 z-50 max-h-[82vh] overflow-y-auto rounded-xl p-4 shadow-2xl shadow-slate-900/20 sm:left-auto sm:right-4 sm:w-[420px]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="micro-label text-slate-500">Inspector</p>
          <h2 className="mt-1 text-xl font-semibold">Run audit</h2>
        </div>
        <div className="flex items-center gap-2">
          {isLoading ? <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-800">Running</span> : null}
          <button
            aria-label="Close audit inspector"
            className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-white text-lg leading-none text-slate-500 transition hover:text-slate-950"
            onClick={() => setIsOpen(false)}
            type="button"
          >
            ×
          </button>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-1 rounded-lg bg-slate-100 p-1 text-xs font-semibold sm:grid-cols-4">
        <TabButton active={activeTab === "workflow"} count={steps.length} label="Workflow" onClick={() => setActiveTab("workflow")} />
        <TabButton active={activeTab === "calls"} count={calls.length} label="Calls" onClick={() => setActiveTab("calls")} />
        <TabButton active={activeTab === "memory"} count={notes.length} label="Memory" onClick={() => setActiveTab("memory")} />
        <TabButton active={activeTab === "warnings"} count={warnings.length} label="Notes" onClick={() => setActiveTab("warnings")} />
      </div>

      <div className="mt-4">
        {activeTab === "workflow" ? <WorkflowTab steps={steps} /> : null}
        {activeTab === "calls" ? <CallsTab logs={calls} /> : null}
        {activeTab === "memory" ? <MemoryTab notes={notes} /> : null}
        {activeTab === "warnings" ? <WarningsTab items={warnings} /> : null}
      </div>
    </section>
  );
}

function TabButton({ active, count, label, onClick }: { active: boolean; count: number; label: string; onClick: () => void }) {
  return (
    <button
      className={`rounded-md px-3 py-2 text-left transition ${active ? "bg-white text-slate-950 shadow-sm" : "text-slate-500 hover:bg-white/70 hover:text-slate-800"}`}
      onClick={onClick}
      type="button"
    >
      <span className="block">{label}</span>
      <span className="text-[11px] font-medium text-slate-500">{count}</span>
    </button>
  );
}

function WorkflowTab({ steps }: { steps: TimelineStep[] }) {
  return (
    <ol className="grid gap-3">
      {steps.map((step, index) => (
        <li className="grid grid-cols-[18px_1fr] gap-3" key={`${step.step_name}-${index}`}>
          <span className={`mt-1.5 h-2.5 w-2.5 rounded-full ${statusDot(step.status)}`} />
          <div className="min-w-0 border-b border-slate-100 pb-3 last:border-b-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-slate-950">{labelize(step.step_name)}</span>
              <StatusBadge status={step.status} />
              {step.tool_name ? <span className="rounded-full bg-cyan-50 px-2 py-0.5 text-[11px] font-semibold text-cyan-800">{step.tool_name}</span> : null}
              {step.fallback_used ? <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-800">fallback</span> : null}
            </div>
            <p className="mt-1 text-xs leading-5 text-slate-600">{step.summary}</p>
            {step.duration_ms !== null && step.duration_ms !== undefined ? <p className="mt-1 text-[11px] text-slate-400">{step.duration_ms.toFixed(1)} ms</p> : null}
          </div>
        </li>
      ))}
    </ol>
  );
}

function CallsTab({ logs }: { logs: ToolCallLog[] }) {
  const [openIndex, setOpenIndex] = useState(0);

  if (!logs.length) {
    return <p className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">Tool call inputs and previews appear after a run.</p>;
  }

  return (
    <div className="grid gap-2">
      {logs.map((log, index) => (
        <article className="rounded-md border border-slate-200 bg-white" key={`${log.tool_name}-${index}`}>
          <button className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left" onClick={() => setOpenIndex(openIndex === index ? -1 : index)} type="button">
            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold text-slate-950">{log.tool_name}</span>
              <span className="text-xs text-slate-500">{labelize(log.step_name)}</span>
            </span>
            <span className="flex shrink-0 items-center gap-2 text-[11px]">
              <StatusBadge status={log.status} />
              <span className="rounded bg-slate-100 px-2 py-0.5 text-slate-600">{log.duration_ms.toFixed(1)} ms</span>
            </span>
          </button>
          {openIndex === index ? (
            <div className="grid gap-3 border-t border-slate-100 bg-slate-50 p-3 text-xs">
              <JsonBlock label="Input" value={log.input} />
              <JsonBlock label="Output preview" value={log.output_preview} />
              {log.error_message ? <p className="rounded bg-red-50 p-2 text-red-700">{log.error_message}</p> : null}
            </div>
          ) : null}
        </article>
      ))}
    </div>
  );
}

function MemoryTab({ notes }: { notes: ResearchNote[] }) {
  if (!notes.length) {
    return <p className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">Saved and reused notes appear after memory search.</p>;
  }

  return (
    <div className="grid gap-3">
      {notes.map((note) => (
        <article className="border-b border-slate-100 pb-3 last:border-b-0" key={note.note_id}>
          <h3 className="text-sm font-semibold leading-5 text-slate-950">{note.title || note.paper_id || "Research note"}</h3>
          <p className="mt-1 text-xs leading-5 text-slate-600">{note.content_preview}</p>
          <div className="mt-2 flex flex-wrap gap-2 text-[11px] font-semibold">
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-600">{note.storage}</span>
            {note.source ? <span className="rounded-full bg-cyan-50 px-2 py-0.5 text-cyan-800">{note.source}</span> : null}
          </div>
        </article>
      ))}
    </div>
  );
}

function WarningsTab({ items }: { items: string[] }) {
  if (!items.length) {
    return <p className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">No fallback notes or low-confidence claims for this run.</p>;
  }

  return (
    <ul className="grid gap-2 text-sm leading-5 text-slate-700">
      {items.map((item, index) => (
        <li className="rounded-md border border-amber-100 bg-amber-50 px-3 py-2 text-amber-900" key={`${index}-${item}`}>
          {item}
        </li>
      ))}
    </ul>
  );
}

function JsonBlock({ label, value }: { label: string; value: unknown }) {
  return (
    <div>
      <div className="mb-1 font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</div>
      <pre className="max-h-44 max-w-full overflow-auto rounded-md bg-white p-2 text-[11px] leading-5 text-slate-700">{JSON.stringify(value, null, 2)}</pre>
    </div>
  );
}

function StatusBadge({ status }: { status: AgentStep["status"] | "pending" }) {
  return <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${statusBadge(status)}`}>{status}</span>;
}

function loadingSteps(isLoading: boolean): TimelineStep[] {
  const names = isLoading
    ? ["plan_research_task", "search_notes", "search_papers", "fetch_paper_details", "extract_summary", "verify_evidence", "format_citations", "save_notes", "generate_final_review"]
    : ["idle"];

  return names.map((step_name) => ({
    step_name,
    status: "pending",
    tool_name: null,
    summary: isLoading ? "Waiting for backend step output..." : "Submit a research question to inspect the run.",
    input: {},
    output_preview: {},
    duration_ms: null,
    fallback_used: false,
  }));
}

function uniqueNotes(notes: ResearchNote[]) {
  const seen = new Set<string>();
  return notes.filter((note) => {
    const key = `${note.paper_id ?? ""}:${note.title ?? ""}:${note.content_preview}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function labelize(value: string) {
  return value.replaceAll("_", " ");
}

function statusDot(status: string) {
  if (status === "success") return "bg-emerald-500";
  if (status === "warning") return "bg-amber-500";
  if (status === "error") return "bg-red-500";
  return "bg-slate-300";
}

function statusBadge(status: string) {
  if (status === "success") return "bg-emerald-50 text-emerald-700";
  if (status === "warning") return "bg-amber-50 text-amber-800";
  if (status === "error") return "bg-red-50 text-red-700";
  return "bg-slate-100 text-slate-600";
}
