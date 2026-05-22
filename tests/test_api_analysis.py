from pathlib import Path

import pytest
from httpx import AsyncClient

from app.api.dependencies import get_analysis_service
from app.llm.openai_compatible import LLMClientError
from app.main import app


class FailingLLMAnalysisService:
    async def analyze(self, birth_info: object, options: object) -> object:
        raise LLMClientError("LLM request failed")


def _valid_request_payload() -> dict[str, object]:
    return {
        "birth": {
            "calendar_type": "solar",
            "birth_datetime": "1995-05-17T08:30:00+08:00",
            "gender": "female",
            "birth_place": "Shanghai, China",
            "timezone": "Asia/Shanghai",
        },
        "options": {
            "themes": ["career"],
            "include_followup_questions": True,
            "include_markdown_report": True,
        },
    }


async def test_analyze_valid_request(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ziwei/analyze",
        json=_valid_request_payload(),
    )

    assert response.status_code == 200
    data = response.json()
    assert "chart" in data
    assert "analysis" in data
    assert "report_markdown" in data
    assert "免责声明" in data["report_markdown"]
    assert data["chart"]["source"] != "stub"
    assert data["chart"]["source"] == "iztro_py"


async def test_analyze_invalid_birth_info(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ziwei/analyze",
        json={
            "birth": {
                "calendar_type": "solar",
            },
            "options": {},
        },
    )

    assert response.status_code == 422


async def test_analyze_invalid_gender(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ziwei/analyze",
        json={
            "birth": {
                "calendar_type": "solar",
                "birth_datetime": "1995-05-17T08:30:00+08:00",
                "gender": "invalid",
                "birth_place": "Shanghai, China",
                "timezone": "Asia/Shanghai",
            },
        },
    )

    assert response.status_code == 422


async def test_analyze_naive_birth_datetime_is_rejected(client: AsyncClient) -> None:
    payload = _valid_request_payload()
    birth = payload["birth"]
    assert isinstance(birth, dict)
    birth["birth_datetime"] = "1995-05-17T08:30:00"

    response = await client.post("/api/v1/ziwei/analyze", json=payload)

    assert response.status_code == 422


async def test_analyze_lunar_calendar(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ziwei/analyze",
        json={
            "birth": {
                "calendar_type": "lunar",
                "birth_datetime": "1995-05-17T08:30:00+08:00",
                "gender": "female",
                "birth_place": "Shanghai, China",
                "timezone": "Asia/Shanghai",
            },
        },
    )

    assert response.status_code == 422
    data = response.json()
    assert data["detail"]["error"]["code"] == "UNSUPPORTED_CALENDAR_TYPE"
    assert "Unsupported calendar type: lunar" in data["detail"]["error"]["message"]


async def test_analyze_unknown_gender(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ziwei/analyze",
        json={
            "birth": {
                "calendar_type": "solar",
                "birth_datetime": "1995-05-17T08:30:00+08:00",
                "gender": "unknown",
                "birth_place": "Shanghai, China",
                "timezone": "Asia/Shanghai",
            },
        },
    )

    assert response.status_code == 422
    data = response.json()
    assert data["detail"]["error"]["code"] == "UNSUPPORTED_GENDER"
    assert "not supported" in data["detail"]["error"]["message"]


async def test_analyze_llm_client_failure_returns_error_response(client: AsyncClient) -> None:
    app.dependency_overrides[get_analysis_service] = lambda: FailingLLMAnalysisService()
    try:
        response = await client.post("/api/v1/ziwei/analyze", json=_valid_request_payload())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    data = response.json()
    assert data["detail"]["error"]["code"] == "LLM_CLIENT_FAILED"
    assert data["detail"]["error"]["message"] == "LLM request failed"


async def test_analyze_llm_config_failure_returns_error_response(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MINGMAX_LLM_PROVIDER", "typo")

    response = await client.post("/api/v1/ziwei/analyze", json=_valid_request_payload())

    assert response.status_code == 500
    data = response.json()
    assert data["detail"]["error"]["code"] == "LLM_CLIENT_FAILED"
    assert "Unsupported LLM provider" in data["detail"]["error"]["message"]


def test_api_routes_do_not_import_engine_providers() -> None:
    route_source = Path("app/api/v1/routes_analysis.py").read_text(encoding="utf-8")
    assert "app.engines.providers" not in route_source
