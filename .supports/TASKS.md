# TASKS.md

## 当前工作模式

- Claude 负责开发、测试、commit 和 push。
- Codex 负责任务规划、code review 和验收。
- merge 只由项目负责人执行。
- 开发前必须阅读 `AGENTS.md` 和 `.supports/` 下的规范文档。
- 每次开启新任务时，本文件只保留当前任务的完整执行说明；旧任务压缩为摘要，避免上下文膨胀。

## 任务压缩规则

当新任务开始时：

- 当前任务保留完整目标、边界、文件、TDD 步骤、测试命令和验收要求。
- 旧任务压缩为 3-8 条摘要，保留分支名、目标、关键交付、关键决策、测试结果和遗留风险。
- 对架构关键任务可以保留更多细节，例如真实 LLM、真实排盘、输出契约。
- 删除旧的大段 Claude 执行提示词、重复文件清单和完整测试日志；必要测试结果用一行摘要保存。

## 分支计划

第一阶段拆分为 8 个可独立 review 和验收的分支，按顺序执行。

### Branch 1: 约束文档与计划

- 分支名：`docs/v0.1-context-and-plan`
- 目标：建立 `AGENTS.md` 和 `.supports/` 规范文档，明确 v0.1 只做紫微斗数 + LLM Agent 分析闭环。
- 关键交付：项目背景、架构、决策、任务、Prompt、API、开发指南文档。
- 重要决策：Claude 开发测试，Codex review 验收，merge 只由项目负责人执行。

### Branch 2: 项目基础结构

- 分支名：`feature/v0.1-project-foundation`
- 目标：建立 FastAPI + uv + pytest 基础结构，不实现紫微业务逻辑。
- 关键交付：`app/`、`tests/`、`app/main.py`、健康检查、Settings、统一 logger、`pyproject.toml`、`uv.lock`、`.env.example`。
- 测试摘要：健康检查、配置、logger、应用创建测试通过。

### Branch 3: 命盘核心结构

- 分支名：`feature/v0.1-chart-core`
- 目标：定义 BirthInfo、RawChart、NormalizedChart、ZiweiChartEngine stub 和 ChartNormalizer。
- 关键交付：`app/schemas/birth.py`、`app/schemas/chart.py`、`app/schemas/analysis.py`、`app/engines/ziwei_chart_engine.py`、`app/engines/chart_normalizer.py`。
- 重要决策：Engine stub 必须显式 `source="stub"`；LLM 不参与排盘。
- 遗留风险：`lunar` 在 Schema 层接受，但 Engine 后续需明确 unsupported。

### Branch 4: LLM 分析闭环

- 分支名：`feature/v0.1-analysis-flow`
- 目标：建立 Mock LLM、Prompt、Agent、Service、API 和 Markdown 报告闭环。
- 关键交付：`LLMClient` 抽象、`MockLLMClient`、Prompt loader、`ZiweiAnalysisAgent`、`AnalysisService`、`POST /api/v1/ziwei/analyze`。
- 重要决策：所有 LLM 调用经过 `LLMClient`；Prompt 独立文件；报告缺少免责声明时 Agent 兜底补齐。
- 遗留风险：早期 `AnalysisResult` 部分字段仍是占位结构，真实 LLM 后需结构化解析。

### Branch 5: 真实 LLM Client

- 分支名：`feature/v0.1-real-llm-client`
- 目标：支持通过配置使用真实 OpenAI-compatible LLM，不再运行时硬编码 Mock。
- 关键交付：`app/llm/openai_compatible.py`、`llm_provider` / `llm_wire_api` / `llm_timeout_seconds` 配置、依赖装配、LLM 错误映射。
- 重要决策：`MINGMAX_LLM_PROVIDER=mock` 使用 Mock；`openai_compatible` 使用真实 Client；未知 provider/wire API/缺配置不得静默退回 mock。
- 支持协议：`chat_completions` 和 `responses`。
- 手动验证：使用脱敏真实配置验证过简单调用和完整 API 闭环；当时 `chart.source` 仍为 `stub`。
- 遗留风险：真实输出质量依赖 Prompt；默认 30s 超时对完整分析可能偏短，生产建议 120s。

