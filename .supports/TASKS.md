# TASKS.md

## 当前工作模式

- Claude 负责开发和测试。
- Codex 负责 code review 和验收。
- Codex 不参与测试执行。
- 开发前必须阅读 `AGENTS.md` 和 `.supports/` 下的规范文档。
- 每次开发任务下达时，Codex 先在本文件写明建议新建分支和分支名称；Claude 基于该分支开发和测试。

## 分支计划

第一阶段拆分为 6 个可独立 review 和验收的分支，按顺序执行。

### Branch 1: 约束文档与计划

- 任务名称：v0.1 约束文档与开发计划
- 建议分支名：`docs/v0.1-context-and-plan`
- 分支用途：提交 `AGENTS.md` 和 `.supports/` 下的项目上下文、架构、决策、任务、Prompt、API、开发指南文档。
- 分支起点：当前主开发基线。
- 交付后验收人：Codex。
- Definition of Done：规范命名的 `.supports/` 文档齐全；旧错名空文档按 `.supports/DECISIONS.md` 的迁移决策处理；Claude/Codex/项目负责人分工、分支、commit、push、merge 规则明确。

Claude 开发前建议执行：

```bash
git switch -c docs/v0.1-context-and-plan
```

### Branch 2: 项目基础结构

- 任务名称：v0.1 FastAPI 项目基础结构
- 建议分支名：`feature/v0.1-project-foundation`
- 分支用途：建立 FastAPI、uv、pytest、格式化、基础 app/tests 结构和健康检查，不实现紫微业务逻辑。
- 分支起点：`docs/v0.1-context-and-plan` 合并后的基线。
- 交付后验收人：Codex。
- Definition of Done：`app/` 和 `tests/` 基础结构存在；FastAPI app 可导入；健康检查接口可测；`pyproject.toml` 配置 Black/isort/pytest；依赖变更包含 `uv.lock`；如新增配置项则包含 `.env.example`；Claude 报告格式化、lint、测试命令和结果。

### Branch 3: 命盘核心结构

- 任务名称：v0.1 命盘 Schema、Engine stub 与 Normalizer
- 建议分支名：`feature/v0.1-chart-core`
- 分支用途：实现 BirthInfo、RawChart、NormalizedChart、ZiweiChartEngine stub、ChartNormalizer 和确定性逻辑测试。
- 分支起点：`feature/v0.1-project-foundation` 合并后的基线。
- 交付后验收人：Codex。
- Definition of Done：出生信息 Schema 校验覆盖合法和非法输入；Engine stub 明确标记 `source = "stub"` 或等价字段；Normalizer 输出稳定结构；LLM 不参与排盘；Claude 报告相关测试命令和结果。

### Branch 4: LLM 分析闭环

- 任务名称：v0.1 LLM 分析、Prompt、Service 与 API 闭环
- 建议分支名：`feature/v0.1-analysis-flow`
- 分支用途：实现 LLM 抽象、Mock LLM、Prompt 文件、ZiweiAnalysisAgent、AnalysisService、`POST /api/v1/ziwei/analyze` 和 Markdown 报告。
- 分支起点：`feature/v0.1-chart-core` 合并后的基线。
- 交付后验收人：Codex。
- Definition of Done：所有 LLM 调用经统一抽象；测试使用 Mock LLM；Prompt 独立文件存在且包含安全约束；API 合法和非法请求均有测试；Markdown 报告包含免责声明；至少测试免责声明存在，必要时检查禁用绝对化表达不会出现在固定 mock 输出中。

### Branch 5: 真实 LLM 接入与真实请求验证

- 任务名称：v0.1 真实 LLM Client 接入
- 建议分支名：`feature/v0.1-real-llm-client`
- 分支用途：实现可配置的真实 LLM Client，让 API 在配置了真实 KEY、模型和 base URL 时不再使用 MockLLMClient。
- 分支起点：`feature/v0.1-analysis-flow` 合并后的基线。
- 交付后验收人：Codex。
- Definition of Done：所有真实 LLM 调用仍经 `LLMClient` 抽象；单元测试不真实访问外部 LLM；真实调用通过手动集成验证记录；失败时返回清晰错误；报告仍包含免责声明；LLM 不参与排盘，命盘仍来自 `ZiweiChartEngine`。

### Branch 6: 简单静态前端界面

- 任务名称：v0.1 简单前端分析界面
- 建议分支名：`feature/v0.1-static-frontend`
- 分支用途：在不引入复杂前端框架的前提下，为现有 `POST /api/v1/ziwei/analyze` 提供一个可用的浏览器界面，用于验证出生信息输入、分析选项、请求状态、错误提示和报告展示闭环。
- 分支起点：`feature/v0.1-real-llm-client` 合并后的基线。
- 交付后验收人：Codex。
- Definition of Done：用户可以在浏览器中打开前端页面并提交出生信息；前端调用现有分析 API；页面展示命盘摘要、分析摘要、主题分析、追问问题和 Markdown 报告；页面明确显示当前 `chart.source = "stub"` 的排盘来源；不新增 React/Vue/Vite 等复杂前端框架；不引入用户系统、历史记录、支付、前端路由或复杂状态管理；Claude 报告格式化、lint、测试命令和结果。

