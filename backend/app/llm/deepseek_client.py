from openai import OpenAI

from app.core.config import Settings, get_settings
from app.models.schemas import Finding, Paper


class DeepSeekClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        if not self.settings.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured")
        self.client = OpenAI(
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
                {
                    "role": "system",
                    "content": "Extract 3 concise academic findings grounded only in the supplied abstracts.",
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nPapers:\n{paper_context}",
                },
            ],
        )
        content = response.choices[0].message.content or ""
        findings = [line.strip("- ").strip() for line in content.splitlines() if line.strip()]
        return [Finding(text=finding) for finding in findings[:5]]