### Branch 6: 简单静态前端

- 分支名：`feature/v0.1-static-frontend`
- 目标：提供原生 HTML/CSS/JS 前端，用于验证出生信息输入、分析选项、错误提示和报告展示闭环。
- 关键交付：`app/web/static/index.html`、`styles.css`、`app.js`，FastAPI 静态文件挂载，根路径重定向。
- 重要决策：不引入 React/Vue/Vite/Tailwind；前端只调用 `/api/v1/ziwei/analyze`，不参与排盘或 LLM 调用。
- 遗留风险：Markdown 报告用 `<pre>` 原文展示；复杂渲染后续再做。

### Branch 7: 真实紫微排盘引擎

- 分支名：`feature/v0.1-real-chart-engine`
- 目标：替换运行时 stub 排盘，使用 `iztro-py>=0.3.4,<1` 作为真实确定性紫微排盘 provider。
- 关键交付：
  - `app/engines/providers/iztro_provider.py` 封装 `iztro-py`；
  - `ZiweiChartEngine.build_chart()` 保持接口不变，内部调用 provider；
  - `RawChart.source` 从 `stub` 改为 `iztro_py`；
  - 前端根据 `chart.source` 动态展示排盘来源；
  - `pyproject.toml` / `uv.lock` 增加 `iztro-py`。
- 支持范围：公历输入、`male` / `female`、12 宫、主星/辅星/杂曜、天干/地支、四化。
- 未支持范围：农历输入、`Gender.unknown`、真太阳时校正、大限、流年。
- 重要决策：第三方紫微库只允许在 Engine/Provider 层使用，不泄漏到 API、Service、Agent 或 LLM 层。
- 遗留风险：`iztro-py` metadata 标注 Python 3.8-3.12，但实际已在 Python 3.14 下安装运行；后续升级 Python 或依赖时需重新验证。

### Branch 8: LLM 输出质量与失败兜底

- 分支名：`feature/v0.1-llm-output-contract-and-fallback`
- 目标：修通真实 LLM 工作流，建立基础分析、主题分析和追问问题的 JSON 输出契约、结构化解析和失败兜底。
- 关键交付：`LLMOutputParseError`、JSON object/array 解析、`LLM_OUTPUT_INVALID` 502 错误映射、Prompt JSON-only 约束、MockLLMClient 分 prompt 返回契约化内容。
- 重要决策：Agent 负责解析 LLM 输出，Service 只编排；模型返回非 JSON、缺字段或字段类型错误时不得伪成功。
- 测试摘要：`uv run black --check .`、`uv run isort --check-only .`、`uv run flake8 .`、`uv run pytest -q` 均已通过；当时测试为 `123 passed`。
- 遗留风险：真实 LLM 输出质量仍依赖 prompt 和模型稳定性；报告 Markdown 暂不做结构化解析。

### Branch 9: 私密样本驱动的排盘准确性基准

- 分支名：`feature/v0.1-chart-accuracy-baseline`
- 目标：建立排盘准确性验证工具链，修复真太阳时偏差导致宫位错误，通过本地私密样本验证排盘正确性。
- 关键交付：
  - `app/engines/chart_diff.py` 结构化命盘对比工具；
  - `app/engines/providers/iztro_provider.py` 真太阳时校正（均时差 + 经度校正）；
  - `app/schemas/birth.py` 新增可选 `longitude` 字段；
  - `scripts/verify_private_chart_sample.py` 本地验证脚本；
  - `tests/test_chart_diff.py`、`tests/test_chart_normalizer_accuracy.py`、`tests/test_provider_input_caliber.py`。
- 重要决策：宫位 index 差异（参考系统起点 vs iztro 起点不同）降为 warning 而非 error；第三方库使用范围限定在 Engine/Provider 层。
- 遗留风险：`iztro-py` metadata 标注 Python 3.8-3.12 但已在 Python 3.14 下运行；真太阳时均时差为近似值。

## Code Review 申请

### Branch 9: `feature/v0.1-chart-accuracy-baseline`

**分支名：** `feature/v0.1-chart-accuracy-baseline`

**Commit 列表：**

1. `feat: add chart diff tool, true solar time correction and accuracy baseline`

