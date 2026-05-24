# API_SPEC.md

## v0.1 API 范围

第一阶段只定义一个最小分析接口：

```text
POST /api/v1/ziwei/analyze
```

API 层只负责请求校验、依赖注入和响应封装，不直接调用 LLM，不直接执行排盘逻辑。

## 请求示例

```json
{
  "birth": {
    "calendar_type": "solar",
    "birth_datetime": "1995-05-17T08:30:00+08:00",
    "gender": "female",
    "birth_place": "Shanghai, China",
    "timezone": "Asia/Shanghai",
    "longitude": 121.47
  },
  "options": {
    "themes": ["career", "relationship"],
    "include_followup_questions": true,
    "include_markdown_report": true
  }
}
```

## 字段枚举

`calendar_type` 可选值：

```text
solar
lunar
```

v0.1 第一阶段可以只实现 `solar`，但遇到未支持的 `lunar` 必须返回清晰错误，不得静默当作公历处理。

`gender` 可选值：

```text
male
female
unknown
```

Branch 7 接入 `iztro-py` 后，真实排盘 provider 只支持 `male` / `female`，分别映射为 `iztro-py` 的 `男` / `女`。`unknown` 必须返回清晰错误，不得静默按任一性别处理。

`timezone` 必须使用 IANA 时区名称，例如 `Asia/Shanghai`。如果请求已提供带 offset 的 `birth_datetime`，仍应保留 `timezone` 用于后续历法策略校准。

`longitude` 为可选字段，单位为东经度数（例如 `121.47`）。默认始终进行真太阳时校正：如果提供 `longitude`，使用其精确值计算；如果不提供，从 `timezone` 的 UTC offset 推算近似经度（`longitude ≈ UTC_offset_hours × 15`），仅含均时差修正，不含经度偏差修正。对于出生地经度与标准时区经线偏差较大的地区，建议显式提供 `longitude` 以获得准确时辰。

`options.themes` v0.1 建议可选值：

```text
career
relationship
self_understanding
```

## 响应示例

```json
{
  "chart": {
    "chart_id": "sample-chart-id",
    "source": "iztro_py",
    "summary": "Normalized ziwei chart summary",
    "ming_palace_index": 3,
    "body_palace_index": 7,
    "five_elements_class": null,
    "lunar_info": null,
    "palaces": [
      {
        "index": 0,
        "name": "命宫",
        "heavenly_stem": "甲",
        "earthly_branch": "子",
        "stars": [
          {"name": "紫微", "brightness": "庙", "category": "major"},
          {"name": "天府", "brightness": "旺", "category": "major"}
        ],
        "four_hua": null,
        "is_body_palace": false,
        "opposite_palace_index": 6,
        "san_fang_si_zheng_indexes": [0, 4, 6, 8],
        "is_empty": false,
        "borrowed_from_index": null,
        "borrowed_major_stars": null
      }
    ],
    "four_hua": {
      "hua_lu": "贪狼",
      "hua_quan": "太阴",
      "hua_ke": "右弼",
      "hua_ji": "天机"
    }
  },
  "analysis": {
    "summary": "基于当前结构化命盘的总体观察。",
    "strong_signals": [],
    "weak_hypotheses": [],
    "cross_checks": [],
    "theme_analyses": []
  },
  "followup_questions": [],
  "report_markdown": "# 紫微斗数分析报告\n\n## 免责声明\n\n本分析仅供文化研究、娱乐体验与自我反思参考，不构成医学、法律、财务、心理诊断或人生决策依据。"
}
```

## 错误响应建议

```json
{
  "error": {
    "code": "INVALID_BIRTH_INFO",
    "message": "Birth information is invalid.",
    "details": []
  }
}
```

## 错误码建议

- `INVALID_BIRTH_INFO`：出生信息字段非法。
- `UNSUPPORTED_CALENDAR_TYPE`：请求了当前阶段不支持的历法类型。
- `CHART_ENGINE_FAILED`：排盘 Engine 失败。
- `PROMPT_LOAD_FAILED`：Prompt 文件缺失或加载失败。
- `LLM_CLIENT_FAILED`：LLM 抽象层调用失败。
- `LLM_OUTPUT_INVALID`：LLM 输出不符合 JSON 契约（非 JSON、空内容、缺少必填字段、字段类型错误）。
- `REPORT_GENERATION_FAILED`：Markdown 报告生成失败。

## 状态码

- `200`：分析成功。
- `422`：请求结构或字段校验失败。
- `500`：内部服务错误。
- `502`：LLM 输出解析失败（`LLM_OUTPUT_INVALID`）。

## 契约约束

- 请求必须先进入 Schema 校验。
- API 不直接调用第三方 LLM SDK。
- API 不直接调用第三方紫微库。
- 响应必须可 JSON 序列化。
- `report_markdown` 必须包含免责声明。
- 单元测试不得真实调用外部 LLM API。
- Branch 7 后 `chart.source` 应反映真实排盘 provider，例如 `iztro_py`；只有实际使用 stub 时才允许返回 `stub`。
- 当前 v0.1 真实排盘使用 `birth_datetime` 在 `timezone` 对应地区的本地日期与小时，默认始终进行真太阳时校正。
- `NormalizedChart` 的 `palaces` 中每个宫位包含 `opposite_palace_index`、`san_fang_si_zheng_indexes`、`is_empty`、`borrowed_from_index`、`borrowed_major_stars` 等确定性关系字段。
- Agent 传给 LLM 的 context 是 `chart_facts` 结构化证据，不是原始 chart JSON。
- `chart_facts` 结构（Branch 16/17+）包含：
  - `supported_analysis_layers`：支持的分析层（`natal_chart`、`decadal_range`）
  - `unsupported_analysis_layers`：不支持的分析层（`annual`、`monthly`、`daily`、`hourly`、`bazi`）
  - `metadata`：命盘背景信息（`lunar_date`、`chinese_date`、`five_elements_class` 等）
  - `palaces[]`：宫位数组，每个包含 `major_star_facts`、`minor_star_facts`、`adjective_star_facts`（结构化星曜事实，包含 `name`、`brightness`、`category`、`scope`、`evidence_id`）
  - `palaces[].decadal`：宫位大限信息（`start_age`、`end_age`、`heavenly_stem`、`earthly_branch`、`palace_name`）
  - `current_age` / `current_decadal`：当前分析上下文
  - `evidence_index`：证据 ID 列表，支持类型：`palace`、`star`、`mutagen`、`relation`、`borrowed`、`decadal`、`metadata`