后续每次新增开发任务，先在本节新增或更新：

- 任务名称；
- 建议分支名；
- 分支用途；
- 分支起点；
- 交付后验收人。

## 第一阶段目标

建立 mingmax v0.1 的最小后端闭环：

```text
BirthInfo -> ZiweiChartEngine -> RawChart -> NormalizedChart -> ZiweiAnalysisAgent -> Markdown Report
```

第一阶段优先目标不是完整紫微算法，而是稳定项目结构、接口边界、Prompt 资产、测试策略和 Mock LLM 闭环。

## Claude 开发任务计划

### Task 1: 初始化后端结构和开发依赖

目标：建立 FastAPI + uv + pytest 的基础项目结构。

要求：

- 使用 `uv` 管理依赖，不使用 `pip` 或 `poetry`。
- 添加 FastAPI、Pydantic、pytest、pytest-asyncio、pytest-cov、httpx、Black、isort、flake8。
- 创建 `app/` 和 `tests/` 基础结构。
- 将默认 `main.py` 迁移为 `app/main.py`，根目录 `main.py` 可保留为轻量入口或删除，但不得破坏 `uv run` 使用。
- 更新 `pyproject.toml` 中 Black、isort、pytest 配置。

建议命令：

```bash
uv add fastapi pydantic pydantic-settings
uv add --dev pytest pytest-asyncio pytest-cov httpx black isort flake8
```

验收关注：

- 项目结构符合 `.supports/ARCHITECTURE.md`。
- 依赖通过 uv 管理。
- 无 `pip install` 文档或脚本。

### Task 2: 定义 Schema

目标：定义出生信息、原始命盘、标准命盘、分析结果和 API 响应结构。

建议文件：

- `app/schemas/birth.py`
- `app/schemas/chart.py`
- `app/schemas/analysis.py`

必须覆盖：

- 出生日期时间；
- 性别或阴阳性别字段；
- 出生地或时区字段；
- `RawChart`；
- `NormalizedChart`；
- 宫位、星曜、四化等可扩展结构；
- `AnalysisResult`；
- `FollowupQuestion`；
- `MarkdownReport` 或响应内的 `report_markdown` 字段。

测试要求由 Claude 执行：

- 出生信息合法输入通过；
- 缺失必要字段失败；
- 非法日期、非法时辰或非法枚举失败；
- API 响应模型可序列化。

### Task 3: 实现 Engine 接口和标准化

目标：建立确定性排盘封装边界，不让 LLM 参与排盘。

建议文件：

- `app/engines/ziwei_chart_engine.py`
- `app/engines/chart_normalizer.py`

要求：

- `ZiweiChartEngine` 对外暴露稳定方法，例如 `build_chart(birth_info: BirthInfo) -> RawChart`。
- 第一阶段可使用 fixture/stub 返回可预测 `RawChart`。
- `ChartNormalizer` 将 `RawChart` 转为 `NormalizedChart`。
- 保留未来替换真实紫微库的内部封装点。

测试要求由 Claude 执行：

- Engine 返回确定性 `RawChart`。
- Normalizer 输出结构稳定。
- LLM 不参与排盘流程。

### Task 4: 建立 LLM 抽象和 Mock Client

目标：所有模型调用通过统一抽象层。

建议文件：

- `app/llm/base.py`
- `app/llm/mock.py`

要求：

- 定义 `LLMClient` 协议或抽象基类。
- Mock Client 返回固定结构，供单元测试使用。
- 不在业务代码中直接调用第三方模型 SDK。
- 配置项集中放在 `Settings`，不得硬编码模型名、URL 或 API Key。

测试要求由 Claude 执行：

- Mock Client 可返回固定分析内容。
- Service/Agent 测试不真实调用外部 LLM API。

### Task 5: 创建 Prompt 资产和加载逻辑

目标：Prompt 不散落在业务逻辑中。

建议文件：

- `app/prompts/ziwei_analysis.md`
- `app/prompts/theme_analysis.md`
- `app/prompts/followup_questions.md`
- `app/prompts/report.md`
- `app/agents/prompt_loader.py`

要求：

- Prompt 必须只允许基于给定结构化命盘分析。
- Prompt 必须禁止虚构星曜、宫位、四化、大限、流年。
- Prompt 必须要求区分强结论、弱假设和待确认问题。
- Prompt 必须避免绝对化、恐吓式、宿命论表达。
- 报告 Prompt 必须包含免责声明要求。

测试要求由 Claude 执行：

- Prompt 文件存在。
- Prompt 加载失败时有清晰异常。
- Prompt 文本包含关键安全约束。

### Task 6: 实现 ZiweiAnalysisAgent 和 Service 编排

目标：完成从结构化命盘到分析结果的 LLM 流程。

建议文件：

- `app/agents/ziwei_analysis_agent.py`
- `app/services/analysis_service.py`

要求：

- Agent 接收 `NormalizedChart`，不得接收未结构化出生信息后自行排盘。
- Service 编排 Engine、Normalizer、Agent。
- 输出包含整体分析、主题分析、宫位交叉验证、追问问题和 Markdown 报告。
- 报告包含免责声明。

