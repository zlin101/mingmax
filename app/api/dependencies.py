from app.agents.ziwei_analysis_agent import ZiweiAnalysisAgent
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import ZiweiChartEngine
from app.llm.mock import MockLLMClient
from app.services.analysis_service import AnalysisService


def get_analysis_service() -> AnalysisService:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    llm = MockLLMClient()
    agent = ZiweiAnalysisAgent(llm)
    return AnalysisService(engine=engine, normalizer=normalizer, agent=agent)