## 真实 LLM 运行时配置

Branch 5 开始允许运行时使用真实 LLM，但必须通过项目统一 `LLMClient` 抽象接入。

建议环境变量：

```text
MINGMAX_LLM_PROVIDER=openai_compatible
MINGMAX_LLM_MODEL=<由本机环境配置>
MINGMAX_LLM_API_KEY=<由本机环境配置>
MINGMAX_LLM_BASE_URL=<由本机环境配置>
MINGMAX_LLM_WIRE_API=chat_completions
MINGMAX_LLM_TIMEOUT_SECONDS=30
```

约束：

- `MINGMAX_LLM_PROVIDER=mock` 时使用 Mock LLM，便于本地无 KEY 开发。
- `MINGMAX_LLM_PROVIDER=openai_compatible` 时使用真实 OpenAI-compatible Client。
- `MINGMAX_LLM_WIRE_API=chat_completions` 时调用 `POST {base_url}/chat/completions`。
- `MINGMAX_LLM_WIRE_API=responses` 时调用 `POST {base_url}/responses`。
- 未知 provider、未知 wire API 或真实 Client 缺少 API Key/base URL/model 时必须返回清晰配置错误，不得静默退回 mock。
- 单元测试必须 mock 外部 HTTP，不得依赖真实 KEY 或真实外网。
- 手动集成验证可以真实调用已配置 KEY，但只能记录脱敏配置和响应摘要。
- 真实 LLM 失败时不得返回伪成功分析，应返回清晰错误。
- `chart.source` 仍反映排盘来源；当前真实 LLM 接入不等于真实紫微排盘。

## 前端核验视图使用的 chart 字段

Branch 12 前端命盘核验视图消费以下 `chart` 字段：

- `chart.source`：排盘来源，展示在来源标识和摘要区。
- `chart.chart_id`：命盘唯一标识，展示在摘要区。
- `chart.ming_palace_index` / `chart.body_palace_index`：命宫/身宫 index，前端据此查找对应宫位名称。
- `chart.five_elements_class`：五行局（Branch 16/17+ 来自 `chart.metadata.five_elements_class`）。
- `chart.metadata`：元数据信息，包含 `lunar_date`（农历日期）、`chinese_date`（四柱字符串）、`five_elements_class`、`soul_palace_earthly_branch`、`body_palace_earthly_branch`、`body`（身宫类型）。
- `chart.current_age`：当前虚岁（Branch 16/17+）。
- `chart.current_decadal`：当前大限信息（Branch 16/17+），包含 `start_age`、`end_age`、`heavenly_stem`、`earthly_branch`、`palace_name`。
- `chart.palaces[].index`：宫位 index（0-11），前端按固定映射将 index 映射到 4x4 网格位置。
- `chart.palaces[].name`：宫位名称。
- `chart.palaces[].heavenly_stem` / `earthly_branch`：天干地支。
- `chart.palaces[].stars[].name` / `brightness` / `category` / `scope`：星曜信息（Branch 16/17+ 增加 `scope` 字段）。
- `chart.palaces[].four_hua`：宫位级四化（`hua_lu`/`hua_quan`/`hua_ke``/`hua_ji`），可能为 `null`。
- `chart.palaces[].is_body_palace`：身宫标记。
- `chart.palaces[].opposite_palace_index`：对宫 index。
- `chart.palaces[].san_fang_si_zheng_indexes`：三方四正 indexes。
- `chart.palaces[].is_empty`：空宫标记。
- `chart.palaces[].borrowed_from_index` / `borrowed_major_stars`：借星来源。
- `chart.palaces[].decadal`：该宫位的大限信息（Branch 16/17+），包含 `start_age`、`end_age`、`heavenly_stem`、`earthly_branch`、`palace_name`。

约束：

- 前端只展示 API 返回的 chart 字段，不计算排盘关系（对宫、三方四正、空宫借星等均由后端提供）。
- 前端按 `index` 到固定 earthly branch 网格位置的映射渲染 4x4 盘面，不依赖 earthly_branch 字符串定位。

## 静态前端路由

```text
GET /                           -> 307 重定向到 /static/index.html
GET /static/index.html          -> 前端入口页
GET /static/styles.css          -> 样式表
GET /static/app.js              -> 前端逻辑
```

约束：

- 前端只通过 `fetch("/api/v1/ziwei/analyze")` 调用后端 API，不绕过 API 层。
- 前端不引入 React、Vue、Vite、Tailwind 或复杂前端框架。
- 页面必须根据 `chart.source` 动态展示排盘来源；只有 `chart.source = "stub"` 时才展示 stub 警告。
- 页面必须展示免责声明。
