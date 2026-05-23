import json

from app.agents.prompt_loader import load_prompt
from app.engines.chart_facts import build_chart_facts
from app.llm.base import LLMClient
from app.llm.mock import DISCLAIMER
from app.schemas.analysis import AnalysisResult, FollowupQuestion, ThemeAnalysis
from app.schemas.chart import NormalizedChart


class LLMOutputParseError(RuntimeError):
    pass


def _parse_json_object(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMOutputParseError(f"LLM output is not valid JSON: {e}") from e
    if not isinstance(result, dict):
        raise LLMOutputParseError(f"LLM output is not a JSON object, got {type(result).__name__}")
    return result


def _require_fields(parsed: dict, fields: list[str], label: str) -> None:
    missing = [f for f in fields if f not in parsed]
    if missing:
        raise LLMOutputParseError(f"{label} missing required fields: {', '.join(missing)}")


def _parse_json_array(raw: str) -> list:
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMOutputParseError(f"LLM output is not valid JSON: {e}") from e
    if not isinstance(result, list):
        raise LLMOutputParseError(f"LLM output is not a JSON array, got {type(result).__name__}")
    return result


class ZiweiAnalysisAgent:
    def __init__(self, llm_client: LLMClient) -> None:
        self._llm = llm_client

    def _build_context(self, chart: NormalizedChart) -> str:
        return json.dumps(build_chart_facts(chart), ensure_ascii=False)

    async def analyze(self, chart: NormalizedChart, themes: list[str] | None = None) -> AnalysisResult:
        prompt = load_prompt("ziwei_analysis")
        context = self._build_context(chart)
        raw = await self._llm.generate(prompt=prompt, context=context)
        parsed = _parse_json_object(raw)
        _require_fields(
            parsed, ["summary", "strong_signals", "weak_hypotheses", "cross_checks", "safety_note"], "analysis"
        )
        try:
            return AnalysisResult(
                summary=parsed["summary"],
                strong_signals=parsed["strong_signals"],
                weak_hypotheses=parsed["weak_hypotheses"],
                cross_checks=parsed["cross_checks"],
                safety_note=parsed["safety_note"],
            )
        except Exception as e:
            raise LLMOutputParseError(f"Failed to parse analysis result: {e}") from e

    async def analyze_themes(self, chart: NormalizedChart, themes: list[str]) -> list[ThemeAnalysis]:
        prompt = load_prompt("theme_analysis")
        context = self._build_context(chart)
        results = []
        for theme in themes:
            themed_prompt = f"{prompt}\n\n分析主题：{theme}"
            raw = await self._llm.generate(prompt=themed_prompt, context=context)
            parsed = _parse_json_object(raw)
            _require_fields(
                parsed,
                ["theme", "observations", "supporting_evidence", "uncertainty", "followup_questions"],
                f"theme analysis for '{theme}'",
            )
            try:
                results.append(
                    ThemeAnalysis(
                        theme=parsed["theme"],
                        observations=parsed["observations"],
                        supporting_evidence=parsed["supporting_evidence"],
                        uncertainty=parsed["uncertainty"],
                        followup_questions=parsed["followup_questions"],
                    )
                )
            except Exception as e:
                raise LLMOutputParseError(f"Failed to parse theme analysis for '{theme}': {e}") from e
        return results

    async def generate_followup_questions(self, chart: NormalizedChart, analysis: str) -> list[FollowupQuestion]:
        prompt = load_prompt("followup_questions")
        context = f"{self._build_context(chart)}\n\n已有分析：\n{analysis}"
        raw = await self._llm.generate(prompt=prompt, context=context)
        parsed = _parse_json_array(raw)
        results = []
        for i, item in enumerate(parsed):
            if not isinstance(item, dict):
                raise LLMOutputParseError(f"Followup question {i} is not a JSON object")
            _require_fields(item, ["question", "reason"], f"followup question {i}")
            try:
                results.append(
                    FollowupQuestion(
                        question=item["question"],
                        reason=item["reason"],
                        related_chart_factors=item.get("related_chart_factors", []),
                    )
                )
            except Exception as e:
                raise LLMOutputParseError(f"Failed to parse followup question {i}: {e}") from e
        return results

    async def generate_report(self, chart: NormalizedChart, analysis: AnalysisResult) -> str:
        prompt = load_prompt("report")
        context = f"{self._build_context(chart)}\n\n已有分析：\n{analysis.model_dump_json()}"
        report = await self._llm.generate(prompt=prompt, context=context)
        if DISCLAIMER not in report:
            report = f"# 紫微斗数分析报告\n\n## 免责声明\n\n{DISCLAIMER}\n\n{report}"
        return report
