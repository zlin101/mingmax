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
    "timezone": "Asia/Shanghai"
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

`timezone` 必须使用 IANA 时区名称，例如 `Asia/Shanghai`。如果请求已提供带 offset 的 `birth_datetime`，仍应保留 `timezone` 用于后续历法策略校准。

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
    "summary": "Normalized ziwei chart summary",
    "palaces": []
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
- `REPORT_GENERATION_FAILED`：Markdown 报告生成失败。

## 状态码

- `200`：分析成功。
- `422`：请求结构或字段校验失败。
- `500`：内部服务错误。

## 契约约束

- 请求必须先进入 Schema 校验。
- API 不直接调用第三方 LLM SDK。
- API 不直接调用第三方紫微库。
- 响应必须可 JSON 序列化。
- `report_markdown` 必须包含免责声明。
- 单元测试不得真实调用外部 LLM API。
