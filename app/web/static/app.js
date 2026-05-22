(function () {
  var form = document.getElementById("analyze-form");
  var loading = document.getElementById("loading");
  var errorSection = document.getElementById("error-section");
  var errorMessage = document.getElementById("error-message");
  var resultSection = document.getElementById("result-section");
  var submitBtn = document.getElementById("submit-btn");

  var chartInfo = document.getElementById("chart-info");
  var analysisSummary = document.getElementById("analysis-summary");
  var themeAnalysesSection = document.getElementById("theme-analyses-section");
  var themeAnalyses = document.getElementById("theme-analyses");
  var followupSection = document.getElementById("followup-section");
  var followupQuestions = document.getElementById("followup-questions");
  var reportSection = document.getElementById("report-section");
  var reportMarkdown = document.getElementById("report-markdown");

  function hide(element) {
    element.classList.add("hidden");
  }

  function show(element) {
    element.classList.remove("hidden");
  }

  function toISOStringWithOffset(datetimeLocalValue) {
    var parts = datetimeLocalValue.replace("T", " ").split(/[- :]/);
    var dt = new Date(
      parseInt(parts[0]),
      parseInt(parts[1]) - 1,
      parseInt(parts[2]),
      parseInt(parts[3]),
      parseInt(parts[4])
    );
    var tz = document.getElementById("timezone").value.trim();
    var offsetMinutes = getTimezoneOffsetMinutes(tz, dt);
    if (offsetMinutes === null) {
      return datetimeLocalValue + "+08:00";
    }
    var sign = offsetMinutes >= 0 ? "+" : "-";
    var absOffset = Math.abs(offsetMinutes);
    var hours = String(Math.floor(absOffset / 60)).padStart(2, "0");
    var mins = String(absOffset % 60).padStart(2, "0");
    return dt.toISOString().slice(0, 19) + sign + hours + ":" + mins;
  }

  function getTimezoneOffsetMinutes(tz, date) {
    try {
      var formatter = new Intl.DateTimeFormat("en-US", {
        timeZone: tz,
        timeZoneName: "shortOffset",
      });
      var parts = formatter.formatToParts(date);
      var offsetPart = parts.find(function (p) {
        return p.type === "timeZoneName";
      });
      if (!offsetPart) return null;
      var match = offsetPart.value.match(/GMT([+-])(\d{1,2})(?::(\d{2}))?/);
      if (!match) return null;
      var sign = match[1] === "+" ? 1 : -1;
      var h = parseInt(match[2]);
      var m = match[3] ? parseInt(match[3]) : 0;
      return sign * (h * 60 + m);
    } catch (_e) {
      return null;
    }
  }

  function buildPayload() {
    var themes = [];
    document
      .querySelectorAll('input[name="themes"]:checked')
      .forEach(function (cb) {
        themes.push(cb.value);
      });

    return {
      birth: {
        calendar_type: document.getElementById("calendar_type").value,
        birth_datetime: toISOStringWithOffset(
          document.getElementById("birth_datetime").value
        ),
        gender: document.getElementById("gender").value,
        birth_place: document.getElementById("birth_place").value.trim(),
        timezone: document.getElementById("timezone").value.trim(),
      },
      options: {
        themes: themes,
        include_followup_questions:
          document.getElementById("include_followup_questions").checked,
        include_markdown_report:
          document.getElementById("include_markdown_report").checked,
      },
    };
  }

  function renderResult(data) {
    var chart = data.chart || {};
    chartInfo.textContent =
      "Chart ID: " +
      (chart.chart_id || "N/A") +
      "\n来源: " +
      (chart.source || "N/A") +
      "\n摘要: " +
      (chart.summary || "N/A");

    var analysis = data.analysis || {};
    analysisSummary.textContent =
      analysis.summary || "无分析结果";

    var themes = analysis.theme_analyses || [];
    if (themes.length > 0) {
      show(themeAnalysesSection);
      themeAnalyses.innerHTML = "";
      themes.forEach(function (t) {
        var div = document.createElement("div");
        div.className = "theme-analysis";
        var h4 = document.createElement("h4");
        h4.textContent = t.theme || "未知主题";
        div.appendChild(h4);
        var pre = document.createElement("pre");
        pre.textContent = JSON.stringify(t, null, 2);
        div.appendChild(pre);
        themeAnalyses.appendChild(div);
      });
    } else {
      hide(themeAnalysesSection);
    }

    var questions = data.followup_questions || [];
    if (questions.length > 0) {
      show(followupSection);
      followupQuestions.innerHTML = "";
      questions.forEach(function (q) {
        var li = document.createElement("li");
        li.textContent =
          q.question +
          (q.reason ? "（原因：" + q.reason + "）" : "");
        followupQuestions.appendChild(li);
      });
    } else {
      hide(followupSection);
    }

    if (data.report_markdown) {
      show(reportSection);
      reportMarkdown.textContent = data.report_markdown;
    } else {
      hide(reportSection);
    }

    show(resultSection);
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    var calendarType = document.getElementById("calendar_type").value;
    if (calendarType === "lunar") {
      alert("当前阶段不支持农历排盘，请选择公历。");
      return;
    }

    hide(errorSection);
    hide(resultSection);
    show(loading);
    submitBtn.disabled = true;

    var payload = buildPayload();

    fetch("/api/v1/ziwei/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok, status: response.status, data: data };
        });
      })
      .then(function (result) {
        hide(loading);
        submitBtn.disabled = false;

        if (!result.ok) {
          var err =
            result.data.detail
              ? JSON.stringify(result.data.detail, null, 2)
              : JSON.stringify(result.data, null, 2);
          errorMessage.textContent = err;
          show(errorSection);
          return;
        }

        renderResult(result.data);
      })
      .catch(function (err) {
        hide(loading);
        submitBtn.disabled = false;
        errorMessage.textContent = "请求失败: " + err.message;
        show(errorSection);
      });
  });
})();
