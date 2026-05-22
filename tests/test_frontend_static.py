from pathlib import Path

from httpx import AsyncClient

TASKS_MD = Path(__file__).resolve().parent.parent / ".supports" / "TASKS.md"


async def test_root_redirects_to_ui(client: AsyncClient) -> None:
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


async def test_static_index_html_accessible(client: AsyncClient) -> None:
    response = await client.get("/static/index.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "mingmax" in response.text
    assert "analyze-form" in response.text


async def test_static_css_accessible(client: AsyncClient) -> None:
    response = await client.get("/static/styles.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


async def test_static_js_accessible(client: AsyncClient) -> None:
    response = await client.get("/static/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"] or "text/" in response.headers["content-type"]


async def test_index_html_has_dynamic_source_notice(client: AsyncClient) -> None:
    response = await client.get("/static/index.html")
    assert response.status_code == 200
    assert "source-notice" in response.text
    assert "source-text" in response.text


async def test_index_html_contains_disclaimer(client: AsyncClient) -> None:
    response = await client.get("/static/index.html")
    assert response.status_code == 200
    assert "免责声明" in response.text or "文化研究" in response.text


async def test_index_html_contains_form_fields(client: AsyncClient) -> None:
    response = await client.get("/static/index.html")
    assert response.status_code == 200
    body = response.text
    assert "calendar_type" in body
    assert "birth_datetime" in body
    assert "gender" in body
    assert "birth_place" in body
    assert "timezone" in body
    assert "themes" in body


async def test_frontend_preserves_local_birth_time_when_building_payload(client: AsyncClient) -> None:
    response = await client.get("/static/app.js")
    assert response.status_code == 200
    js = response.text
    assert "toISOStringWithOffset" in js
    assert "getTimezoneOffsetMinutes" in js
    assert "datetimeLocalValue" in js


async def test_frontend_has_dynamic_source_display(client: AsyncClient) -> None:
    response = await client.get("/static/app.js")
    assert response.status_code == 200
    js = response.text
    assert "source-notice" in js
    assert "stub" in js
    assert "sourceText" in js


async def test_frontend_reports_non_json_http_errors_with_status(client: AsyncClient) -> None:
    response = await client.get("/static/app.js")
    assert response.status_code == 200
    js = response.text
    assert "parseResponse" in js
    assert "HTTP_" in js


def test_tasks_document_uses_actual_static_frontend_branch_name() -> None:
    content = TASKS_MD.read_text(encoding="utf-8")
    assert "第一阶段拆分为 7 个可独立 review 和验收的分支" in content
