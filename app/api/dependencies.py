from app.agents.ziwei_analysis_agent import ZiweiAnalysisAgent
from app.core.config import get_settings
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import ZiweiChartEngine
from app.llm.base import LLMClient
from app.llm.mock import MockLLMClient
from app.llm.openai_compatible import OpenAICompatibleLLMClient
from app.services.analysis_service import AnalysisService


def _get_llm_client() -> LLMClient:
    settings = get_settings()
    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleLLMClient(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    return MockLLMClient()


def get_analysis_service() -> AnalysisService:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    llm = _get_llm_client()
    agent = ZiweiAnalysisAgent(llm)
    return AnalysisService(engine=engine, normalizer=normalizer, agent=agent)
