from app.models.schemas import Finding, Paper
from app.services.verification_service import verify_findings


def paper() -> Paper:
    return Paper(
        paper_id="p1",
        title="RAG Faithfulness",
        authors=["A. Researcher"],
        abstract="Retrieval augmented generation improves faithfulness by grounding answers in retrieved evidence.",
        published_date="2024-01-01",
        source="arxiv",
        url="https://example.com/p1",
        citation_count=None,
    )


def test_finding_with_abstract_evidence_is_high_or_medium_confidence():
    findings = [Finding(text="RAG improves faithfulness with retrieved evidence.")]

    verified = verify_findings(findings, [paper()])

    assert verified[0].confidence in {"high", "medium"}
    assert verified[0].evidence_paper_title == "RAG Faithfulness"
    assert "retrieved evidence" in verified[0].evidence_snippet.lower()


def test_finding_without_evidence_is_low_confidence():
    findings = [Finding(text="Graph neural networks reduce GPU memory usage.")]

    verified = verify_findings(findings, [paper()])

    assert verified[0].confidence == "low"
    assert verified[0].evidence_paper_title is None
