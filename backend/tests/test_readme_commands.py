from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_readme_referenced_local_scripts_exist():
    readme = (PROJECT_ROOT / "README.md").read_text()

    for script in [
        "scripts/run_backend.sh",
        "scripts/run_frontend.sh",
        "scripts/run_mcp_server.sh",
        "scripts/test_all.sh",
    ]:
        assert script in readme
        assert (PROJECT_ROOT / script).exists()


def test_quick_start_and_public_docs_exist():
    readme = (PROJECT_ROOT / "README.md").read_text()

    assert "## Quick Start" in readme
    for command in [
        "python3 -m venv .venv",
        ".venv/bin/python -m pip install -r backend/requirements.txt -r mcp_server/requirements.txt",
        "npm install",
        "RESEARCHPILOT_DEMO_MODE=true scripts/run_backend.sh",
        "scripts/run_frontend.sh",
        "scripts/test_all.sh",
    ]:
        assert command in readme

    for doc in [
        "docs/ARCHITECTURE.md",
        "docs/PROJECT_NOTES.md",
        "docs/DEMO_SCRIPT.md",
    ]:
        path = PROJECT_ROOT / doc
        assert path.exists()
        assert path.read_text().strip()


def test_demo_papers_fixture_has_required_fields():
    papers = json.loads((PROJECT_ROOT / "mcp_server/data/demo_papers.json").read_text())
    required = {"paper_id", "title", "authors", "abstract", "published_date", "source", "url", "citation_count"}

    assert len(papers) >= 3
    for paper in papers:
        assert required <= set(paper)
        assert paper["source"] == "demo"
        assert paper["paper_id"].startswith("demo-")
        assert paper["title"]
        assert paper["authors"]
        assert paper["abstract"]
