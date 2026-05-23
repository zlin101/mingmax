# ARCHITECTURE.md

## 分层结构

推荐目录结构：

```text
app/
  main.py
  api/
    v1/
      routes_analysis.py
  agents/
    ziwei_analysis_agent.py
  core/
    config.py
    logging.py
  engines/
    providers/
      iztro_provider.py
    ziwei_chart_engine.py
    chart_normalizer.py
    chart_relations.py
    chart_facts.py
    chart_diff.py
    time_calibration.py
  llm/
    base.py
    mock.py
  prompts/
    ziwei_analysis.md
    theme_analysis.md
    followup_questions.md
    report.md
  schemas/
    birth.py
    chart.py
    analysis.py
  services/
    analysis_service.py
  web/
    __init__.py
    static/
      index.html
      styles.css
      app.js
tests/
  conftest.py
  test_birth_schema.py
  test_chart_engine.py
  test_chart_normalizer.py
  test_chart_relations.py
  test_chart_facts.py
  test_analysis_service.py
  test_api_analysis.py
  test_prompt_loading.py
  test_mock_llm.py
  test_frontend_static.py
```

## 模块职责

- API 层：请求校验、依赖注入、响应封装，不写复杂业务逻辑，不直接调用 LLM。
- Service 层：编排出生信息、排盘、标准化、Agent 分析和报告生成流程。
- Engine 层：负责确定性排盘、命盘标准化、宫位关系计算（`chart_relations`）、结构化事实提取（`chart_facts`），不调用 LLM；第三方紫微库通过 `engines/providers/` 适配后再由 `ZiweiChartEngine` 使用。
- Agent 层：组织 LLM 分析流程、Prompt Pipeline、追问与校准，不负责排盘或关系计算。Agent 通过 `build_chart_facts()` 生成结构化证据传给 LLM，不得将原始 `NormalizedChart` JSON 直接交给模型。
- LLM 层：统一模型调用抽象，提供真实 Client 和 Mock Client。
- Schema 层：定义请求、响应、命盘、分析结果等结构化模型。
- Web 层：静态前端文件，通过 FastAPI 挂载，只调用后端 API，不直接参与排盘或 LLM 调用。
- Prompt 层：集中管理 Prompt 模板和输出约束。

## 数据流

```text
HTTP Request
  -> BirthInfo schema validation
  -> AnalysisService
  -> ZiweiChartEngine
  -> RawChart
  -> ChartNormalizer (enriches with relations: opposite, san_fang_si_zheng, empty/borrowed)
  -> NormalizedChart
  -> build_chart_facts() (extracts structured evidence)
  -> ZiweiAnalysisAgent (passes chart_facts, not raw chart JSON)
  -> LLMClient
  -> AnalysisResult
  -> Markdown report
  -> HTTP Response
```

## 禁止跨层调用

- API 层不得直接调用 LLM。
- API 层不得直接执行排盘或报告拼装。
- Agent 层不得执行安星、定宫、四化、大限、流年、对宫、三方四正、空宫借星等确定性逻辑。
- Engine 层不得调用 LLM。
- `chart_relations` 和 `chart_facts` 属于 Engine 层，Agent 层只能消费其输出。
- 第三方紫微库必须通过 `ZiweiChartEngine` 和内部 provider 封装，当前 Branch 7 优先使用 `iztro-py`。
- 第三方模型 SDK 必须通过 `LLMClient` 封装。

## v0.1 最小闭环

Branch 1-6 允许使用可预测的 Engine stub 和 Mock/真实 LLM Client 建立 API、Service、Agent、Prompt、Report、Web 的完整闭环。Branch 7 开始使用 `iztro-py` provider 替换运行时 stub 排盘，保持 `BirthInfo -> ZiweiChartEngine -> RawChart -> NormalizedChart -> ZiweiAnalysisAgent` 数据流不变。

## 排盘准确性验证

### 输入口径

`BirthInfo` 支持可选 `longitude` 字段（东经度数）：

- 默认始终进行真太阳时校正。
- 如果提供 `longitude`，使用其精确值计算真太阳时偏移（均时差 + 经度校正）。
- 如果不提供 `longitude`，从 `timezone` 的 UTC offset 推算近似经度（`longitude ≈ UTC_offset_hours × 15`），此时只有均时差修正，不含经度偏差修正。

### 真太阳时计算

`time_calibration.py` 中的 `true_solar_time_offset()` 使用均时差近似公式和经度校正计算真太阳时偏移。`infer_longitude_from_timezone()` 从时区 UTC offset 推算近似经度作为默认值。`iztro_provider.py` 只消费校正结果，不持有时间校正常量或公式。

### 字段保真

`ChartNormalizer` 直接透传 `RawChart` 的 `palaces`、`four_hua`，不丢弃或修改字段，并额外填充宫位关系（对宫、三方四正、空宫判断、借星）。`chart_diff.py` 提供结构化对比工具用于验证。

### 宫位关系计算

`app/engines/chart_relations.py` 提供纯函数：`opposite_palace_index()`、`san_fang_si_zheng_indexes()`、`is_empty_palace()`、`borrowed_from_index()`、`borrowed_major_stars()`。所有关系在 Engine/Normalizer 层计算，Agent 和 LLM 层不得重新推算。

### 结构化证据层

`app/engines/chart_facts.py` 的 `build_chart_facts()` 从 `NormalizedChart` 生成结构化事实字典，包含命宫/身宫定位、四化、每个宫位的主星/辅星/杂曜/化曜/对宫/三方四正/空宫借星。Agent 通过此函数构建传给 LLM 的 context，不再传递原始 chart JSON。

### 对比工具

`app/engines/chart_diff.py` 提供 `diff_charts()` 函数，将 `NormalizedChart` 与 `ExpectedChartSnapshot` 进行字段级对比，返回差异列表（severity: error/warning）。

### 本地验证脚本

`scripts/verify_private_chart_sample.py` 接受本地文件路径，解析参考命盘文本，与 mingmax 排盘结果对比，输出脱敏差异摘要。不得提交私密验证文件。

### 未支持范围

- 农历输入
- `Gender.unknown`
- 真太阳时精确校正（无 longitude 时使用时区推算近似经度，偏差可能较大）
- 大限、流年、流月、流日、流时
