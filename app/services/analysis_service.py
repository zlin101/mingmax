from app.agents.ziwei_analysis_agent import ZiweiAnalysisAgent
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import ZiweiChartEngine
from app.llm.mock import DISCLAIMER
from app.schemas.analysis import AnalysisOptions, AnalysisResponse, AnalysisResult, FollowupQuestion, ThemeAnalysis
from app.schemas.birth import BirthInfo


class AnalysisService:
    def __init__(self, engine: ZiweiChartEngine, normalizer: ChartNormalizer, agent: ZiweiAnalysisAgent) -> None:
        self._engine = engine
        self._normalizer = normalizer
        self._agent = agent

    async def analyze(self, birth_info: BirthInfo, options: AnalysisOptions) -> AnalysisResponse:
        raw_chart = self._engine.build_chart(birth_info)
        normalized = self._normalizer.normalize(raw_chart)

        analysis_text = await self._agent.analyze(normalized, options.themes)

        theme_analyses = []
        if options.themes:
            theme_results = await self._agent.analyze_themes(normalized, options.themes)
            theme_analyses = [
                ThemeAnalysis(theme=theme, observations=[result], uncertainty="mock")
                for theme, result in zip(options.themes, theme_results)
            ]

        followup_questions = []
        if options.include_followup_questions:
            fq_text = await self._agent.generate_followup_questions(normalized, analysis_text)
            followup_questions = [FollowupQuestion(question=fq_text, reason="mock")]

        report_markdown = None
        if options.include_markdown_report:
            report_markdown = await self._agent.generate_report(normalized, analysis_text)

        analysis_result = AnalysisResult(
            summary=analysis_text,
            strong_signals=[],
            weak_hypotheses=[],
            cross_checks=[],
            theme_analyses=theme_analyses,
            safety_note=DISCLAIMER,
        )

        return AnalysisResponse(
            chart=normalized.model_dump(),
            analysis=analysis_result,
            followup_questions=followup_questions,
            report_markdown=report_markdown,
        )
