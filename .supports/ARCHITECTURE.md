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
  test_analysis_service.py
  test_api_analysis.py
  test_prompt_loading.py
  test_mock_llm.py
  test_frontend_static.py
```

## 模块职责

- API 层：请求校验、依赖注入、响应封装，不写复杂业务逻辑，不直接调用 LLM。
- Service 层：编排出生信息、排盘、标准化、Agent 分析和报告生成流程。
- Engine 层：负责确定性排盘、命盘标准化、规则计算，不调用 LLM；第三方紫微库通过 `engines/providers/` 适配后再由 `ZiweiChartEngine` 使用。
- Agent 层：组织 LLM 分析流程、Prompt Pipeline、追问与校准，不负责排盘。
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
  -> ChartNormalizer
  -> NormalizedChart
  -> ZiweiAnalysisAgent
  -> LLMClient
  -> AnalysisResult
  -> Markdown report
  -> HTTP Response
```

## 禁止跨层调用

- API 层不得直接调用 LLM。
- API 层不得直接执行排盘或报告拼装。
- Agent 层不得执行安星、定宫、四化、大限、流年等确定性排盘逻辑。
- Engine 层不得调用 LLM。
- 第三方紫微库必须通过 `ZiweiChartEngine` 和内部 provider 封装，当前 Branch 7 优先使用 `iztro-py`。
- 第三方模型 SDK 必须通过 `LLMClient` 封装。

## v0.1 最小闭环

Branch 1-6 允许使用可预测的 Engine stub 和 Mock/真实 LLM Client 建立 API、Service、Agent、Prompt、Report、Web 的完整闭环。Branch 7 开始使用 `iztro-py` provider 替换运行时 stub 排盘，保持 `BirthInfo -> ZiweiChartEngine -> RawChart -> NormalizedChart -> ZiweiAnalysisAgent` 数据流不变。
