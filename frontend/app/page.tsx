import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <h1 className="text-3xl font-semibold">ResearchPilot</h1>
      <p className="mt-3 max-w-2xl text-slate-600">
        MCP-based academic research workflow with structured evidence, citations, and notes.
      </p>
      <Link className="mt-6 inline-block rounded bg-slate-900 px-4 py-2 text-white" href="/research">
        Open research runner
      </Link>
    </main>
  );
}
