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

## 当前任务：Branch 8 LLM 输出质量与失败兜底

### 基本信息

- 任务名称：v0.1 LLM 输出质量与失败兜底
- 建议分支名：`feature/v0.1-llm-output-contract-and-fallback`
- 分支起点：`feature/v0.1-real-chart-engine` 合并后的 `develop` 基线。
- 交付后验收人：Codex。

Claude 开发前建议执行：

```bash
git switch develop
git pull --ff-only
git switch -c feature/v0.1-llm-output-contract-and-fallback
```

### 任务目标

先修通真实模型工作流，确保运行时不会误用 MockLLMClient；再为基础分析、主题分析和追问问题建立 JSON 输出契约、解析逻辑和失败兜底。

当前已确认的根因：

- 如果本机 `.env` 未显式设置 `MINGMAX_LLM_PROVIDER=openai_compatible`，运行时会继续使用 MockLLMClient。
- `app/services/analysis_service.py` 当前仍硬编码 `uncertainty="mock"` 和 `reason="mock"`。
- `MockLLMClient` 当前返回 Markdown stub 报告文本，导致主题分析里出现整段 Markdown 被塞入 `observations` 的情况。
- Branch 7 已处理真实排盘；Branch 8 不再改排盘 provider，只消费 `NormalizedChart`。

### 任务边界

本分支只解决：

- 真实 LLM 工作流启用与可验证性；
- LLM JSON 输出契约；
- Agent 结构化解析；
- 解析失败兜底；
- `mock` 占位字段清理；
- 相关 Prompt、API、测试和文档更新。

本分支不做：

- 真实排盘 provider 改造；
- 八字、MBTI、多 Agent；
- 数据库、任务队列、向量数据库；
- 用户系统、支付系统；
- 复杂前端或前端框架。

### 必须修改的模块

- `app/core/config.py`
  - 保留默认 `llm_provider="mock"`，但文档和手动验证必须明确真实模型需要 `MINGMAX_LLM_PROVIDER=openai_compatible`。
- `.env.example`
  - 补充真实模型启用示例，强调必须设置 `MINGMAX_LLM_PROVIDER=openai_compatible`，不能只设置 model/key/base_url。
- `app/llm/mock.py`
  - Mock 返回内容改为符合 JSON 输出契约的文本，不再返回 stub Markdown 报告作为所有 prompt 的固定输出。
- `app/agents/ziwei_analysis_agent.py`
  - 增加结构化解析职责。
  - `analyze()` 应返回 `AnalysisResult` 或等价内部结构，而不是裸字符串。
  - `analyze_themes()` 应返回 `list[ThemeAnalysis]`。
  - `generate_followup_questions()` 应返回 `list[FollowupQuestion]`。
  - `generate_report()` 可以继续返回 Markdown，但必须基于结构化分析上下文。
- `app/services/analysis_service.py`
  - 移除 `uncertainty="mock"`、`reason="mock"` 等开发占位。
  - Service 只编排 Engine、Normalizer、Agent，不负责拼装假的分析字段。
- `app/api/errors.py` 与 `app/api/v1/routes_analysis.py`
  - 将 LLM 输出解析错误映射为清晰错误响应。
  - 建议错误码：`LLM_OUTPUT_INVALID`。
  - HTTP 状态可用 `502 Bad Gateway` 或沿用当前 LLM 失败策略，但必须一致并有测试。
- `app/prompts/ziwei_analysis.md`
  - 明确要求只输出 JSON object，不要 Markdown，不要代码块。
- `app/prompts/theme_analysis.md`
  - 明确要求只输出 JSON object，不要 Markdown，不要代码块。
- `app/prompts/followup_questions.md`
  - 明确要求只输出 JSON array，不要 Markdown，不要代码块。
- `.supports/API_SPEC.md`
  - 若实现中调整错误码或响应格式，必须同步更新。
- `.supports/PROMPT_GUIDE.md`
  - 若 Prompt JSON 字段变化，必须同步更新。

### 输出契约

基础分析 JSON：

```json
{
  "summary": "string",
  "strong_signals": ["string"],
  "weak_hypotheses": ["string"],
  "cross_checks": ["string"],
  "safety_note": "string"
}
```

主题分析 JSON：

```json
{
  "theme": "relationship",
  "observations": ["string"],
  "supporting_evidence": ["string"],
  "uncertainty": "string",
  "followup_questions": ["string"]
}
```

追问问题 JSON：

```json
[
  {
    "question": "string",
    "reason": "string",
    "related_chart_factors": ["string"]
  }
]
```

### 推荐 TDD 步骤

1. 先写 `tests/test_ziwei_analysis_agent.py` 或更新现有 Agent 测试：
   - Mock LLM 返回合法基础分析 JSON，`agent.analyze()` 解析为 `AnalysisResult`。
   - Mock LLM 返回合法主题 JSON，`agent.analyze_themes()` 解析为 `ThemeAnalysis`。
   - Mock LLM 返回合法追问 JSON array，`agent.generate_followup_questions()` 解析为 `FollowupQuestion` 列表。
   - Mock LLM 返回非 JSON，抛出明确的 LLM 输出错误。
   - Mock LLM 返回缺少必填字段，抛出明确的 LLM 输出错误。
   - Mock LLM 返回字段类型错误，抛出明确的 LLM 输出错误。
2. 再实现 Agent 解析逻辑和错误类型。
3. 更新 `MockLLMClient`，让不同 prompt 返回符合契约的固定 JSON 或报告 Markdown。
4. 更新 `AnalysisService`，移除 `mock` 占位字段。
5. 写 API 错误映射测试：
   - LLM 输出解析失败时 API 返回结构化错误，不返回伪成功分析。
6. 写依赖装配或配置测试：
   - `MINGMAX_LLM_PROVIDER=openai_compatible` 时返回真实 Client。
   - `.env` 只设置 model/key/base_url 但未设置 provider 时，仍应保持 mock；文档必须明确这一点。
7. 更新 prompt 文件和 `.supports/` 文档。

### 手动真实 LLM 验证要求

Claude 完成本分支后，使用本机私密 `.env` 做一次手动验证，但不得提交真实 key。

必须记录脱敏信息：

```text
MINGMAX_LLM_PROVIDER=openai_compatible
MINGMAX_LLM_MODEL=<脱敏或模型名>
MINGMAX_LLM_BASE_URL=<脱敏或公开网关 URL>
MINGMAX_LLM_API_KEY=<redacted>
MINGMAX_LLM_WIRE_API=chat_completions
MINGMAX_LLM_TIMEOUT_SECONDS=120
```

验收响应必须满足：

- 不出现 `uncertainty: "mock"`。
- 不出现 `reason: "mock"`。
- 不出现 MockLLMClient 固定文案"基于 stub 排盘的模拟分析"。
- 主题分析的 `observations` 是观察点数组，不是整段 Markdown 报告。
- 如果模型认为证据不足，必须基于当前 `chart.source` 和结构化命盘说明原因，不能把 Mock 文案当作模型输出。
- 报告包含免责声明。

### 测试命令

Claude 完成开发后必须报告以下命令和结果：

```bash
uv run black --check .
uv run isort --check-only .
uv run flake8 .
uv run pytest -q
```

如当前分支还没有 `.flake8` 导致 `uv run flake8 .` 扫描 `.venv` 或使用 79 行宽，Claude 应补充最小 `.flake8`，与 Black/isort 的 120 行宽保持一致，并排除 `.venv`。

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