测试要求由 Claude 执行：

- Service 编排顺序正确。
- Mock LLM 被调用。
- 输出包含免责声明。
- 异常分支有明确错误响应或异常。

### Task 7: 实现 API

目标：提供 v0.1 最小分析接口。

建议文件：

- `app/api/v1/routes_analysis.py`
- `app/api/v1/router.py`
- `app/main.py`

建议接口：

```text
POST /api/v1/ziwei/analyze
```

要求：

- API 层只做请求校验、依赖注入、响应封装。
- 业务流程由 `AnalysisService` 处理。
- 错误响应结构一致。

测试要求由 Claude 执行：

- 合法请求返回 200。
- 非法请求返回 422 或统一错误结构。
- 响应包含标准化命盘摘要、分析结果、追问问题和 Markdown 报告。

### Task 8: 接入真实 LLM Client

目标：在保持统一 LLM 抽象层的前提下，支持真实模型调用，替换 API 运行时默认 Mock 输出。

建议文件：

- `app/llm/openai_compatible.py`
- `app/api/dependencies.py`
- `app/core/config.py`
- `.env.example`
- `tests/test_real_llm_client.py`
- `tests/test_api_analysis.py`
- `.supports/DECISIONS.md`
- `.supports/API_SPEC.md`

要求：

- 新增 `OpenAICompatibleLLMClient` 或等价真实 Client，实现 `LLMClient.generate(prompt: str, context: str = "") -> str`。
- 真实 Client 必须从 `Settings` 读取配置，不得硬编码 API Key、base URL、模型名、wire API 或超时时间。
- 继续保留 `MockLLMClient`，用于单元测试和无 KEY 本地开发。
- API 运行时通过依赖装配选择真实 Client：当 `MINGMAX_LLM_PROVIDER=mock` 时使用 Mock；当 `MINGMAX_LLM_PROVIDER=openai_compatible` 时使用真实 Client。
- 支持至少一种 OpenAI-compatible wire API；建议同时支持：
  - `MINGMAX_LLM_WIRE_API=chat_completions`：`POST {base_url}/chat/completions`
  - `MINGMAX_LLM_WIRE_API=responses`：`POST {base_url}/responses`
- 如果项目运行时使用 `httpx` 调用外部 API，必须将 `httpx` 放入运行时依赖，而不是只放在 dev dependency。
- 外部请求必须设置超时，例如 `MINGMAX_LLM_TIMEOUT_SECONDS=30`。
- 请求失败、非 2xx、响应缺少文本时，必须抛出项目内清晰异常，例如 `LLMClientError`。
- API 层不得直接调用第三方模型 SDK 或 HTTP 客户端，仍由 Service/Agent 通过 `LLMClient` 间接调用。
- LLM 只解释 `NormalizedChart`，不得参与排盘、历法换算、星曜落宫、四化、大限或流年计算。
- 真实 LLM 输出仍必须经过报告免责声明兜底逻辑；报告缺少免责声明时自动补齐。
- 不要提交真实 `.env` 或任何 KEY。

建议配置：

```text
MINGMAX_LLM_PROVIDER=openai_compatible
MINGMAX_LLM_MODEL=<由本机环境配置>
MINGMAX_LLM_API_KEY=<由本机环境配置>
MINGMAX_LLM_BASE_URL=<由本机环境配置，例如 https://api.openai.com/v1 或本地兼容网关>
MINGMAX_LLM_WIRE_API=chat_completions
MINGMAX_LLM_TIMEOUT_SECONDS=30
```

测试要求由 Claude 执行：

- 单元测试必须 mock 外部 HTTP，不得真实调用外部 LLM。
- 覆盖真实 Client 的成功解析、401/403、5xx、超时或网络异常、响应缺少文本等分支。
- 覆盖依赖装配：`MINGMAX_LLM_PROVIDER=mock` 使用 `MockLLMClient`，`openai_compatible` 使用真实 Client。
- 覆盖 API 使用真实 Client 的 mock HTTP 路径，确保 `POST /api/v1/ziwei/analyze` 返回分析文本、主题分析、追问、Markdown 报告。
- 手动集成验证可以真实调用已配置 KEY，并在 `.supports/TASKS.md` 的 Code Review 申请中记录请求样例、响应摘要、脱敏后的配置项和风险。
- 手动集成验证不得把真实 KEY、完整敏感响应或本机私密配置写入仓库。

验收关注：

- Runtime 不再被硬编码到 `MockLLMClient`。
- 真实 Client 不绕过 `LLMClient` 抽象。
- 单元测试不依赖真实 KEY 或外网。
- 手动真实调用结果可复现，且报告包含免责声明。
- `chart.source` 仍标记为 `stub`，不得暗示已经实现真实紫微排盘。

### Task 9: 实现简单静态前端界面

目标：提供一个轻量、可维护、可测试的浏览器界面，优先验证 v0.1 后端闭环，而不是构建完整前端应用。

建议文件：

