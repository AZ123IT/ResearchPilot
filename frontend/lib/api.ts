import type { ResearchRequest, ResearchResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function runResearch(request: ResearchRequest): Promise<ResearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/research/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let detail = "";
    try {
      const payload = (await response.json()) as { detail?: unknown };
      detail = payload.detail ? `: ${JSON.stringify(payload.detail)}` : "";
    } catch {
      detail = "";
    }
    throw new Error(`Research request failed with ${response.status}${detail}`);
  }

  return response.json() as Promise<ResearchResponse>;
}
