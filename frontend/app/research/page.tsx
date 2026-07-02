"use client";

import { useState } from "react";

import { AppTopBar } from "@/components/AppTopBar";
import { InspectorPanel } from "@/components/InspectorPanel";
import { PaginatedResults } from "@/components/PaginatedResults";
import { ResearchForm } from "@/components/ResearchForm";
import { runResearch } from "@/lib/api";
import type { ResearchRequest, ResearchResponse } from "@/lib/types";

const initialRequest: ResearchRequest = {
  question: "What are recent methods for improving RAG faithfulness?",
  max_results: 5,
  citation_style: "IEEE",
};

export default function ResearchPage() {
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(request: ResearchRequest) {
    setIsLoading(true);
    setError(null);
    try {
      const response = await runResearch(request);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Research request failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#eef2f3] text-slate-950">
      <div className="mx-auto grid w-full max-w-[1440px] gap-3 px-3 py-3 sm:px-5 lg:px-7">
        <AppTopBar error={error} isLoading={isLoading} response={result} />

        <section className="grid min-w-0 gap-3 content-start">
          <ResearchForm defaultValue={initialRequest} isLoading={isLoading} onSubmit={handleSubmit} />
          <PaginatedResults isLoading={isLoading} response={result} />
        </section>

        <InspectorPanel error={error} isLoading={isLoading} response={result} />
      </div>
    </main>
  );
}