- `app/web/static/index.html`
- `app/web/static/styles.css`
- `app/web/static/app.js`
- `app/web/__init__.py`
- `app/main.py`
- `tests/test_frontend_static.py`
- `.supports/ARCHITECTURE.md`
- `.supports/API_SPEC.md`
- `.supports/TASKS.md`

实现建议：

- 使用 FastAPI 挂载静态文件，建议路径为 `GET /ui` 或 `GET /` 重定向到前端入口；实际路径由 Claude 结合现有 `app/main.py` 最小改动决定。
- 前端使用原生 HTML、CSS、JavaScript，不引入 React、Vue、Vite、Tailwind、前端路由或复杂状态管理。
- 表单字段与 `AnalysisRequest` 保持一致：
  - `calendar_type`，默认 `solar`，可显示 `lunar` 但提示当前阶段不支持；
  - `birth_datetime`；
  - `gender`；
  - `birth_place`；
  - `timezone`，默认可填 `Asia/Shanghai`；
  - `themes`，支持 `career`、`relationship`、`self_understanding`；
  - `include_followup_questions`；
  - `include_markdown_report`。
- 前端通过 `fetch("/api/v1/ziwei/analyze")` 调用后端，不绕过 API，不直接调用 LLM。
- 页面展示：
  - 加载态；
  - API 错误信息；
  - `chart.chart_id`、`chart.source`、`chart.summary`；
  - `analysis.summary`；
  - `analysis.theme_analyses`；
  - `followup_questions`；
  - `report_markdown`，第一阶段可用 `<pre>` 展示原始 Markdown，不要求引入 Markdown 渲染库。
- 页面必须明确提示：当前排盘结果仍为 stub，仅用于验证分析流程，不代表真实紫微排盘已经完成。
- UI 风格应克制、清晰、偏工具化，避免营销页、复杂视觉资产和不必要动效。

测试要求由 Claude 执行：

- 静态入口可访问，返回 200。
- 静态 CSS/JS 可访问，返回 200。
- API 原有测试继续通过。
- 如添加静态路由或重定向，覆盖对应行为。
- 不新增真实外部 LLM 调用；测试环境继续强制使用 mock provider。

验收关注：

- 是否保持 v0.1 小而清晰，不引入复杂前端工程。
- 前端是否只调用后端 API，不直接参与排盘或 LLM 调用。
- 是否清晰标注 `chart.source = "stub"`。
- 是否正确展示免责声明和错误信息。
- 是否同步更新 `.supports/ARCHITECTURE.md`、`.supports/API_SPEC.md` 或其他受影响文档。

## Claude 执行提示词

```text
你负责开发和测试 mingmax v0.1 第一阶段。开始前必须阅读 AGENTS.md 和 .supports/ 下的所有规范文档。

请先查看 .supports/TASKS.md 的“分支计划”，确认当前任务对应分支。如果分支不存在，请从该任务指定的分支起点新建对应分支后再开发。

本阶段目标是建立最小后端闭环：BirthInfo -> ZiweiChartEngine -> RawChart -> NormalizedChart -> ZiweiAnalysisAgent -> Markdown Report。

约束：
1. 只实现紫微斗数 + LLM Agent 分析闭环，不实现八字、MBTI、多体系交叉验证、用户系统、支付系统、复杂前端、向量数据库或任务队列。
2. 紫微排盘必须由确定性程序或 stub engine 完成，LLM 不得参与排盘、历法换算、星曜落宫、四化、大限或流年计算。
3. 所有 LLM 调用必须通过统一 LLM 抽象层，测试必须使用 Mock LLM Client，不得真实调用外部 LLM API。
4. Prompt 必须独立成文件或清晰隔离的 Prompt 模块，不得散落硬编码在业务逻辑中。
5. 使用 uv 管理依赖，不要使用 pip 或 poetry。
6. 保持小而清晰的 Python 后端结构，不引入 LangChain、LangGraph、CrewAI、向量数据库、任务队列或不必要 ORM。
7. 确定性逻辑必须补充测试。你负责运行测试并记录结果。
8. 按 .supports/DEVELOPMENT_GUIDE.md 的 Commit 与 Push 规则提交和推送；commit message 使用 Conventional Commits。
9. 不得自行 merge；merge 只由项目负责人执行。

完成后请输出：
- 分支名；
- commit 列表；
- 修改文件列表；
- 关键架构决策；
- 测试命令和测试结果；
- 未完成事项或风险。

Codex 只负责后续 code review 和验收，不参与测试执行。
```

## Claude 执行提示词：Branch 5 真实 LLM Client

