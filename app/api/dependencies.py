from app.agents.ziwei_analysis_agent import ZiweiAnalysisAgent
from app.api.errors import llm_client_failed_exception
from app.core.config import get_settings
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import ZiweiChartEngine
from app.llm.base import LLMClient
from app.llm.mock import MockLLMClient
from app.llm.openai_compatible import LLMClientConfigError, LLMClientError, OpenAICompatibleLLMClient
from app.services.analysis_service import AnalysisService


def _get_llm_client() -> LLMClient:
    settings = get_settings()
    if settings.llm_provider == "mock":
        return MockLLMClient()

    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleLLMClient(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            wire_api=settings.llm_wire_api,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    raise LLMClientConfigError(f"Unsupported LLM provider: {settings.llm_provider}")


def get_analysis_service() -> AnalysisService:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    try:
        llm = _get_llm_client()
    except LLMClientError as e:
        raise llm_client_failed_exception(e) from e
    agent = ZiweiAnalysisAgent(llm)
    return AnalysisService(engine=engine, normalizer=normalizer, agent=agent)