**修改文件列表：**

- `app/engines/chart_diff.py` — 新增 `ExpectedPalaceSnapshot`、`ExpectedChartSnapshot`、`PalaceDiff`、`ChartDiffResult`、`diff_charts()` 结构化对比工具；index 差异为 warning，major_stars/name/count/hua 差异为 error
- `app/engines/providers/iztro_provider.py` — 新增 365 日均时差近似表 `_EQUATION_OF_TIME_APPROX`；新增 `_true_solar_time_offset()` 计算真太阳时偏移；`_get_local_date_hour()` 在提供 longitude 时自动校正时辰
- `app/schemas/birth.py` — 新增可选 `longitude: float | None = None` 字段（东经度数）
- `scripts/verify_private_chart_sample.py` — 本地私密样本验证脚本，解析参考命盘文本，与排盘结果对比，输出脱敏差异摘要
- `.gitignore` — 新增 `.supports/TEST_INFO_EVA.md` 排除规则
- `tests/test_chart_diff.py` — 9 项测试：identical、star mismatch、body palace warning、count mismatch、four hua、missing palace、index warning、no private data
- `tests/test_chart_normalizer_accuracy.py` — 10 项测试验证 NormalizedChart 保真透传
- `tests/test_provider_input_caliber.py` — 8 项测试：有/无 longitude、真太阳时校正、EOT 边界、negative longitude、gender unknown
- `.supports/API_SPEC.md` — 新增 `longitude` 字段文档、排盘准确性验证相关说明
- `.supports/ARCHITECTURE.md` — 新增排盘准确性验证章节：输入口径、真太阳时计算、字段保真、对比工具、本地验证脚本、未支持范围
- `.supports/DEVELOPMENT_GUIDE.md` — 新增本地私密样本验证章节和隐私要求
- `.supports/DECISIONS.md` — 新增 D019（私密样本不进仓库）
- `.supports/TASKS.md` — 压缩旧任务摘要，更新当前任务

**关键架构决策：**

- 真太阳时校正仅在提供 `longitude` 时启用，不改变无 longitude 的默认行为
- 均时差使用 365 天近似表（精度约 1 分钟），足够时辰级判定
- 宫位 index 在不同排盘系统中起点不同（子 vs 寅），降为 warning 避免误报
- 私密验证文件 `.supports/TEST_INFO_EVA.md` 通过 `.gitignore` 排除，测试只使用合成 fixture
- `chart_diff.py` 只输出字段级差异统计，不包含任何出生信息

**测试命令和结果：**

```bash
uv run black --check .   # 55 files unchanged
uv run isort --check-only .  # no changes
uv run flake8 .           # 0 errors

uv run pytest -q          # 150 passed in 0.40s
```

**本地验证结果：**

使用私密样本 `scripts/verify_private_chart_sample.py .supports/TEST_INFO_EVA.md` 验证通过，0 errors。

**未完成事项或风险：**

- 真太阳时均时差为近似值，精度约 1 分钟，极端边界（时辰交界点）可能需更高精度表
- 大限、流年、流月、流日、流时暂未支持
- 农历输入和 `Gender.unknown` 仍不支持
- `.supports/ZIWEI_TS_REFERENCE_REVIEW.md` 为研究过程文档，是否提交待确认

**请求 Codex review。**

## Codex 验收清单

Codex 验收时关注：

- 是否遵守 `AGENTS.md` 和 `.supports/` 约束。
- 是否保持分层清晰：API 不直接调用 LLM，Service 只编排，Agent 负责 Prompt 与解析，Engine 只排盘。
- 是否移除 `mock` 占位字段，不再把 Markdown 整段塞进结构化字段。
- 是否所有真实 LLM 调用仍经过统一 `LLMClient` 抽象。
- 是否 Prompt 独立管理并要求 JSON 输出。
- 是否对非 JSON、空内容、缺字段、字段类型错误有测试和清晰错误。
- 是否单元测试不访问真实外部 LLM，不依赖本机 `.env`。
- 是否报告包含免责声明。
- 是否没有引入超出 v0.1 范围的依赖或模块。

## Code Review 申请

### Branch 8: `feature/v0.1-llm-output-contract-and-fallback`

