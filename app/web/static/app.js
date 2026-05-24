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
    "成都": 104.066,
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
  var analysisOverview = document.getElementById("analysis-overview");
  var analysisStrongSignals = document.getElementById("analysis-strong-signals");
  var analysisWeakHypotheses = document.getElementById("analysis-weak-hypotheses");
  var analysisCrossChecks = document.getElementById("analysis-cross-checks");
  var themeAnalysesSection = document.getElementById("theme-analyses-section");
  var themeAnalyses = document.getElementById("theme-analyses");
  var followupSection = document.getElementById("followup-section");
  var followupQuestions = document.getElementById("followup-questions");
  var reportSection = document.getElementById("report-section");
  var reportMarkdown = document.getElementById("report-markdown");

  var chartGrid = document.getElementById("chart-grid");
  var chartSummary = document.getElementById("chart-summary");
  var palaceDetail = document.getElementById("palace-detail");
  var palaceDetailContent = document.getElementById("palace-detail-content");

  // iztro palace index to earthly branch grid position (1-based CSS grid)
  // index 0=寅..11=丑, arranged clockwise around a 4x4 grid
  var INDEX_TO_GRID = [
    { row: 4, col: 1 }, // 0: 寅
    { row: 3, col: 1 }, // 1: 卯
    { row: 2, col: 1 }, // 2: 辰
    { row: 1, col: 1 }, // 3: 巳
    { row: 1, col: 2 }, // 4: 午
    { row: 1, col: 3 }, // 5: 未
    { row: 1, col: 4 }, // 6: 申
    { row: 2, col: 4 }, // 7: 酉
    { row: 3, col: 4 }, // 8: 戌
    { row: 4, col: 4 }, // 9: 亥
    { row: 4, col: 3 }, // 10: 子
    { row: 4, col: 2 }, // 11: 丑
  ];

  var currentChart = null;

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

  function _addSummaryItem(container, label, value) {
    var span = document.createElement("span");
    span.className = "summary-item";
    var labelEl = document.createElement("span");
    labelEl.className = "summary-label";
    labelEl.textContent = label;
    span.appendChild(labelEl);
    var valueEl = document.createElement("span");
    valueEl.className = "summary-value";
    valueEl.textContent = value;
    span.appendChild(valueEl);
    container.appendChild(span);
  }

  function renderChartSummary(chart) {
    chartSummary.textContent = "";

    _addSummaryItem(chartSummary, "来源：", chart.source || "N/A");
    _addSummaryItem(chartSummary, "Chart ID：", chart.chart_id || "N/A");

    var palaces = chart.palaces || [];
    var palaceByIndex = {};
    for (var i = 0; i < palaces.length; i++) {
      palaceByIndex[palaces[i].index] = palaces[i];
    }

    var mingPalace = chart.ming_palace_index != null ? palaceByIndex[chart.ming_palace_index] : null;
    var bodyPalace = chart.body_palace_index != null ? palaceByIndex[chart.body_palace_index] : null;

    _addSummaryItem(chartSummary, "命宫：", mingPalace ? mingPalace.name + "（" + (mingPalace.earthly_branch || "") + "）" : "N/A");
    _addSummaryItem(chartSummary, "身宫：", bodyPalace ? bodyPalace.name + "（" + (bodyPalace.earthly_branch || "") + "）" : "N/A");

    var meta = chart.metadata || {};
    _addSummaryItem(chartSummary, "五行局：", chart.five_elements_class || meta.five_elements_class || "暂未提供");
    _addSummaryItem(chartSummary, "农历：", meta.lunar_date || "暂未提供");
    _addSummaryItem(chartSummary, "四柱背景：", meta.chinese_date || "暂未提供");

    if (chart.current_age != null) {
      _addSummaryItem(chartSummary, "当前虚岁：", String(chart.current_age));
    }
    if (chart.current_decadal) {
      var cd = chart.current_decadal;
      _addSummaryItem(chartSummary, "当前大限：", cd.start_age + "-" + cd.end_age + " " + (cd.palace_name || ""));
    }
  }

  function renderChartGrid(chart) {
    chartGrid.textContent = "";
    currentChart = chart;
    hide(palaceDetail);

    var palaces = chart.palaces || [];
    var palaceByIndex = {};
    for (var i = 0; i < palaces.length; i++) {
      palaceByIndex[palaces[i].index] = palaces[i];
    }

    var decadalPalaceIdx = chart.current_decadal ? chart.current_decadal.palace_index : null;

    for (var idx = 0; idx < 12; idx++) {
      var pos = INDEX_TO_GRID[idx];
      var palace = palaceByIndex[idx];
      var cell = document.createElement("div");
      cell.className = "palace-cell";
      if (idx === decadalPalaceIdx) {
        cell.classList.add("is-current-decadal");
      }
      cell.setAttribute("tabindex", "0");
      cell.setAttribute("data-index", String(idx));
      cell.style.gridRow = String(pos.row);
      cell.style.gridColumn = String(pos.col);

      if (palace) {
        cell.appendChild(buildPalaceCellContent(palace));
      }

      cell.addEventListener("click", onPalaceClick);
      cell.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          this.click();
        }
      });

      chartGrid.appendChild(cell);
    }

    var center = document.createElement("div");
    center.className = "center-cell";
    var titleEl = document.createElement("div");
    titleEl.className = "center-title";
    titleEl.textContent = "mingmax";
    center.appendChild(titleEl);

    var meta = chart.metadata || {};
    var unavailable = "暂未提供";
    var infoLines = ["紫微斗数命盘"];
    var fiveElements = chart.five_elements_class || meta.five_elements_class || unavailable;
    infoLines.push("五行局: " + fiveElements);
    infoLines.push("农历: " + (meta.lunar_date || unavailable));
    infoLines.push("四柱背景: " + (meta.chinese_date || unavailable));

    var mingPalace = palaceByIndex[chart.ming_palace_index];
    var bodyPalace = palaceByIndex[chart.body_palace_index];
    infoLines.push("命宫: " + (mingPalace ? mingPalace.name : unavailable));
    infoLines.push("身宫: " + (bodyPalace ? bodyPalace.name : unavailable));

    infoLines.push("虚岁: " + (chart.current_age != null ? chart.current_age : unavailable));
    if (chart.current_decadal) {
      var cd = chart.current_decadal;
      infoLines.push("大限: " + cd.start_age + "-" + cd.end_age + " " + (cd.palace_name || ""));
    } else {
      infoLines.push("大限: " + unavailable);
    }

    for (var i = 0; i < infoLines.length; i++) {
      var lineEl = document.createElement("div");
      lineEl.className = "center-line";
      lineEl.textContent = infoLines[i];
      center.appendChild(lineEl);
    }

    chartGrid.appendChild(center);
  }

  function buildPalaceCellContent(palace) {
    var frag = document.createDocumentFragment();

    var nameEl = document.createElement("div");
    nameEl.className = "palace-name";
    nameEl.textContent = palace.name;
    frag.appendChild(nameEl);

    var branch = (palace.heavenly_stem || "") + (palace.earthly_branch || "");
    if (branch) {
      var branchEl = document.createElement("div");
      branchEl.className = "palace-branch";
      branchEl.textContent = branch;
      frag.appendChild(branchEl);
    }

    if (palace.name === "命宫") {
      var b = document.createElement("span");
      b.className = "badge badge-ming";
      b.textContent = "命";
      frag.appendChild(b);
    }
    if (palace.is_body_palace) {
      var b = document.createElement("span");
      b.className = "badge badge-body";
      b.textContent = "身";
      frag.appendChild(b);
    }

    var stars = palace.stars || [];
    var majors = [];
    var minorCount = 0;
    for (var i = 0; i < stars.length; i++) {
      if (stars[i].category === "major") majors.push(stars[i]);
      else minorCount++;
    }

    var starsEl = document.createElement("div");
    starsEl.className = "stars";
    for (var i = 0; i < majors.length; i++) {
      var span = document.createElement("span");
      span.className = "star-name";
      span.textContent = majors[i].name;
      starsEl.appendChild(span);
    }
    if (minorCount > 0) {
      var span = document.createElement("span");
      span.className = "minor-count";
      span.textContent = "+" + minorCount;
      starsEl.appendChild(span);
    }
    frag.appendChild(starsEl);

    if (palace.four_hua) {
      var fh = palace.four_hua;
      if (fh.hua_lu) { var b = document.createElement("span"); b.className = "badge badge-hua-lu"; b.textContent = "禄"; frag.appendChild(b); }
      if (fh.hua_quan) { var b = document.createElement("span"); b.className = "badge badge-hua-quan"; b.textContent = "权"; frag.appendChild(b); }
      if (fh.hua_ke) { var b = document.createElement("span"); b.className = "badge badge-hua-ke"; b.textContent = "科"; frag.appendChild(b); }
      if (fh.hua_ji) { var b = document.createElement("span"); b.className = "badge badge-hua-ji"; b.textContent = "忌"; frag.appendChild(b); }
    }

    if (palace.is_empty) {
      var b = document.createElement("span");
      b.className = "badge badge-empty";
      b.textContent = "空宫";
      frag.appendChild(b);
    }
    if (palace.borrowed_major_stars && palace.borrowed_major_stars.length > 0) {
      var b = document.createElement("span");
      b.className = "badge badge-borrowed";
      b.textContent = "借星";
      frag.appendChild(b);
    }

    if (palace.decadal && palace.decadal.start_age != null && palace.decadal.end_age != null) {
      var decEl = document.createElement("div");
      decEl.className = "palace-decadal";
      decEl.textContent = palace.decadal.start_age + "-" + palace.decadal.end_age;
      frag.appendChild(decEl);
    }

    return frag;
  }

  function onPalaceClick(e) {
    var cell = e.currentTarget;
    var index = parseInt(cell.getAttribute("data-index"), 10);

    var allCells = chartGrid.querySelectorAll(".palace-cell");
    for (var i = 0; i < allCells.length; i++) {
      allCells[i].classList.remove("selected");
    }
    cell.classList.add("selected");

    if (currentChart) {
      var palaces = currentChart.palaces || [];
      var palace = null;
      for (var i = 0; i < palaces.length; i++) {
        if (palaces[i].index === index) { palace = palaces[i]; break; }
      }
      if (palace) renderPalaceDetail(palace);
    }
  }

  function findPalaceByIndex(index) {
    if (!currentChart) return null;
    var palaces = currentChart.palaces || [];
    for (var i = 0; i < palaces.length; i++) {
      if (palaces[i].index === index) return palaces[i];
    }
    return null;
  }

  function _addDetailRow(container, label, text) {
    var row = document.createElement("div");
    row.className = "detail-row";
    var labelEl = document.createElement("span");
    labelEl.className = "detail-label";
    labelEl.textContent = label;
    row.appendChild(labelEl);
    row.appendChild(document.createTextNode(text));
    container.appendChild(row);
  }

  function addEvidenceTags(container, label, evidenceIds) {
    if (!evidenceIds || evidenceIds.length === 0) return;
    var wrap = document.createElement("div");
    wrap.className = "evidence-tags";
    if (label) {
      var labelEl = document.createElement("span");
      labelEl.className = "evidence-label";
      labelEl.textContent = label;
      wrap.appendChild(labelEl);
    }
    for (var i = 0; i < evidenceIds.length; i++) {
      var tag = document.createElement("span");
      tag.className = "evidence-tag";
      tag.textContent = evidenceIds[i];
      wrap.appendChild(tag);
    }
    container.appendChild(wrap);
  }

  function _addStarsGroup(container, title, stars) {
    var group = document.createElement("div");
    group.className = "detail-stars-group";
    var h5 = document.createElement("h5");
    h5.textContent = title;
    group.appendChild(h5);
    var div = document.createElement("div");
    var names = [];
    for (var i = 0; i < stars.length; i++) {
      var parts = [stars[i].name];
      if (stars[i].brightness) parts.push("（" + stars[i].brightness + "）");
      if (stars[i].scope) parts.push("[" + stars[i].scope + "]");
      names.push(parts.join(""));
    }
    div.textContent = names.length > 0 ? names.join("、") : "无";
    group.appendChild(div);
    container.appendChild(group);
  }

  function renderPalaceDetail(palace) {
    palaceDetailContent.textContent = "";

    _addDetailRow(palaceDetailContent, "宫位：", palace.name + "（index " + palace.index + "）");

    var branch = (palace.heavenly_stem || "") + (palace.earthly_branch || "");
    _addDetailRow(palaceDetailContent, "天干地支：", branch || "暂未提供");

    var stars = palace.stars || [];
    var majors = [];
    var minors = [];
    var adjectives = [];
    var others = [];
    for (var i = 0; i < stars.length; i++) {
      var cat = stars[i].category;
      if (cat === "major") majors.push(stars[i]);
      else if (cat === "minor") minors.push(stars[i]);
      else if (cat === "adjective") adjectives.push(stars[i]);
      else others.push(stars[i]);
    }

    _addStarsGroup(palaceDetailContent, "主星", majors);
    if (minors.length > 0) _addStarsGroup(palaceDetailContent, "辅星", minors);
    if (adjectives.length > 0) _addStarsGroup(palaceDetailContent, "杂曜", adjectives);
    if (others.length > 0) _addStarsGroup(palaceDetailContent, "其他", others);

    if (palace.opposite_palace_index != null) {
      var opp = findPalaceByIndex(palace.opposite_palace_index);
      _addDetailRow(palaceDetailContent, "对宫：", opp ? opp.name + "（index " + opp.index + "）" : "index " + palace.opposite_palace_index);
    }
    if (palace.san_fang_si_zheng_indexes) {
      var names = [];
      for (var i = 0; i < palace.san_fang_si_zheng_indexes.length; i++) {
        var idx = palace.san_fang_si_zheng_indexes[i];
        var p = findPalaceByIndex(idx);
        names.push(p ? p.name : "index " + idx);
      }
      _addDetailRow(palaceDetailContent, "三方四正：", names.join("、"));
    }

    _addDetailRow(palaceDetailContent, "空宫：", palace.is_empty ? "是" : "否");

    if (palace.is_empty && palace.borrowed_from_index != null) {
      var borrowFrom = findPalaceByIndex(palace.borrowed_from_index);
      _addDetailRow(palaceDetailContent, "借星来源：", borrowFrom ? borrowFrom.name + "（index " + borrowFrom.index + "）" : "index " + palace.borrowed_from_index);
    }
    if (palace.borrowed_major_stars && palace.borrowed_major_stars.length > 0) {
      _addDetailRow(palaceDetailContent, "借入主星：", palace.borrowed_major_stars.join("、"));
    }

    if (palace.decadal) {
      var d = palace.decadal;
      var decText = d.start_age + "-" + d.end_age + "岁";
      if (d.heavenly_stem) decText += " " + d.heavenly_stem;
      if (d.earthly_branch) decText += d.earthly_branch;
      _addDetailRow(palaceDetailContent, "大限：", decText);
    }

    if (palace.four_hua) {
      var fh = palace.four_hua;
      var huaList = [];
      if (fh.hua_lu) huaList.push(fh.hua_lu + "化禄");
      if (fh.hua_quan) huaList.push(fh.hua_quan + "化权");
      if (fh.hua_ke) huaList.push(fh.hua_ke + "化科");
      if (fh.hua_ji) huaList.push(fh.hua_ji + "化忌");
      if (huaList.length > 0) {
        _addDetailRow(palaceDetailContent, "本宫四化：", huaList.join("、"));
      }
    }

    show(palaceDetail);
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

    renderChartSummary(chart);
    renderChartGrid(chart);

    chartInfo.textContent =
      "Chart ID: " +
      (chart.chart_id || "N/A") +
      "\n来源: " +
      source +
      "\n摘要: " +
      (chart.summary || "N/A");

    var analysis = data.analysis || {};

    // Structured analysis overview
    analysisOverview.textContent = "";
    var overviewH3 = document.createElement("h3");
    overviewH3.textContent = "分析概览";
    analysisOverview.appendChild(overviewH3);
    var overviewP = document.createElement("p");
    overviewP.textContent = analysis.summary || "无分析结果";
    analysisOverview.appendChild(overviewP);

    // Strong signals
    var strongSignals = analysis.strong_signals || [];
    if (strongSignals.length > 0) {
      show(analysisStrongSignals);
      analysisStrongSignals.textContent = "";
      var h3 = document.createElement("h3");
      h3.textContent = "强信号";
      analysisStrongSignals.appendChild(h3);
      var ul = document.createElement("ul");
      for (var i = 0; i < strongSignals.length; i++) {
        var li = document.createElement("li");
        li.textContent = strongSignals[i];
        ul.appendChild(li);
      }
      analysisStrongSignals.appendChild(ul);
    } else {
      hide(analysisStrongSignals);
    }

    // Weak hypotheses
    var weakHypotheses = analysis.weak_hypotheses || [];
    if (weakHypotheses.length > 0) {
      show(analysisWeakHypotheses);
      analysisWeakHypotheses.textContent = "";
      var h3 = document.createElement("h3");
      h3.textContent = "弱假设";
      analysisWeakHypotheses.appendChild(h3);
      var ul = document.createElement("ul");
      for (var i = 0; i < weakHypotheses.length; i++) {
        var li = document.createElement("li");
        li.textContent = weakHypotheses[i];
        ul.appendChild(li);
      }
      analysisWeakHypotheses.appendChild(ul);
    } else {
      hide(analysisWeakHypotheses);
    }

    // Cross checks
    var crossChecks = analysis.cross_checks || [];
    if (crossChecks.length > 0) {
      show(analysisCrossChecks);
      analysisCrossChecks.textContent = "";
      var h3 = document.createElement("h3");
      h3.textContent = "交叉校验";
      analysisCrossChecks.appendChild(h3);
      var ul = document.createElement("ul");
      for (var i = 0; i < crossChecks.length; i++) {
        var li = document.createElement("li");
        li.textContent = crossChecks[i];
        ul.appendChild(li);
      }
      analysisCrossChecks.appendChild(ul);
    } else {
      hide(analysisCrossChecks);
    }

    // Theme analyses
    var themes = analysis.theme_analyses || [];
    if (themes.length > 0) {
      show(themeAnalysesSection);
      themeAnalyses.textContent = "";
      themes.forEach(function (t) {
        var div = document.createElement("div");
        div.className = "theme-analysis";
        var h4 = document.createElement("h4");
        h4.textContent = t.theme || "未知主题";
        div.appendChild(h4);

        if (t.observations && t.observations.length > 0) {
          var obsDiv = document.createElement("div");
          obsDiv.textContent = "观察: " + t.observations.join("；");
          div.appendChild(obsDiv);
        }
        if (t.supporting_evidence && t.supporting_evidence.length > 0) {
          addEvidenceTags(div, "证据:", t.supporting_evidence);
        }
        if (t.uncertainty) {
          var uncDiv = document.createElement("div");
          uncDiv.textContent = "不确定性: " + t.uncertainty;
          div.appendChild(uncDiv);
        }

        themeAnalyses.appendChild(div);
      });
    } else {
      hide(themeAnalysesSection);
    }

    // Followup questions
    var questions = data.followup_questions || [];
    if (questions.length > 0) {
      show(followupSection);
      followupQuestions.textContent = "";
      questions.forEach(function (q) {
        var li = document.createElement("li");
        var questionText = document.createElement("span");
        questionText.textContent = q.question || "";
        li.appendChild(questionText);
        if (q.reason) {
          var reasonText = document.createElement("span");
          reasonText.textContent = "（原因：" + q.reason + "）";
          li.appendChild(reasonText);
        }
        if (q.related_chart_factors && q.related_chart_factors.length > 0) {
          addEvidenceTags(li, "关联:", q.related_chart_factors);
        }
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
