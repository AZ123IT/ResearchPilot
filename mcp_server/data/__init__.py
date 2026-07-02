import json
from pathlib import Path


DEMO_WARNING = "Demo mode enabled: using local fixture papers instead of external academic APIs."


def demo_mode_enabled() -> bool:
    import os

    return os.getenv("RESEARCHPILOT_DEMO_MODE", "false").lower() in {"1", "true", "yes"}


def load_demo_papers() -> list[dict]:
    path = Path(__file__).with_name("demo_papers.json")
    return json.loads(path.read_text())


def find_demo_paper(paper_id: str) -> dict | None:
    for paper in load_demo_papers():
        if paper.get("paper_id") == paper_id:
            return paper
    return None
