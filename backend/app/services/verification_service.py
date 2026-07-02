import re

from app.models.schemas import Finding, Paper


STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "answer",
    "answers",
    "are",
    "based",
    "been",
    "being",
    "from",
    "have",
    "into",
    "that",
    "the",
    "their",
    "this",
    "with",
}


def verify_findings(findings: list[Finding], papers: list[Paper]) -> list[Finding]:
    verified: list[Finding] = []
    for finding in findings:
        best_paper, best_score = _best_supporting_paper(finding.text, papers)
        if best_paper is None:
            verified.append(finding.model_copy(update={"confidence": "low"}))
            continue

        confidence = "high" if best_score >= 0.55 else "medium" if best_score >= 0.25 else "low"
        if confidence == "low":
            verified.append(finding.model_copy(update={"confidence": "low"}))
            continue

        verified.append(
            finding.model_copy(
                update={
                    "confidence": confidence,
                    "evidence_paper_title": best_paper.title,
                    "evidence_snippet": _snippet(best_paper.abstract),
                }
            )
        )
    return verified


def _best_supporting_paper(finding_text: str, papers: list[Paper]) -> tuple[Paper | None, float]:
    finding_terms = _keywords(finding_text)
    if not finding_terms:
        return None, 0.0

    best_paper: Paper | None = None
    best_score = 0.0
    for paper in papers:
        abstract_terms = _keywords(paper.abstract)
        overlap = finding_terms & abstract_terms
        score = len(overlap) / len(finding_terms)
        if score > best_score:
            best_paper = paper
            best_score = score
    return best_paper, best_score


def _keywords(text: str) -> set[str]:
    terms = re.findall(r"[a-zA-Z][a-zA-Z0-9-]+", text.lower())
    return {term for term in terms if len(term) > 3 and term not in STOPWORDS}


def _snippet(text: str, limit: int = 240) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    return f"{clean[: limit - 3].rstrip()}..."