```text
你负责开发和测试 mingmax v0.1 Branch 5：真实 LLM Client 接入。开始前必须阅读 AGENTS.md 和 .supports/ 下的所有规范文档。

当前分支已经由 Codex 基于 develop 创建：
feature/v0.1-real-llm-client

目标：
让运行时可以通过配置使用真实 LLM，不再总是使用 MockLLMClient；但单元测试仍必须 mock 外部 HTTP，不得依赖真实 KEY 或真实外网。

硬性约束：
1. 紫微排盘仍由 ZiweiChartEngine 完成。当前仍是 source="stub" 的排盘结果，LLM 不得参与排盘、历法换算、星曜落宫、四化、大限或流年计算。
2. 所有真实模型调用必须通过 LLMClient 抽象，不得在 API 层、Service 层或业务逻辑中散落第三方 SDK/HTTP 调用。
3. 不得提交真实 .env、API Key、token 或本机私密配置。
4. 如果运行时使用 httpx，请把 httpx 放入运行时依赖，并同步提交 pyproject.toml 和 uv.lock。
5. Prompt 仍使用 app/prompts/ 下的独立文件。
6. 报告必须包含免责声明；如果真实 LLM 输出缺失免责声明，Agent 必须兜底补齐。
7. 错误要清晰：401/403、5xx、超时、网络错误、响应缺少文本都要转成项目内 LLMClientError 或等价异常。

建议实现：
- 新增 app/llm/openai_compatible.py。
- 在 app/core/config.py 增加：
  - llm_provider
  - llm_wire_api
  - llm_timeout_seconds
- 在 app/api/dependencies.py 根据 settings 选择 MockLLMClient 或 OpenAICompatibleLLMClient。
- 支持 MINGMAX_LLM_WIRE_API=chat_completions 和/或 responses；如果只做一个，优先 chat_completions，并在文档说明。
- 更新 .env.example，不填真实 KEY。
- 更新 .supports/DECISIONS.md 和 .supports/API_SPEC.md 中的真实 LLM 接入约束。

测试要求：
- 单元测试 mock HTTP，不真实请求外部 LLM。
- 覆盖成功、鉴权失败、服务端错误、超时/网络错误、响应缺少文本。
- 覆盖 provider 选择逻辑。
- 覆盖 API 在 mock HTTP 下能返回真实 Client 解析出的内容。

手动集成验证：
- 你可以使用本机已配置的真实 KEY 做一次手动调用。
- 只记录脱敏配置、请求命令、响应摘要、是否包含免责声明。
- 不要把 KEY 或完整敏感响应写入仓库。

完成后请输出：
- 分支名；
- commit 列表；
- 修改文件列表；
- 关键架构决策；
- 单元测试命令和结果；
- 手动真实 LLM 验证命令和脱敏结果；
- 未完成事项或风险。

Codex 只负责后续 code review 和验收，不参与测试执行。
```

## Claude 执行提示词：Branch 6 简单静态前端

```text
你负责开发和测试 mingmax v0.1 Branch 6：简单静态前端界面。开始前必须阅读 AGENTS.md 和 .supports/ 下的所有规范文档。

建议分支：
feature/v0.1-static-frontend

请在 feature/v0.1-real-llm-client 合并后的基线上创建该分支。如果当前基线尚未合并，请先等待项目负责人确认基线。

目标：
为现有 POST /api/v1/ziwei/analyze 提供一个轻量浏览器界面，用于验证出生信息输入、分析选项、请求状态、错误提示和报告展示闭环。

硬性约束：
1. 不引入 React、Vue、Vite、Tailwind、前端路由、复杂状态管理或复杂前端构建体系。
2. 使用 FastAPI 提供静态 HTML/CSS/JS 页面。
3. 前端只调用后端 /api/v1/ziwei/analyze，不直接调用 LLM，不参与排盘，不写业务分析逻辑。
4. 紫微排盘仍由 ZiweiChartEngine 完成。当前 chart.source 仍是 stub，前端必须清晰展示这一点，不能暗示已经完成真实紫微排盘。
5. 不实现用户系统、历史记录、支付、复杂前端、向量数据库或任务队列。
6. 不提交真实 .env、API Key、token 或本机私密配置。
7. 如涉及架构、API 展示或开发命令变化，必须更新对应 .supports/ 文档。

建议实现：
- 新增 app/web/static/index.html。
- 新增 app/web/static/styles.css。
- 新增 app/web/static/app.js。
- 如有需要，新增 app/web/__init__.py。
- 在 app/main.py 挂载静态文件，建议提供 /ui 页面入口，避免影响已有 /api/v1/* 路由。
- 表单字段覆盖 calendar_type、birth_datetime、gender、birth_place、timezone、themes、include_followup_questions、include_markdown_report。
- calendar_type 默认 solar；可以显示 lunar 选项，但要提示 v0.1 当前不支持 lunar。
- 使用 fetch("/api/v1/ziwei/analyze") 调用 API。
- 展示 chart.chart_id、chart.source、chart.summary、analysis.summary、analysis.theme_analyses、followup_questions 和 report_markdown。
- report_markdown 第一阶段可以用 pre 展示原始 Markdown，不需要引入 Markdown 渲染库。
- 页面风格保持克制、工具化、清晰，不做营销页。

测试要求：
- 单元测试或 API 测试覆盖 /ui 或静态入口返回 200。
- 覆盖 CSS/JS 静态资源返回 200。
- 原有 API 测试继续通过。
- 测试环境继续强制 MINGMAX_LLM_PROVIDER=mock，不真实调用外部 LLM。

完成后请输出：
- 分支名；
- commit 列表；
- 修改文件列表；
- 前端入口 URL；
- 关键架构决策；
- 测试命令和测试结果；
- 未完成事项或风险。

Codex 只负责后续 code review 和验收，不参与测试执行。
```