**分支名：** `feature/v0.1-llm-output-contract-and-fallback`

**Commit 列表：**

1. `feat: add LLM output JSON contract, structured parsing and fallback error mapping`

**修改文件列表：**

- `app/agents/ziwei_analysis_agent.py` — 新增 `LLMOutputParseError`、`_parse_json_object()`、`_parse_json_array()` 解析函数；Agent 方法改为返回结构化类型（`AnalysisResult`、`ThemeAnalysis`、`FollowupQuestion`）；`generate_report()` 接受 `AnalysisResult` 参数
- `app/llm/mock.py` — MockLLMClient 根据 prompt 类型返回不同内容：基础分析 JSON、主题分析 JSON、追问 JSON 数组、Markdown 报告；所有 JSON 符合输出契约
- `app/services/analysis_service.py` — 移除 `uncertainty="mock"` 和 `reason="mock"` 占位；Service 只编排 Engine→Normalizer→Agent 流程
- `app/api/errors.py` — 新增 `llm_output_invalid_exception()` 和 `LLM_OUTPUT_INVALID` 错误码（HTTP 502）
- `app/api/v1/routes_analysis.py` — 新增 `LLMOutputParseError` 捕获和 `502` 响应
- `app/prompts/ziwei_analysis.md` — 明确要求只输出 JSON object，不输出 Markdown 或代码块
- `app/prompts/theme_analysis.md` — 明确要求只输出 JSON object，不输出 Markdown 或代码块
- `app/prompts/followup_questions.md` — 明确要求只输出 JSON 数组，不输出 Markdown 或代码块
- `.env.example` — 补充真实 LLM 启用说明，强调必须设置 `MINGMAX_LLM_PROVIDER=openai_compatible`
- `tests/test_agent_parsing.py` — 新增 Agent 解析测试（20 项：valid JSON、invalid JSON、code block、missing fields、wrong types、array instead of object、object instead of array）
- `tests/test_analysis_service.py` — 更新 Service 测试，新增 `test_service_analysis_has_no_mock_placeholders` 验证无 mock 占位
- `tests/test_mock_llm.py` — 更新 MockLLMClient 测试，验证不同 prompt 类型返回不同 JSON 格式
- `tests/test_api_analysis.py` — 新增 `LLM_OUTPUT_INVALID` 502 错误响应测试
- `tests/test_prompt_loading.py` — 更新 Prompt 测试，验证 JSON 输出要求
- `.supports/API_SPEC.md` — 新增 `LLM_OUTPUT_INVALID` 错误码和 `502` 状态码
- `.supports/DECISIONS.md` — 新增 D017（JSON 契约解析）和 D018（Prompt JSON-only 要求）
- `.supports/TASKS.md` — 压缩旧任务摘要，更新当前任务

**关键架构决策：**

- Agent 层新增 `LLMOutputParseError`，所有 LLM JSON 解析错误统一由此异常表示
- `_parse_json_object()` 和 `_parse_json_array()` 支持剥离 LLM 常见误输出的代码块包裹
- MockLLMClient 根据 prompt 关键字（"追问生成"/"主题分析助手"/"报告生成助手"）返回不同格式内容
- Service 不再硬编码 `uncertainty="mock"` 或 `reason="mock"`，所有分析字段来自 Agent 结构化返回
- API 层将 `LLMOutputParseError` 映射为 HTTP 502 + `LLM_OUTPUT_INVALID` 错误码
- Prompt 全部要求 JSON-only 输出，不含 Markdown 包裹

**测试命令和结果：**

```bash
uv run black --check .   # 50 files unchanged
uv run isort --check-only .  # no changes
uv run flake8 .           # 0 errors

uv run pytest -q          # 123 passed in 0.34s
```

**未完成事项或风险：**

- 真实 LLM 集成验证待手动完成（需要本机配置真实 KEY）
- 真实 LLM 输出质量取决于 Prompt 和模型能力；当前 Prompt 已明确要求 JSON-only，但模型可能仍返回带代码块的内容（解析层已处理此情况）
- `generate_report()` 仍返回 Markdown 文本，未做结构化解析（符合设计：报告天然是 Markdown 格式）

**请求 Codex review。**
