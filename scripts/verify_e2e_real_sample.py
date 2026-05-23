import argparse
import asyncio
import json
import sys

from app.agents.analysis_evidence_validator import validate_analysis_output
from app.agents.ziwei_analysis_agent import ZiweiAnalysisAgent
from app.engines.chart_facts import build_chart_facts
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import ZiweiChartEngine
from app.llm.mock import MockLLMClient
from app.schemas.birth import BirthInfo
from scripts.verify_private_chart_sample import _parse_reference


def _build_birth_info(ref: dict) -> BirthInfo:
    from datetime import datetime, timedelta, timezone

    dt_str = ref["clock_time"]
    dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone(timedelta(hours=8)))
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=dt,
        gender=ref["gender"],
        birth_place="Redacted",
        timezone="Asia/Shanghai",
        longitude=ref.get("longitude"),
    )


async def _run_pipeline(birth_info: BirthInfo, use_mock: bool) -> dict:
    engine = ZiweiChartEngine()
    raw = engine.build_chart(birth_info)
    normalizer = ChartNormalizer()
    normalized = normalizer.normalize(raw)

    facts = build_chart_facts(normalized)

    if use_mock:
        llm = MockLLMClient()
    else:
        from app.core.config import Settings
        from app.llm.openai_compatible import OpenAICompatibleClient

        settings = Settings()
        llm = OpenAICompatibleClient(settings)

    agent = ZiweiAnalysisAgent(llm)

    analysis = await agent.analyze(normalized)

    theme_analyses = await agent.analyze_themes(normalized, ["career", "relationship"])
    analysis = analysis.model_copy(update={"theme_analyses": theme_analyses})

    followup_questions = await agent.generate_followup_questions(normalized, analysis.model_dump_json())

    report = await agent.generate_report(normalized, analysis)

    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=theme_analyses,
        followup_questions=followup_questions,
        report_markdown=report,
    )

    return {
        "chart_source": normalized.source,
        "ming_palace": facts.get("ming_palace"),
        "body_palace": facts.get("body_palace"),
        "palace_count": len(facts.get("palaces", [])),
        "llm_mode": "mock" if use_mock else "real",
        "validation_issues": [{"severity": i.severity, "code": i.code, "message": i.message} for i in issues],
        "issue_count": len(issues),
        "error_count": len([i for i in issues if i.severity == "error"]),
        "warning_count": len([i for i in issues if i.severity == "warning"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="End-to-end validation with evidence checking")
    parser.add_argument("input_file", help="Path to private verification file")
    parser.add_argument("--mock-llm", action="store_true", help="Use mock LLM instead of real")
    args = parser.parse_args()

    with open(args.input_file, encoding="utf-8") as f:
        text = f.read()

    ref = _parse_reference(text)
    if "clock_time" not in ref or "gender" not in ref:
        print("ERROR: Could not extract clock_time and gender from input file", file=sys.stderr)
        sys.exit(1)

    birth_info = _build_birth_info(ref)
    result = asyncio.run(_run_pipeline(birth_info, use_mock=args.mock_llm))

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
