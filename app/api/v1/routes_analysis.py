from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.ziwei_analysis_agent import LLMOutputParseError
from app.api.dependencies import get_analysis_service
from app.api.errors import llm_client_failed_exception, llm_output_invalid_exception
from app.engines.errors import UnsupportedCalendarTypeError, UnsupportedGenderError
from app.llm.openai_compatible import LLMClientError
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, ErrorResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.post(
    "/ziwei/analyze",
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
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
    except UnsupportedGenderError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error": {
                    "code": "UNSUPPORTED_GENDER",
                    "message": str(e),
                    "details": [],
                }
            },
        )
    except LLMOutputParseError as e:
        raise llm_output_invalid_exception(e) from e
    except LLMClientError as e:
        raise llm_client_failed_exception(e) from e
