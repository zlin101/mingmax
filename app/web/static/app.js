(function () {
  var form = document.getElementById("analyze-form");
  var loading = document.getElementById("loading");
  var errorSection = document.getElementById("error-section");
  var errorMessage = document.getElementById("error-message");
  var resultSection = document.getElementById("result-section");
  var submitBtn = document.getElementById("submit-btn");
  var sourceNotice = document.getElementById("source-notice");
  var sourceText = document.getElementById("source-text");

  var birthPlaceInput = document.getElementById("birth_place");
  var longitudeInput = document.getElementById("longitude");

  var CITY_LONGITUDES = {
    "北京": 116.407,
    "上海": 121.474,
    "广州": 113.264,
    "深圳": 114.058,
    "成都": 104.067,
    "重庆": 106.552,
    "杭州": 120.155,
    "武汉": 114.305,
    "南京": 118.797,
    "天津": 117.190,
    "苏州": 120.619,
    "西安": 108.940,
    "长沙": 112.938,
    "沈阳": 123.432,
    "青岛": 120.383,
    "郑州": 113.625,
    "大连": 121.615,
    "东莞": 113.752,
    "宁波": 121.544,
    "厦门": 118.089,
    "福州": 119.296,
    "无锡": 120.312,
    "合肥": 117.227,
    "昆明": 102.833,
    "哈尔滨": 126.535,
    "济南": 117.001,
    "佛山": 113.122,
    "长春": 125.325,
    "温州": 120.700,
    "石家庄": 114.515,
    "南宁": 108.320,
    "贵阳": 106.630,
    "南昌": 115.858,
    "太原": 112.549,
    "乌鲁木齐": 87.617,
    "拉萨": 91.132,
    "呼和浩特": 111.671,
    "兰州": 103.834,
    "银川": 106.278,
    "西宁": 101.778,
    "海口": 110.350,
    "三亚": 109.508,
    "香港": 114.169,
    "台北": 121.565,
    "澳门": 113.544,
    "常州": 119.974,
    "徐州": 117.185,
    "烟台": 121.391,
    "洛阳": 112.454,
    "珠海": 113.553,
    "中山": 113.393,
    "惠州": 114.412,
    "保定": 115.465,
    "台州": 121.421,
    "南通": 120.865,
    "嘉兴": 120.756,
    "金华": 119.650,
    "绍兴": 120.581,
    "潍坊": 119.107,
    "扬州": 119.413,
    "赣州": 114.933,
    "桂林": 110.299,
    "柳州": 109.412,
    "大理": 100.225,
    "丽江": 100.233,
    "泉州": 118.676,
    "漳州": 117.647,
    "宜昌": 111.287,
    "襄阳": 112.144,
    "株洲": 113.134,
    "岳阳": 113.129,
    "衡阳": 112.572,
    "遵义": 106.937,
    "绵阳": 104.682,
    "宜宾": 104.641,
    "泸州": 105.442,
    "曲靖": 103.796,
    "齐齐哈尔": 123.953,
    "吉林": 126.550,
    "鞍山": 122.996,
    "抚顺": 123.961,
    "牡丹江": 129.632,
    "秦皇岛": 119.586,
    "唐山": 118.175,
    "邯郸": 114.491,
    "廊坊": 116.684,
    "沧州": 116.839,
    "泰安": 117.089,
    "临沂": 118.356,
    "德州": 116.359,
    "聊城": 115.985,
    "菏泽": 115.480,
    "滨州": 117.972,
    "枣庄": 117.324,
    "日照": 119.461,
    "威海": 122.120,
    "东营": 118.675,
    "拉萨": 91.132,
    "喀什": 75.990,
    "伊犁": 81.324,
    "阿克苏": 80.265,
    "吐鲁番": 89.184,
    "敦煌": 94.662,
    "兰州": 103.834,
    "天水": 105.725,
    "酒泉": 98.494,
  };

  function autofillLongitude() {
    var place = birthPlaceInput.value.trim();
    if (!place) return;
    for (var city in CITY_LONGITUDES) {
      if (place.indexOf(city) !== -1 || city.indexOf(place) !== -1) {
        longitudeInput.value = CITY_LONGITUDES[city];
        return;
      }
    }
  }

  birthPlaceInput.addEventListener("input", autofillLongitude);
  birthPlaceInput.addEventListener("change", autofillLongitude);
  birthPlaceInput.addEventListener("blur", autofillLongitude);

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
      parseInt(parts[0], 10),
      parseInt(parts[1], 10) - 1,
      parseInt(parts[2], 10),
      parseInt(parts[3], 10),
      parseInt(parts[4], 10)
    );
    var tz = document.getElementById("timezone").value.trim();
    var offsetMinutes = getTimezoneOffsetMinutes(tz, dt);
    if (offsetMinutes === null) {
      return datetimeLocalValue + ":00+08:00";
    }
    var sign = offsetMinutes >= 0 ? "+" : "-";
    var absOffset = Math.abs(offsetMinutes);
    var hours = String(Math.floor(absOffset / 60)).padStart(2, "0");
    var mins = String(absOffset % 60).padStart(2, "0");
    return datetimeLocalValue + ":00" + sign + hours + ":" + mins;
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
      var h = parseInt(match[2], 10);
      var m = match[3] ? parseInt(match[3], 10) : 0;
      return sign * (h * 60 + m);
    } catch (_e) {
      return null;
    }
  }

  function parseResponse(response) {
    return response.json().catch(function () {
      return response.text().then(function (text) {
        return {
          error: {
            code: "HTTP_" + response.status,
            message: "HTTP " + response.status + (text ? ": " + text : ""),
            details: [],
          },
        };
      });
    });
  }

  function buildPayload() {
    var themes = [];
    document
      .querySelectorAll('input[name="themes"]:checked')
      .forEach(function (cb) {
        themes.push(cb.value);
      });

    var longitudeEl = document.getElementById("longitude");
    var longitude = longitudeEl.value.trim() ? parseFloat(longitudeEl.value) : undefined;

    return {
      birth: {
        calendar_type: document.getElementById("calendar_type").value,
        birth_datetime: toISOStringWithOffset(
          document.getElementById("birth_datetime").value
        ),
        gender: document.getElementById("gender").value,
        birth_place: document.getElementById("birth_place").value.trim(),
        longitude: longitude,
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
    var source = chart.source || "unknown";

    sourceNotice.className = source === "stub" ? "stub-notice" : "source-notice";
    if (source === "stub") {
      sourceText.textContent = "当前排盘结果为 stub 数据，仅用于验证分析流程，不代表真实紫微排盘已完成。";
    } else {
      sourceText.textContent = source;
    }
    show(sourceNotice);

    chartInfo.textContent =
      "Chart ID: " +
      (chart.chart_id || "N/A") +
      "\n来源: " +
      source +
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
        return parseResponse(response).then(function (data) {
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
