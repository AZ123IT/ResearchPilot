import json
import re
from typing import Any

from openai import OpenAI

from app.core.config import Settings, get_settings
from app.models.schemas import Finding, Paper


MAX_FINDINGS = 5
SYSTEM_PROMPT = (
    "Extract 3 concise academic findings grounded only in the supplied abstracts. "
    'Respond with JSON only, in the form {"findings": ["finding one", "finding two", "finding three"]}. '
    "Each finding is one plain sentence with no numbering or markdown."
)
LIST_MARKER = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")


class DeepSeekClient:
    def __init__(self, settings: Settings | None = None, client: Any | None = None):
        self.settings = settings or get_settings()
        if not self.settings.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured")
        self.client = client or OpenAI(
            api_key=self.settings.deepseek_api_key,
            base_url=self.settings.deepseek_base_url,
            timeout=20,
        )

    def extract_findings(self, question: str, papers: list[Paper]) -> list[Finding]:
        paper_context = "\n\n".join(
            f"Title: {paper.title}\nAbstract: {paper.abstract}" for paper in papers[:5]
        )
        response = self.client.chat.completions.create(
            model=self.settings.deepseek_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Question: {question}\n\nPapers:\n{paper_context}"},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or ""
        return [Finding(text=text) for text in parse_findings(content)[:MAX_FINDINGS]]


def parse_findings(content: str) -> list[str]:
    """Read findings from the model's JSON reply, tolerating a plain list as a fallback."""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return _parse_list_lines(content)

    items = payload.get("findings", []) if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return []
    findings = []
    for item in items:
        text = (item.get("text") or item.get("claim")) if isinstance(item, dict) else item
        if isinstance(text, str) and text.strip():
            findings.append(_clean(text))
    return findings


def _parse_list_lines(content: str) -> list[str]:
    findings = []
    for line in content.splitlines():
        text = _clean(line)
        # Lead-ins such as "Here are three findings:" are not findings.
        if text and not text.endswith(":"):
            findings.append(text)
    return findings


def _clean(text: str) -> str:
    return LIST_MARKER.sub("", text).replace("**", "").strip()
