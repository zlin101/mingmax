import subprocess
from pathlib import Path

from httpx import AsyncClient

APP_JS = Path("app/web/static/app.js")
TASKS_MD = Path(__file__).resolve().parent.parent / ".supports" / "TASKS.md"


def _run_app_js(script_body: str) -> None:
    script = """
const fs = require("fs");
const vm = require("vm");

function makeElement(value) {
  return {
    value: value || "",
    checked: false,
    disabled: false,
    innerHTML: "",
    textContent: "",
    className: "",
    classList: {
      add: function () {},
      remove: function () {},
    },
    appendChild: function () {},
    addEventListener: function (_event, handler) {
      this.handler = handler;
    },
  };
}

const elements = {
  "analyze-form": makeElement(),
  "loading": makeElement(),
  "error-section": makeElement(),
  "error-message": makeElement(),
  "result-section": makeElement(),
  "submit-btn": makeElement(),
  "source-notice": makeElement(),
  "source-text": makeElement(),
  "chart-info": makeElement(),
  "analysis-summary": makeElement(),
  "theme-analyses-section": makeElement(),
  "theme-analyses": makeElement(),
  "followup-section": makeElement(),
  "followup-questions": makeElement(),
  "report-section": makeElement(),
  "report-markdown": makeElement(),
  "calendar_type": makeElement("solar"),
  "birth_datetime": makeElement("1995-05-17T08:30"),
  "gender": makeElement("female"),
  "birth_place": makeElement("Shanghai, China"),
  "longitude": makeElement(""),
  "timezone": makeElement("Asia/Shanghai"),
  "include_followup_questions": makeElement(),
  "include_markdown_report": makeElement(),
};
elements["include_followup_questions"].checked = true;
elements["include_markdown_report"].checked = true;

const context = {
  document: {
    getElementById: function (id) {
      return elements[id];
    },
    querySelectorAll: function () {
      return [];
    },
    createElement: function () {
      return makeElement();
    },
  },
  Intl: Intl,
  Date: Date,
  JSON: JSON,
  String: String,
  Math: Math,
  parseInt: parseInt,
  Promise: Promise,
  alert: function () {},
  fetch: function () {
    throw new Error("fetch not configured");
  },
};

vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), context);
""" + script_body
    result = subprocess.run(["node", "-e", script, str(APP_JS)], check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


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


async def test_index_html_marks_unknown_gender_as_unsupported(client: AsyncClient) -> None:
    response = await client.get("/static/index.html")
    assert response.status_code == 200
    assert '<option value="unknown" disabled>' in response.text
    assert "真实排盘暂不支持" in response.text


def test_frontend_preserves_local_birth_time_when_building_payload() -> None:
    _run_app_js("""
let capturedPayload = null;
context.fetch = function (_url, options) {
  capturedPayload = JSON.parse(options.body);
  return Promise.resolve({
    ok: true,
    status: 200,
    json: function () {
      return Promise.resolve({
        chart: { source: "iztro_py" },
        analysis: {},
        followup_questions: [],
        report_markdown: null,
      });
    },
  });
};

elements["analyze-form"].handler({ preventDefault: function () {} });
setTimeout(function () {
  if (capturedPayload.birth.birth_datetime !== "1995-05-17T08:30:00+08:00") {
    throw new Error("unexpected birth_datetime: " + capturedPayload.birth.birth_datetime);
  }
}, 0);
""")


def test_frontend_has_dynamic_source_display() -> None:
    _run_app_js("""
context.fetch = function () {
  return Promise.resolve({
    ok: true,
    status: 200,
    json: function () {
      return Promise.resolve({
        chart: { source: "iztro_py", chart_id: "chart-1", summary: "summary" },
        analysis: {},
        followup_questions: [],
        report_markdown: null,
      });
    },
  });
};

elements["analyze-form"].handler({ preventDefault: function () {} });
setTimeout(function () {
  if (elements["source-notice"].className !== "source-notice") {
    throw new Error("unexpected source notice class: " + elements["source-notice"].className);
  }
  if (elements["source-text"].textContent !== "iztro_py") {
    throw new Error("unexpected source text: " + elements["source-text"].textContent);
  }
}, 0);
""")


def test_frontend_reports_non_json_http_errors_with_status() -> None:
    _run_app_js("""
context.fetch = function () {
  return Promise.resolve({
    ok: false,
    status: 502,
    json: function () {
      return Promise.reject(new Error("invalid json"));
    },
    text: function () {
      return Promise.resolve("Bad Gateway");
    },
  });
};

elements["analyze-form"].handler({ preventDefault: function () {} });
setTimeout(function () {
  if (!elements["error-message"].textContent.includes("HTTP 502")) {
    throw new Error("unexpected error message: " + elements["error-message"].textContent);
  }
}, 0);
""")


def test_tasks_document_uses_actual_static_frontend_branch_name() -> None:
    content = TASKS_MD.read_text(encoding="utf-8")
    assert "第一阶段拆分为 8 个可独立 review 和验收的分支" in content
