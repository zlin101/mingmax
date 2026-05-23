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
  var el = {
    value: value || "",
    checked: false,
    disabled: false,
    innerHTML: "",
    className: "",
    classList: {
      add: function () {
        for (var i = 0; i < arguments.length; i++) {
          if (!this.contains(arguments[i])) {
            el.className = el.className ? el.className + " " + arguments[i] : arguments[i];
          }
        }
      },
      remove: function () {
        for (var i = 0; i < arguments.length; i++) {
          var cls = arguments[i];
          var parts = el.className.split(" ");
          el.className = parts.filter(function (c) { return c && c !== cls; }).join(" ");
        }
      },
      contains: function (c) {
        return (" " + el.className + " ").indexOf(" " + c + " ") >= 0;
      },
    },
    _children: [],
    appendChild: function (child) {
      if (child && child._isFragment) {
        for (var i = 0; i < child._children.length; i++) {
          this._children.push(child._children[i]);
        }
      } else {
        this._children.push(child);
      }
    },
    _handlers: {},
    addEventListener: function (event, handler) {
      this._handlers[event] = handler;
      this.handler = handler;
    },
    setAttribute: function (name, value) {
      this["attr_" + name] = value;
    },
    getAttribute: function (name) {
      return this["attr_" + name];
    },
    style: {},
    querySelectorAll: function (selector) {
      if (selector && selector.charAt(0) === ".") {
        var cn = selector.slice(1);
        return this._children.filter(function (c) {
          return c && c.classList && c.classList.contains(cn);
        });
      }
      return [];
    },
  };
  Object.defineProperty(el, 'textContent', {
    get: function() { return this._tc !== undefined ? this._tc : ""; },
    set: function(v) { this._tc = v; if (v === "") this._children = []; },
    configurable: true
  });
  return el;
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
  "chart-grid": makeElement(),
  "chart-summary": makeElement(),
  "palace-detail": makeElement(),
  "palace-detail-content": makeElement(),
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
    createDocumentFragment: function () {
      var el = makeElement();
      el._isFragment = true;
      return el;
    },
    createTextNode: function (text) {
      var node = { _tc: text, _children: [], _isText: true };
      return node;
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


def test_frontend_autofills_longitude_from_city() -> None:
    _run_app_js("""
  elements["birth_place"].value = "广州";
  elements["birth_place"]._handlers["input"]();
  if (Number(elements["longitude"].value) !== 113.264) {
    throw new Error("expected longitude 113.264 for 广州, got: " + elements["longitude"].value);
  }
  """)


def test_frontend_autofills_longitude_partial_match() -> None:
    _run_app_js("""
  elements["birth_place"].value = "广州市天河区";
  elements["birth_place"]._handlers["input"]();
  if (Number(elements["longitude"].value) !== 113.264) {
    throw new Error("expected longitude 113.264 for partial match, got: " + elements["longitude"].value);
  }
  """)


def test_frontend_no_autofill_for_unknown_city() -> None:
    _run_app_js("""
elements["birth_place"].value = "某个不存在的城市";
elements["birth_place"]._handlers["input"]();
if (elements["longitude"].value !== "" && elements["longitude"].value !== undefined) {
  throw new Error("expected empty longitude for unknown city, got: " + elements["longitude"].value);
}
""")


# --- Chart verification view tests ---


async def test_index_html_has_chart_verification_section(client: AsyncClient) -> None:
    response = await client.get("/static/index.html")
    assert response.status_code == 200
    body = response.text
    assert "chart-verification" in body
    assert "chart-summary" in body
    assert "chart-grid" in body
    assert "palace-detail" in body
    assert "palace-detail-content" in body


async def test_index_html_chart_grid_before_analysis_summary(client: AsyncClient) -> None:
    response = await client.get("/static/index.html")
    body = response.text
    verify_pos = body.index("chart-verification")
    summary_pos = body.index('id="analysis-summary"')
    assert verify_pos < summary_pos


def _chart_response() -> dict:
    return {
        "chart": {
            "source": "iztro_py",
            "chart_id": "test-chart-001",
            "ming_palace_index": 11,
            "body_palace_index": 7,
            "five_elements_class": None,
            "lunar_info": None,
            "palaces": [
                {
                    "index": 0,
                    "name": "父母宫",
                    "heavenly_stem": "甲",
                    "earthly_branch": "寅",
                    "stars": [{"name": "天梁", "brightness": "庙", "category": "major"}],
                    "four_hua": None,
                    "is_body_palace": False,
                    "opposite_palace_index": 6,
                    "san_fang_si_zheng_indexes": [0, 4, 6, 8],
                    "is_empty": False,
                    "borrowed_from_index": None,
                    "borrowed_major_stars": None,
                },
                {
                    "index": 3,
                    "name": "官禄宫",
                    "heavenly_stem": "丁",
                    "earthly_branch": "巳",
                    "stars": [],
                    "four_hua": None,
                    "is_body_palace": False,
                    "opposite_palace_index": 9,
                    "san_fang_si_zheng_indexes": [3, 7, 9, 11],
                    "is_empty": True,
                    "borrowed_from_index": 9,
                    "borrowed_major_stars": ["太阳"],
                },
                {
                    "index": 7,
                    "name": "财帛宫",
                    "heavenly_stem": "辛",
                    "earthly_branch": "酉",
                    "stars": [
                        {"name": "紫微", "brightness": "旺", "category": "major"},
                        {"name": "天府", "brightness": "庙", "category": "major"},
                        {"name": "左辅", "brightness": None, "category": "minor"},
                    ],
                    "four_hua": {"hua_lu": "紫微", "hua_quan": None, "hua_ke": None, "hua_ji": None},
                    "is_body_palace": True,
                    "opposite_palace_index": 1,
                    "san_fang_si_zheng_indexes": [3, 7, 9, 11],
                    "is_empty": False,
                    "borrowed_from_index": None,
                    "borrowed_major_stars": None,
                },
                {
                    "index": 11,
                    "name": "命宫",
                    "heavenly_stem": "乙",
                    "earthly_branch": "丑",
                    "stars": [
                        {"name": "天机", "brightness": "利", "category": "major"},
                        {"name": "文昌", "brightness": None, "category": "minor"},
                    ],
                    "four_hua": {"hua_lu": None, "hua_quan": None, "hua_ke": None, "hua_ji": "天机"},
                    "is_body_palace": False,
                    "opposite_palace_index": 5,
                    "san_fang_si_zheng_indexes": [3, 7, 9, 11],
                    "is_empty": False,
                    "borrowed_from_index": None,
                    "borrowed_major_stars": None,
                },
            ],
            "four_hua": {"hua_lu": "紫微", "hua_quan": "太阴", "hua_ke": "右弼", "hua_ji": "天机"},
        },
        "analysis": {
            "summary": "test",
            "strong_signals": [],
            "weak_hypotheses": [],
            "cross_checks": [],
            "theme_analyses": [],
        },
        "followup_questions": [],
        "report_markdown": None,
    }


def _setup_fetch_with_chart() -> str:
    import json

    data = _chart_response()
    return (
        "context.fetch = function () {"
        "  return Promise.resolve({"
        "    ok: true,"
        "    status: 200,"
        "    json: function () { return Promise.resolve(" + json.dumps(data) + "); }"
        "  });"
        "};"
    )


def test_frontend_renders_palaces_in_grid() -> None:
    _run_app_js(
        _setup_fetch_with_chart()
        + """
    elements["analyze-form"].handler({ preventDefault: function () {} });
    """
        + """
    setTimeout(function () {
      var grid = elements["chart-grid"];
      if (!grid._children || grid._children.length === 0) {
        throw new Error("chart-grid has no children");
      }
      var cells = grid._children.filter(function (c) {
        return c && c.classList && c.classList.contains("palace-cell");
      });
      if (cells.length !== 12) {
        throw new Error("expected 12 palace cells, got " + cells.length);
      }
    }, 0);
    """
    )


def test_frontend_renders_center_cell() -> None:
    _run_app_js(
        _setup_fetch_with_chart()
        + """
    elements["analyze-form"].handler({ preventDefault: function () {} });
    """
        + """
    setTimeout(function () {
      var grid = elements["chart-grid"];
      var centers = grid._children.filter(function (c) {
        return c && c.classList && c.classList.contains("center-cell");
      });
      if (centers.length !== 1) {
        throw new Error("expected 1 center cell, got " + centers.length);
      }
    }, 0);
    """
    )


def test_frontend_renders_ming_body_badges() -> None:
    _run_app_js(
        _setup_fetch_with_chart()
        + """
    elements["analyze-form"].handler({ preventDefault: function () {} });
    """
        + """
    setTimeout(function () {
      var grid = elements["chart-grid"];
      var cells = grid.querySelectorAll(".palace-cell");
      var mingCell = null;
      var bodyCell = null;
      for (var i = 0; i < cells.length; i++) {
        var idx = cells[i].getAttribute("data-index");
        if (idx === "11") mingCell = cells[i];
        if (idx === "7") bodyCell = cells[i];
      }
      if (!mingCell) throw new Error("ming palace cell not found");
      if (!bodyCell) throw new Error("body palace cell not found");
      var hasMingBadge = mingCell._children.some(function (c) {
        return c && c.classList && c.classList.contains("badge-ming");
      });
      if (!hasMingBadge) throw new Error("ming badge not found on index 11");
      var hasBodyBadge = bodyCell._children.some(function (c) {
        return c && c.classList && c.classList.contains("badge-body");
      });
      if (!hasBodyBadge) throw new Error("body badge not found on index 7");
    }, 0);
    """
    )


def test_frontend_renders_four_hua_badges() -> None:
    _run_app_js(
        _setup_fetch_with_chart()
        + """
    elements["analyze-form"].handler({ preventDefault: function () {} });
    """
        + """
    setTimeout(function () {
      var grid = elements["chart-grid"];
      var cells = grid.querySelectorAll(".palace-cell");
      var huaLuCell = null;
      var huaJiCell = null;
      for (var i = 0; i < cells.length; i++) {
        var idx = cells[i].getAttribute("data-index");
        if (idx === "7") huaLuCell = cells[i];
        if (idx === "11") huaJiCell = cells[i];
      }
      var hasLuBadge = huaLuCell._children.some(function (c) {
        return c && c.classList && c.classList.contains("badge-hua-lu");
      });
      if (!hasLuBadge) throw new Error("hua-lu badge not found on index 7");
      var hasJiBadge = huaJiCell._children.some(function (c) {
        return c && c.classList && c.classList.contains("badge-hua-ji");
      });
      if (!hasJiBadge) throw new Error("hua-ji badge not found on index 11");
    }, 0);
    """
    )


def test_frontend_renders_empty_borrowed_badges() -> None:
    _run_app_js(
        _setup_fetch_with_chart()
        + """
    elements["analyze-form"].handler({ preventDefault: function () {} });
    """
        + """
    setTimeout(function () {
      var grid = elements["chart-grid"];
      var cells = grid.querySelectorAll(".palace-cell");
      var emptyCell = null;
      for (var i = 0; i < cells.length; i++) {
        if (cells[i].getAttribute("data-index") === "3") emptyCell = cells[i];
      }
      if (!emptyCell) throw new Error("empty palace cell (index 3) not found");
      var hasEmptyBadge = emptyCell._children.some(function (c) {
        return c && c.classList && c.classList.contains("badge-empty");
      });
      if (!hasEmptyBadge) throw new Error("empty badge not found on index 3");
      var hasBorrowedBadge = emptyCell._children.some(function (c) {
        return c && c.classList && c.classList.contains("badge-borrowed");
      });
      if (!hasBorrowedBadge) throw new Error("borrowed badge not found on index 3");
    }, 0);
    """
    )


def test_frontend_shows_unavailable_for_missing_fields() -> None:
    _run_app_js(
        _setup_fetch_with_chart()
        + """
    elements["analyze-form"].handler({ preventDefault: function () {} });
    """
        + """
    setTimeout(function () {
      function collectText(el) {
        var parts = [];
        if (el._tc) parts.push(el._tc);
        for (var i = 0; i < el._children.length; i++) {
          parts.push(collectText(el._children[i]));
        }
        return parts.join(" ");
      }
      var text = collectText(elements["chart-summary"]);
      if (text.indexOf("暂未提供") < 0) {
        throw new Error("expected '暂未提供' in chart summary, got: " + text);
      }
    }, 0);
    """
    )


def test_frontend_detail_panel_on_palace_click() -> None:
    _run_app_js(
        _setup_fetch_with_chart()
        + """
    elements["analyze-form"].handler({ preventDefault: function () {} });
    """
        + """
    setTimeout(function () {
      function collectText(el) {
        var parts = [];
        if (el._tc) parts.push(el._tc);
        for (var i = 0; i < el._children.length; i++) {
          parts.push(collectText(el._children[i]));
        }
        return parts.join(" ");
      }
      var grid = elements["chart-grid"];
      var cells = grid.querySelectorAll(".palace-cell");
      var mingCell = null;
      for (var i = 0; i < cells.length; i++) {
        if (cells[i].getAttribute("data-index") === "11") mingCell = cells[i];
      }
      if (!mingCell) throw new Error("ming cell not found");
      mingCell._handlers.click({ currentTarget: mingCell });
      var text = collectText(elements["palace-detail-content"]);
      if (text.indexOf("命宫") < 0) {
        throw new Error("expected '命宫' in detail, got: " + text);
      }
      if (text.indexOf("天机") < 0) {
        throw new Error("expected star '天机' in detail, got: " + text);
      }
      if (text.indexOf("对宫") < 0) {
        throw new Error("expected opposite palace info in detail, got: " + text);
      }
    }, 0);
    """
    )


def test_frontend_no_localStorage_sessionStorage_writes() -> None:
    js_code = (Path("app/web/static/app.js")).read_text(encoding="utf-8")
    forbidden = ["localStorage", "sessionStorage", "cookie"]
    for term in forbidden:
        assert term not in js_code, f"Forbidden storage API found in app.js: {term}"


def test_frontend_xss_safe_star_name_rendering() -> None:
    """Malicious chart field content must appear as text, not interpreted as HTML."""
    import json

    malicious = '<img src=x onerror="alert(1)">'
    data = _chart_response()
    # Inject malicious content into star name, palace name, and chart source
    data["chart"]["palaces"][0]["stars"][0]["name"] = malicious
    data["chart"]["palaces"][0]["name"] = malicious
    data["chart"]["source"] = malicious

    _run_app_js(
        "context.fetch = function () {"
        "  return Promise.resolve({"
        "    ok: true,"
        "    status: 200,"
        "    json: function () { return Promise.resolve(" + json.dumps(data) + "); }"
        "  });"
        "};"
        + """
    function collectText(el) {
      var parts = [];
      if (el._tc) parts.push(el._tc);
      for (var i = 0; i < el._children.length; i++) {
        parts.push(collectText(el._children[i]));
      }
      return parts.join(" ");
    }
    elements["analyze-form"].handler({ preventDefault: function () {} });
    setTimeout(function () {
      // Star name in palace cell must appear as text, not as HTML element
      var grid = elements["chart-grid"];
      var cells = grid.querySelectorAll(".palace-cell");
      var targetCell = null;
      for (var i = 0; i < cells.length; i++) {
        if (cells[i].getAttribute("data-index") === "0") targetCell = cells[i];
      }
      if (!targetCell) throw new Error("cell index 0 not found");
      var cellText = collectText(targetCell);
      if (cellText.indexOf('"""
        + malicious
        + """') < 0) {
        throw new Error("expected malicious star name as text in cell, got: " + cellText);
      }
      // innerHTML must NOT contain the raw <img tag (it stays as textContent)
      var cellInner = targetCell.innerHTML;
      if (cellInner && cellInner.indexOf("<img") >= 0) {
        throw new Error("XSS: innerHTML contains raw <img tag");
      }

      // Chart summary must also show source as text
      var summaryText = collectText(elements["chart-summary"]);
      if (summaryText.indexOf('"""
        + malicious
        + """') < 0) {
        throw new Error("expected malicious source as text in summary, got: " + summaryText);
      }

      // Palace detail panel must show palace name and star as text
      targetCell._handlers.click({ currentTarget: targetCell });
      var detailText = collectText(elements["palace-detail-content"]);
      if (detailText.indexOf('"""
        + malicious
        + """') < 0) {
        throw new Error("expected malicious content as text in detail, got: " + detailText);
      }
    }, 0);
    """
    )