## Code Review 申请

### Branch 2: `feature/v0.1-project-foundation`

**分支名：** `feature/v0.1-project-foundation`

**Commit 列表：**

1. `49cdfb1` — docs: add v0.1 planning docs and规范命名 .supports/ 文档
2. `a199002` — feat: add FastAPI project foundation with health check

**修改文件列表：**

- `AGENTS.md` — 更新完整项目约束
- `.supports/` — 新增 7 个规范文档，删除 3 个旧错名空文档
- `pyproject.toml` — 配置依赖、Black/isort/pytest/hatch build
- `uv.lock` — 依赖锁文件
- `.env.example` — 环境变量示例
- `app/__init__.py`, `app/main.py` — FastAPI 应用入口
- `app/core/config.py` — Settings 配置类
- `app/core/logging.py` — 统一 logger
- `app/api/v1/__init__.py`, `app/api/v1/router.py` — 健康检查路由
- `app/schemas/`, `app/services/`, `app/engines/`, `app/agents/`, `app/llm/`, `app/prompts/` — 空目录占位
- `tests/conftest.py` — httpx AsyncClient fixture
- `tests/test_app.py` — 应用创建测试
- `tests/test_config.py` — 配置默认值测试
- `tests/test_logging.py` — logger 单例测试
- `tests/test_health.py` — 健康检查接口测试

**关键架构决策：**

- Settings 使用 `MINGMAX_` 环境变量前缀，通过 `pydantic-settings` 管理
- 健康检查挂在 `GET /api/v1/health`，符合 API 规范前缀
- `app/main.py` 使用工厂模式 `create_app()`，便于测试和扩展
- 项目使用 `app/` 作为包目录（非 `mingmax/`），通过 hatch build 配置映射

**测试命令和结果：**

```bash
# 格式化
uv run black .     # All done! 15 files left unchanged
uv run isort .     # Skipped 2 files (already sorted)
uv run flake8 app/ tests/ --max-line-length=120  # 0 errors

# 测试
uv run pytest -v   # 7 passed in 0.02s
uv run pytest --cov=app  # 100% coverage, 42 statements
```

**未完成事项或风险：**

- 无。本分支仅搭建基础结构，不涉及紫微业务逻辑。
- `main.py`（根目录）保留但未更新，未来可考虑作为轻量入口或删除。

**请求 Codex review。**

---

### Branch 3: `feature/v0.1-chart-core`

**分支名：** `feature/v0.1-chart-core`

**Commit 列表：**

1. `251e135` — feat: add birth info schemas, chart engine stub and normalizer
2. `5edff35` — docs: add code review request for feature/v0.1-chart-core

**修改文件列表：**

- `app/schemas/birth.py` — BirthInfo Schema（含 CalendarType、Gender 枚举、timezone IANA 校验）
- `app/schemas/chart.py` — RawChart、NormalizedChart、Palace、Star、FourHua Schema
- `app/schemas/analysis.py` — AnalysisResult、FollowupQuestion、AnalysisResponse、AnalysisOptions Schema
- `app/engines/ziwei_chart_engine.py` — ZiweiChartEngine stub（source="stub"，12 宫确定性输出）
- `app/engines/chart_normalizer.py` — ChartNormalizer（RawChart → NormalizedChart）
- `tests/test_birth_schema.py` — BirthInfo 校验测试（9 项：合法/非法/缺失/边界）
- `tests/test_chart_schema.py` — Palace/RawChart/NormalizedChart 序列化测试
- `tests/test_chart_engine.py` — Engine 确定性测试、Normalizer 结构测试（6 项）
- `tests/test_analysis_schema.py` — AnalysisResult/Response 序列化测试

**关键架构决策：**

- Engine stub 显式标记 `source="stub"`（D009 决策），不伪装真实排盘
- LLM 不参与排盘流程，ZiweiChartEngine 只做确定性计算
- BirthInfo 使用 `zoneinfo.ZoneInfo` 校验 IANA 时区格式
- NormalizedChart 携带 summary 字段，供后续 Agent 分析使用
- AnalysisOptions 支持 themes 配置，为 Branch 4 主题分析预留

**测试命令和结果：**

```bash
uv run black --check app/ tests/ main.py   # 29 files unchanged
uv run isort --check-only app/ tests/ main.py  # no changes
uv run flake8 app/ tests/ main.py --max-line-length=120  # 0 errors

uv run pytest -v   # 28 passed in 0.04s
uv run pytest --cov=app  # 100% coverage, 129 statements, 0 miss
```

**未完成事项或风险：**

- 无。本分支仅实现 Schema、Engine stub 和 Normalizer，不涉及 LLM 调用。
- `lunar` calendar_type 已在 Schema 层面接受，但 Engine stub 未区分处理。Branch 4 或后续需在 Service 层增加 `UNSUPPORTED_CALENDAR_TYPE` 校验。
- AnalysisRequest 中 `birth` 字段暂用 `dict`，Branch 4 实现 API 时将替换为 `BirthInfo`。

**请求 Codex review。**

---

