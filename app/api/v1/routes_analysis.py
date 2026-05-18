from fastapi import APIRouter, Depends

from app.agents.ziwei_analysis_agent import ZiweiAnalysisAgent
from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import UnsupportedCalendarTypeError, ZiweiChartEngine
from app.llm.mock import MockLLMClient
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisResult, ErrorResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()


def get_analysis_service() -> AnalysisService:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    llm = MockLLMClient()
    agent = ZiweiAnalysisAgent(llm)
    return AnalysisService(engine=engine, normalizer=normalizer, agent=agent)


@router.post("/ziwei/analyze", responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze(
    request: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    try:
        return await service.analyze(request.birth, request.options)
    except UnsupportedCalendarTypeError as e:
        return AnalysisResponse(
            analysis=AnalysisResult(summary=str(e)),
            chart={},
        )
