from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_analysis_service
from app.engines.ziwei_chart_engine import UnsupportedCalendarTypeError
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, ErrorResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.post("/ziwei/analyze", responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze(
    request: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    try:
        return await service.analyze(request.birth, request.options)
    except UnsupportedCalendarTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error": {
                    "code": "UNSUPPORTED_CALENDAR_TYPE",
                    "message": str(e),
                    "details": [],
                }
            },
        )