### Branch 4: `feature/v0.1-analysis-flow`

**分支名：** `feature/v0.1-analysis-flow`

**Commit 列表：**

1. `b49dbc2` — feat: add LLM abstraction, mock client, prompts, agent, service and API

**修改文件列表：**

- `app/llm/base.py` — LLMClient 抽象基类
- `app/llm/mock.py` — MockLLMClient，含 DISCLAIMER 和 MOCK_ANALYSIS 常量
- `app/core/config.py` — 新增 llm_model、llm_api_key、llm_base_url 配置
- `app/agents/prompt_loader.py` — Prompt 文件加载器，含 PromptLoadError
- `app/agents/ziwei_analysis_agent.py` — Agent 封装 analyze/themes/followup/report
- `app/services/analysis_service.py` — 编排 Engine→Normalizer→Agent 流程
- `app/api/v1/routes_analysis.py` — POST /api/v1/ziwei/analyze 端点
- `app/api/v1/__init__.py` — 注册 analysis_router
- `app/prompts/ziwei_analysis.md` — 基础分析 Prompt（含安全约束）
- `app/prompts/theme_analysis.md` — 主题分析 Prompt
- `app/prompts/followup_questions.md` — 追问生成 Prompt
- `app/prompts/report.md` — 报告生成 Prompt（含免责声明要求）
- `.env.example` — 新增 LLM 配置项
- `tests/test_mock_llm.py` — Mock LLM 测试（3 项）
- `tests/test_prompt_loading.py` — Prompt 加载和安全约束测试（4 项）
- `tests/test_analysis_service.py` — Service 编排测试（5 项）
- `tests/test_api_analysis.py` — API 合法/非法/边界测试（4 项）

**关键架构决策：**

- LLMClient 为抽象基类，MockLLMClient 返回固定内容，真实 Client 未来替换
- API 层通过 Depends 注入 AnalysisService，不直接调用 LLM 或 Engine
- ZiweiAnalysisAgent 只接收 NormalizedChart，不参与排盘
- Prompt 独立文件管理，通过 prompt_loader 加载
- 报告生成后检查是否包含 DISCLAIMER，缺失时自动追加
- Settings 新增 LLM 配置，使用 MINGMAX_ 前缀

**测试命令和结果：**

```bash
uv run black --check app/ tests/ main.py   # 39 files unchanged
uv run isort --check-only app/ tests/ main.py  # no changes
uv run flake8 app/ tests/ main.py --max-line-length=120  # 0 errors

uv run pytest -v   # 48 passed in 0.09s
uv run pytest --cov=app  # 99% coverage, 239 statements, 2 miss
```

**未完成事项或风险：**

- Agent 主题分析结果暂未写入 AnalysisResponse（Mock 返回固定文本，结构化解析留待后续）
- AnalysisService 中 AnalysisResult 的 strong_signals/weak_hypotheses 为 stub 硬编码，待接入真实 LLM 后替换
- 覆盖率 99%：`llm/base.py` 抽象方法声明未覆盖（正常），`ziwei_analysis_agent.py:36` 为免责追加分支
- 未引入超出 v0.1 范围的依赖

**请求 Codex review。**

---

### Branch 5: `feature/v0.1-real-llm-client`

**分支名：** `feature/v0.1-real-llm-client`

**Commit 列表：**

1. `4a9f3c0` — docs: add real llm client branch plan (Codex)
2. `bd54ccd` — feat: add OpenAI-compatible LLM client with configurable provider

**修改文件列表：**

- `app/llm/openai_compatible.py` — OpenAICompatibleLLMClient + LLMClientError/LLMClientConfigError，支持 chat_completions 和 responses
- `app/core/config.py` — 新增 llm_provider、llm_wire_api、llm_timeout_seconds 配置
- `app/api/dependencies.py` — 根据 MINGMAX_LLM_PROVIDER 选择 Mock/Real Client
- `app/api/errors.py` — 统一 API 错误响应构造
- `app/api/v1/routes_analysis.py` — 将 LLMClientError 映射为 LLM_CLIENT_FAILED 错误响应
- `.env.example` — 新增 MINGMAX_LLM_PROVIDER、LLM_WIRE_API、LLM_TIMEOUT_SECONDS
- `pyproject.toml` — httpx 从 dev 移至运行时依赖
- `uv.lock` — 依赖锁文件更新
- `tests/test_real_llm_client.py` — 真实 Client 单元测试（成功/鉴权/服务器/超时/网络/缺内容/非法 JSON/配置错误/responses）
- `tests/test_dependencies.py` — Provider 选择与未知 provider 测试
- `tests/test_api_analysis.py` — LLM_CLIENT_FAILED 运行时错误与依赖装配配置错误响应测试
- `tests/conftest.py` — 测试默认强制使用 mock provider，避免本机 `.env` 触发真实外部调用

**关键架构决策：**

