import subprocess
from pathlib import Path

from httpx import AsyncClient

APP_JS = Path("app/web/static/app.js")
TASKS_MD = Path(".supports/TASKS.md")


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


async def test_index_html_contains_stub_notice(client: AsyncClient) -> None:
    response = await client.get("/static/index.html")
    assert response.status_code == 200
    assert "stub" in response.text.lower()


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


def test_frontend_preserves_local_birth_time_when_building_payload() -> None:
    script = f"""
const fs = require("fs");
const vm = require("vm");

const elements = {{
  "analyze-form": {{
    addEventListener: function (_event, handler) {{
      this.handler = handler;
    }},
  }},
  "loading": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "error-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "error-message": {{ textContent: "" }},
  "result-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "submit-btn": {{ disabled: false }},
  "chart-info": {{ textContent: "" }},
  "analysis-summary": {{ textContent: "" }},
  "theme-analyses-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "theme-analyses": {{ innerHTML: "", appendChild: function () {{}} }},
  "followup-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "followup-questions": {{ innerHTML: "", appendChild: function () {{}} }},
  "report-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "report-markdown": {{ textContent: "" }},
  "calendar_type": {{ value: "solar" }},
  "birth_datetime": {{ value: "1995-05-17T08:30" }},
  "gender": {{ value: "female" }},
  "birth_place": {{ value: "Shanghai, China" }},
  "timezone": {{ value: "Asia/Shanghai" }},
  "include_followup_questions": {{ checked: true }},
  "include_markdown_report": {{ checked: true }},
}};

let capturedPayload = null;
const context = {{
  document: {{
    getElementById: function (id) {{ return elements[id]; }},
    querySelectorAll: function () {{ return []; }},
    createElement: function () {{
      return {{
        className: "",
        textContent: "",
        appendChild: function () {{}},
      }};
    }},
  }},
  fetch: function (_url, options) {{
    capturedPayload = JSON.parse(options.body);
    return Promise.resolve({{
      ok: true,
      status: 200,
      json: function () {{
        return Promise.resolve({{
          chart: {{}},
          analysis: {{}},
          followup_questions: [],
          report_markdown: null,
        }});
      }},
    }});
  }},
  Intl: Intl,
  Date: Date,
  JSON: JSON,
  String: String,
  Math: Math,
  parseInt: parseInt,
  Promise: Promise,
  alert: function () {{}},
}};

vm.runInNewContext(fs.readFileSync("{APP_JS}", "utf8"), context);
elements["analyze-form"].handler({{ preventDefault: function () {{}} }});

Promise.resolve().then(function () {{
  if (capturedPayload.birth.birth_datetime !== "1995-05-17T08:30:00+08:00") {{
    throw new Error("unexpected birth_datetime: " + capturedPayload.birth.birth_datetime);
  }}
}});
"""
    result = subprocess.run(["node", "-e", script], check=False, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


def test_tasks_document_uses_actual_static_frontend_branch_name() -> None:
    content = TASKS_MD.read_text(encoding="utf-8")

    assert "第一阶段拆分为 6 个可独立 review 和验收的分支" in content
    assert "feature/v0.1-simple-frontend" not in content
    assert "feature/v0.1-static-frontend" in content


def test_frontend_reports_non_json_http_errors_with_status() -> None:
    script = f"""
const fs = require("fs");
const vm = require("vm");

const elements = {{
  "analyze-form": {{
    addEventListener: function (_event, handler) {{
      this.handler = handler;
    }},
  }},
  "loading": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "error-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "error-message": {{ textContent: "" }},
  "result-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "submit-btn": {{ disabled: false }},
  "chart-info": {{ textContent: "" }},
  "analysis-summary": {{ textContent: "" }},
  "theme-analyses-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "theme-analyses": {{ innerHTML: "", appendChild: function () {{}} }},
  "followup-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "followup-questions": {{ innerHTML: "", appendChild: function () {{}} }},
  "report-section": {{ classList: {{ add: function () {{}}, remove: function () {{}} }} }},
  "report-markdown": {{ textContent: "" }},
  "calendar_type": {{ value: "solar" }},
  "birth_datetime": {{ value: "1995-05-17T08:30" }},
  "gender": {{ value: "female" }},
  "birth_place": {{ value: "Shanghai, China" }},
  "timezone": {{ value: "Asia/Shanghai" }},
  "include_followup_questions": {{ checked: true }},
  "include_markdown_report": {{ checked: true }},
}};

const context = {{
  document: {{
    getElementById: function (id) {{ return elements[id]; }},
    querySelectorAll: function () {{ return []; }},
    createElement: function () {{
      return {{
        className: "",
        textContent: "",
        appendChild: function () {{}},
      }};
    }},
  }},
  fetch: function () {{
    return Promise.resolve({{
      ok: false,
      status: 502,
      headers: {{ get: function () {{ return "text/plain"; }} }},
      text: function () {{ return Promise.resolve("Bad Gateway"); }},
      json: function () {{ return Promise.reject(new Error("invalid json")); }},
    }});
  }},
  Intl: Intl,
  Date: Date,
  JSON: JSON,
  String: String,
  Math: Math,
  parseInt: parseInt,
  Promise: Promise,
  alert: function () {{}},
}};

vm.runInNewContext(fs.readFileSync("{APP_JS}", "utf8"), context);
elements["analyze-form"].handler({{ preventDefault: function () {{}} }});

setTimeout(function () {{
  if (!elements["error-message"].textContent.includes("HTTP 502")) {{
    throw new Error("unexpected error message: " + elements["error-message"].textContent);
  }}
}}, 0);
"""
    result = subprocess.run(["node", "-e", script], check=False, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
