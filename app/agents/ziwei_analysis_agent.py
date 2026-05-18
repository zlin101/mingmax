from app.agents.prompt_loader import load_prompt
from app.llm.base import LLMClient
from app.llm.mock import DISCLAIMER
from app.schemas.chart import NormalizedChart


class ZiweiAnalysisAgent:
    def __init__(self, llm_client: LLMClient) -> None:
        self._llm = llm_client

    async def analyze(self, chart: NormalizedChart, themes: list[str] | None = None) -> str:
        prompt = load_prompt("ziwei_analysis")
        context = chart.model_dump_json()
        return await self._llm.generate(prompt=prompt, context=context)

    async def analyze_themes(self, chart: NormalizedChart, themes: list[str]) -> list[str]:
        prompt = load_prompt("theme_analysis")
        context = chart.model_dump_json()
        results = []
        for theme in themes:
            themed_prompt = f"{prompt}\n\n分析主题：{theme}"
            result = await self._llm.generate(prompt=themed_prompt, context=context)
            results.append(result)
        return results

    async def generate_followup_questions(self, chart: NormalizedChart, analysis: str) -> str:
        prompt = load_prompt("followup_questions")
        context = f"{chart.model_dump_json()}\n\n已有分析：\n{analysis}"
        return await self._llm.generate(prompt=prompt, context=context)

    async def generate_report(self, chart: NormalizedChart, analysis: str) -> str:
        prompt = load_prompt("report")
        context = f"{chart.model_dump_json()}\n\n已有分析：\n{analysis}"
        report = await self._llm.generate(prompt=prompt, context=context)
        if DISCLAIMER not in report:
            report = f"# 紫微斗数分析报告\n\n## 免责声明\n\n{DISCLAIMER}\n\n{report}"
        return report
