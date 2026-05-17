import pytest
from pydantic import ValidationError

from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisResult, FollowupQuestion


def test_analysis_result_serializable() -> None:
    result = AnalysisResult(summary="test summary")
    data = result.model_dump()
    assert data["summary"] == "test summary"
    assert data["strong_signals"] == []


def test_followup_question_serializable() -> None:
    q = FollowupQuestion(question="test?", reason="reason", related_chart_factors=["命宫"])
    data = q.model_dump()
    assert data["question"] == "test?"


def test_analysis_response_serializable() -> None:
    resp = AnalysisResponse(
        chart={"chart_id": "id", "summary": "s"},
        analysis=AnalysisResult(summary="summary"),
    )
    data = resp.model_dump()
    assert "chart" in data
    assert "analysis" in data


def test_analysis_request_validates_birth_info() -> None:
    request = AnalysisRequest(
        birth={
            "calendar_type": "solar",
            "birth_datetime": "1995-05-17T08:30:00+08:00",
            "gender": "female",
            "birth_place": "Shanghai, China",
            "timezone": "Asia/Shanghai",
        }
    )

    assert request.birth.timezone == "Asia/Shanghai"


def test_analysis_request_rejects_invalid_birth_info() -> None:
    with pytest.raises(ValidationError):
        AnalysisRequest(birth={"calendar_type": "solar"})
