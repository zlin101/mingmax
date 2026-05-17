from app.schemas.analysis import AnalysisResponse, AnalysisResult, FollowupQuestion


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
