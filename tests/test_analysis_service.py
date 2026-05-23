import json
from datetime import datetime, timedelta, timezone

from app.agents.ziwei_analysis_agent import ZiweiAnalysisAgent
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import ZiweiChartEngine
from app.llm.mock import DISCLAIMER, MockLLMClient
from app.schemas.analysis import AnalysisOptions
from app.schemas.birth import BirthInfo
from app.schemas.chart import NormalizedChart
from app.services.analysis_service import AnalysisService


def _birth_info() -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(1995, 5, 17, 8, 30, tzinfo=timezone(timedelta(hours=8))),
        gender="female",
        birth_place="Shanghai, China",
        timezone="Asia/Shanghai",
    )


def _service() -> AnalysisService:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    llm = MockLLMClient()
    agent = ZiweiAnalysisAgent(llm)
    return AnalysisService(engine=engine, normalizer=normalizer, agent=agent)


async def test_service_analysis_order() -> None:
    service = _service()
    result = await service.analyze(_birth_info(), AnalysisOptions())

    assert result.analysis is not None
    assert result.chart is not None
    assert "chart_id" in result.chart


async def test_service_calls_mock_llm() -> None:
    service = _service()
    result = await service.analyze(_birth_info(), AnalysisOptions())

    assert isinstance(result.analysis.summary, str)
    assert len(result.analysis.summary) > 0
    assert len(result.analysis.strong_signals) > 0
    assert DISCLAIMER in result.analysis.safety_note


async def test_service_includes_theme_analysis() -> None:
    service = _service()
    result = await service.analyze(_birth_info(), AnalysisOptions(themes=["career"]))

    assert len(result.analysis.theme_analyses) == 1
    assert result.analysis.theme_analyses[0].theme == "career"
    assert len(result.analysis.theme_analyses[0].observations) > 0


async def test_service_report_contains_disclaimer() -> None:
    service = _service()
    result = await service.analyze(_birth_info(), AnalysisOptions(include_markdown_report=True))

    assert result.report_markdown is not None
    assert DISCLAIMER in result.report_markdown


async def test_service_followup_questions() -> None:
    service = _service()
    result = await service.analyze(_birth_info(), AnalysisOptions(include_followup_questions=True))

    assert len(result.followup_questions) > 0
    assert result.followup_questions[0].question
    assert result.followup_questions[0].reason


async def test_service_no_report_when_disabled() -> None:
    service = _service()
    result = await service.analyze(_birth_info(), AnalysisOptions(include_markdown_report=False))

    assert result.report_markdown is None


async def test_service_analysis_has_no_mock_placeholders() -> None:
    service = _service()
    result = await service.analyze(_birth_info(), AnalysisOptions(themes=["career"], include_followup_questions=True))

    assert result.analysis.strong_signals != []
    for ta in result.analysis.theme_analyses:
        assert ta.uncertainty is not None
        assert ta.uncertainty != "mock"
    for fq in result.followup_questions:
        assert fq.reason != "mock"


def test_agent_context_uses_chart_facts_not_raw_chart() -> None:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    chart = normalizer.normalize(raw)
    agent = ZiweiAnalysisAgent(MockLLMClient())
    context = agent._build_context(chart)
    parsed = json.loads(context)
    assert "ming_palace" in parsed
    assert "four_hua" in parsed
    assert "palaces" in parsed
    for p in parsed["palaces"]:
        assert "opposite_palace" in p
        assert "san_fang_si_zheng" in p


async def test_service_output_passes_evidence_validation() -> None:
    from app.agents.analysis_evidence_validator import validate_analysis_output
    from app.engines.chart_facts import build_chart_facts

    service = _service()
    result = await service.analyze(
        _birth_info(),
        AnalysisOptions(themes=["career"], include_followup_questions=True, include_markdown_report=True),
    )
    chart = NormalizedChart(**result.chart)
    facts = build_chart_facts(chart)
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=result.analysis,
        theme_analyses=result.analysis.theme_analyses,
        followup_questions=result.followup_questions,
        report_markdown=result.report_markdown,
    )
    fabricated = [i for i in issues if i.code.startswith("FABRICATED")]
    assert len(fabricated) == 0, f"Fabricated references found: {[i.message for i in fabricated]}"
    unsafe = [i for i in issues if i.code == "UNSAFE_EXPRESSION"]
    assert len(unsafe) == 0, f"Unsafe expressions found: {[i.message for i in unsafe]}"
