from datetime import datetime, timedelta, timezone

from app.agents.ziwei_analysis_agent import ZiweiAnalysisAgent
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import ZiweiChartEngine
from app.llm.mock import DISCLAIMER, MockLLMClient
from app.schemas.analysis import AnalysisOptions
from app.schemas.birth import BirthInfo
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