- OpenAICompatibleLLMClient 通过 httpx 调用 `/chat/completions` 或 `/responses`，不依赖 openai SDK
- LLMClientError 统一包装所有错误类型（auth/server/timeout/network/empty）
- `MINGMAX_LLM_PROVIDER=mock` 使用 MockLLMClient，`openai_compatible` 使用真实 Client
- 未知 provider、未知 wire API 或真实 Client 缺少必要配置时不静默退回 mock
- 超时通过 `MINGMAX_LLM_TIMEOUT_SECONDS` 可配置，默认 30s
- 所有调用仍经 LLMClient 抽象，API 层和 Service 层不感知具体实现

**单元测试命令和结果：**

```bash
uv run black --check app/ tests/ main.py   # 43 files unchanged
uv run isort --check-only app/ tests/ main.py  # no changes
uv run flake8 app/ tests/ main.py --max-line-length=120  # 0 errors

uv run pytest -v   # 60 passed in 0.10s
uv run pytest --cov=app  # 99% coverage, 290 statements, 3 miss
```

**手动真实 LLM 集成验证：**

```text
配置（脱敏）：
- MINGMAX_LLM_PROVIDER=openai_compatible
- MINGMAX_LLM_MODEL=glm-5.1
- MINGMAX_LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
- MINGMAX_LLM_API_KEY=sk-***（已配置于本机 .env，未提交）
- MINGMAX_LLM_TIMEOUT_SECONDS=120

简单调用测试：prompt="请用一句话回答：1+1等于几？"
→ 成功，返回 "1+1等于2。"

完整 API 闭环测试（themes=[], followup=false, report=true）：
→ 成功
- Chart source: stub（排盘仍为 stub，未伪装真实排盘）
- Analysis summary: 366 chars（真实 LLM 生成）
- Report: 667 chars，包含免责声明（LLM 自行生成 + Agent 兜底）
- LLM 正确识别 stub 命盘数据为空，提示无法进行实质分析

风险提示：
- 30s 默认超时对完整紫微分析可能不够，建议生产环境设 120s
- 真实 LLM 输出质量取决于模型和 Prompt，stub 命盘下 LLM 会如实说明数据不足
```

**未完成事项或风险：**

- 已支持 `chat_completions` 与 `responses` wire API；真实网关兼容性仍需按所用 provider 手动验证
- 默认超时 30s 可能不够，生产环境建议 120s+，已在 .env.example 中注释说明
- chart.source 仍为 `stub`，LLM 会如实识别并说明数据不足

**请求 Codex review。**

---

### Branch 6: `feature/v0.1-static-frontend`

**分支名：** `feature/v0.1-static-frontend`

**Commit 列表：**

1. `feat: add static frontend for analysis UI`

**修改文件列表：**

- `app/web/__init__.py` — Web 模块初始化
- `app/web/static/index.html` — 前端入口页面（含表单、结果展示、stub 提示、免责声明）
- `app/web/static/styles.css` — 克制工具化样式
- `app/web/static/app.js` — 前端逻辑（表单提交、API 调用、结果渲染、错误展示）
- `app/main.py` — 新增静态文件挂载和根路径重定向
- `tests/test_frontend_static.py` — 前端静态资源测试（7 项）
- `.supports/ARCHITECTURE.md` — 新增 Web 层目录结构和职责说明
- `.supports/API_SPEC.md` — 新增静态前端路由和约束

**关键架构决策：**

- 使用 FastAPI `StaticFiles` 挂载静态资源，路径 `/static/`
- 根路径 `GET /` 307 重定向到 `/static/index.html`
- 前端使用原生 HTML/CSS/JS，不引入 React、Vue、Vite、Tailwind 等复杂前端框架
- 前端只通过 `fetch("/api/v1/ziwei/analyze")` 调用后端 API，不绕过 API 层
- 页面明确标注当前排盘结果为 stub
- 页面展示免责声明
- 支持加载态、API 错误信息、命盘信息、分析摘要、主题分析、追问问题、Markdown 报告
- 农历选项在页面提示当前不支持，提交时阻止

**测试命令和结果：**

```bash
uv run black --check app/ tests/ main.py   # 46 files unchanged
uv run isort --check-only app/ tests/ main.py  # no changes
uv run flake8 app/ tests/ main.py --max-line-length=120  # 0 errors

uv run pytest -v   # 77 passed in 0.20s
uv run pytest --cov=app  # 98% coverage, 365 statements, 9 miss
```

**未完成事项或风险：**

- 无。本分支仅实现静态前端界面，不涉及后端业务逻辑变更。
- Markdown 报告当前以 `<pre>` 原始文本展示，未引入 Markdown 渲染库（符合 v0.1 简单要求）。
- 前端时区偏移计算使用浏览器 Intl API，未来如需精确到分钟偏移可增强。

**请求 Codex review。**

---

## Codex 验收清单

Codex 验收时关注：

- 是否遵守 `AGENTS.md` 和 `.supports/` 约束；
- 是否保持分层清晰；
- API 层是否没有直接调用 LLM 或排盘逻辑；
- Engine 是否承担确定性排盘边界；
- Agent 是否只解释结构化命盘；
- LLM 调用是否经过统一抽象；
- Prompt 是否独立管理并包含安全约束；
- 测试是否由 Claude 执行并报告结果；
- 报告是否包含免责声明；
- 是否引入超出 v0.1 范围的依赖或模块。
