from httpx import AsyncClient


async def test_analyze_valid_request(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ziwei/analyze",
        json={
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
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "chart" in data
    assert "analysis" in data
    assert "report_markdown" in data
    assert "免责声明" in data["report_markdown"]


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

    assert response.status_code == 200
    data = response.json()
    assert "Unsupported calendar type: lunar" in data["analysis"]["summary"]
