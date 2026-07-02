"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { CitationsPanel } from "@/components/CitationsPanel";
import { LiteratureReview } from "@/components/LiteratureReview";
import { SourcesTable } from "@/components/SourcesTable";
import type { ResearchResponse } from "@/lib/types";

interface PaginatedResultsProps {
  response: ResearchResponse | null;
  isLoading: boolean;
}

export function PaginatedResults({ response, isLoading }: PaginatedResultsProps) {
  const [activePage, setActivePage] = useState(0);
  const pageFrameRef = useRef<HTMLDivElement>(null);
  const pages = useMemo(
    () => [
      {
        label: "Review",
        content: <LiteratureReview isLoading={isLoading} response={response} />,
      },
      {
        label: "Sources",
        content: <SourcesTable citations={response?.citations ?? []} evidenceItems={response?.evidence_items ?? []} papers={response?.papers ?? []} />,
      },
      {
        label: "Bibliography",
        content: <CitationsPanel citations={response?.citations ?? []} />,
      },
    ],
    [isLoading, response],
  );

  useEffect(() => {
    setActivePage(0);
  }, [response?.question]);

  useEffect(() => {
    pageFrameRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  }, [activePage]);

  function goToPreviousPage() {
    setActivePage((page) => Math.max(0, page - 1));
  }

  function goToNextPage() {
    setActivePage((page) => Math.min(pages.length - 1, page + 1));
  }

  return (
    <section className="grid min-w-0 gap-3">
      <div className="min-w-0 lg:max-h-[calc(100vh-320px)] lg:overflow-y-auto lg:pr-1 [scrollbar-gutter:stable]" ref={pageFrameRef}>
        {pages[activePage].content}
      </div>

      <nav
        aria-label="Result pages"
        className="panel-surface flex items-center justify-center gap-4 rounded-full px-4 py-3"
      >
        <button
          aria-label="Previous result page"
          className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-2xl leading-none text-slate-700 shadow-sm transition hover:border-cyan-300 hover:text-cyan-800 disabled:cursor-not-allowed disabled:opacity-35"
          disabled={activePage === 0}
          onClick={goToPreviousPage}
          type="button"
        >
          <span aria-hidden="true">‹</span>
        </button>

        <div className="flex items-center gap-3">
          {pages.map((page, index) => (
            <button
              aria-current={activePage === index ? "page" : undefined}
              aria-label={`Go to ${page.label} page`}
              className="flex h-8 w-8 items-center justify-center rounded-full transition hover:bg-slate-100"
              key={page.label}
              onClick={() => setActivePage(index)}
              type="button"
            >
              <span
                aria-hidden="true"
                className={`block rounded-full transition-all ${
                  activePage === index ? "h-3 w-3 bg-cyan-800 shadow-[0_0_0_4px_rgba(8,145,178,0.12)]" : "h-2 w-2 bg-slate-300"
                }`}
              />
            </button>
          ))}
        </div>

        <button
          aria-label="Next result page"
          className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-2xl leading-none text-slate-700 shadow-sm transition hover:border-cyan-300 hover:text-cyan-800 disabled:cursor-not-allowed disabled:opacity-35"
          disabled={activePage === pages.length - 1}
          onClick={goToNextPage}
          type="button"
        >
          <span aria-hidden="true">›</span>
        </button>
      </nav>
    </section>
  );
}
