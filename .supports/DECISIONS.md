# DECISIONS.md

## 已确认决策

### D001: v0.1 只做紫微斗数 + LLM Agent 分析闭环

- 状态：已确认
- 原因：先建立确定性排盘、结构化命盘和 LLM 分析的最小闭环，避免过早扩展多体系。
- 影响：不得在 v0.1 中引入八字、MBTI、大五人格、多体系交叉验证等模块。

### D002: 紫微排盘必须由确定性程序完成

- 状态：已确认
- 原因：LLM 不适合承担历法换算、星曜落宫、四化、大限、流年等确定性计算。
- 正确流程：

```text
BirthInfo -> ZiweiChartEngine -> RawChart -> NormalizedChart -> ZiweiAnalysisAgent
```

### D003: 所有 LLM 调用必须经过统一 LLM 抽象层

- 状态：已确认
- 原因：避免第三方 SDK 调用散落在业务代码中，便于替换模型、mock 测试和控制安全边界。
- 影响：API 层、Service 层、Engine 层不得直接调用第三方模型 SDK。

### D004: Prompt 是核心资产，必须独立管理

- 状态：已确认
- 原因：Prompt 决定 LLM 输出边界、结构和安全性。
- 影响：Prompt 不得大量硬编码在业务逻辑中，应放在独立文件或 Prompt 模块中。

### D005: 技术栈保持轻量

- 状态：已确认
- 选型：
  - Python >=3.14
  - FastAPI
  - uv
  - pytest / pytest-asyncio / pytest-cov
  - Black / isort / flake8
- 影响：默认不引入 LangChain、LangGraph、CrewAI、向量数据库、任务队列、不必要 ORM 或复杂前端框架。

### D006: 评审与验收职责独立

- 状态：已确认
- 决策：Claude 负责开发和测试执行，Codex 负责 code review 和验收。
- 影响：Codex 验收时可以检查测试结果、代码结构、文档和行为约束，但不主动参与测试执行。

### D007: merge 只由项目负责人执行

- 状态：已确认
- 决策：Claude 可以开发、测试、commit、push；Codex 可以 review 和验收；merge 只由项目负责人执行。
- 影响：Claude 和 Codex 都不得自行 merge 分支。

### D008: 旧错名 `.supports/` 空文档迁移为规范命名文档

- 状态：已确认
- 背景：仓库曾存在 `.supports/CONTEXT_PROJECT.md`、`.supports/DECISION.md`、`.supports/TEST.md`，它们为空且不符合 `AGENTS.md` 约定。
- 决策：以 `.supports/PROJECT_CONTEXT.md`、`.supports/DECISIONS.md`、`.supports/TASKS.md` 等规范命名文档为准；旧错名空文档可以删除。
- 影响：Claude 不应继续向旧错名文档写入内容。

### D009: 第一阶段 Engine stub 必须显式标记

- 状态：已确认
- 决策：第一阶段允许使用 Engine stub 建立闭环，但 stub 结果必须通过 `source = "stub"`、`is_stub = true` 或等价字段显式标记。
- 影响：stub 结果不得伪装为真实紫微排盘结果；报告或 API 响应不得暗示 stub 已完成真实排盘。

### D010: 真实 LLM 接入必须可配置且仍经过 LLMClient 抽象

- 状态：已确认
- 决策：Branch 5 开始支持真实 LLM 调用。运行时通过 `MINGMAX_LLM_PROVIDER` 选择 `mock` 或 `openai_compatible`，真实调用必须经过 `LLMClient` 抽象。`openai_compatible` 支持 `MINGMAX_LLM_WIRE_API=chat_completions` 和 `responses`。
- 影响：API 层、Service 层和 Agent 以外的业务逻辑不得直接调用第三方模型 SDK 或 HTTP API；单元测试不得真实访问外部 LLM。

### D011: 真实 LLM 只负责解释，不负责排盘

- 状态：已确认
- 决策：即使接入真实模型，紫微排盘仍由 `ZiweiChartEngine` 完成。当前阶段如果 Engine 仍是 stub，则响应必须保留 `source = "stub"`。
- 影响：Prompt、Agent 和真实 LLM Client 不得承担历法换算、安星、定宫、四化、大限、流年等确定性逻辑。

### D012: 真实 KEY 和本机私密配置不得进入仓库

- 状态：已确认
- 决策：`.env.example` 可以记录变量名和空值示例，真实 `.env`、API Key、token、本机私密 base URL 不得提交。
- 影响：Claude 进行手动真实 LLM 验证时，只能记录脱敏配置和响应摘要。

### D013: LLM 配置错误不得静默降级

- 状态：已确认
- 决策：未知 `MINGMAX_LLM_PROVIDER`、未知 `MINGMAX_LLM_WIRE_API` 或真实 Client 缺少必要配置时必须抛出清晰错误，并由 API 映射为 `LLM_CLIENT_FAILED`。
- 影响：生产环境配置拼写错误不会伪装为 MockLLMClient 成功响应。

### D014: Branch 7 开始替换 Engine stub 为真实确定性排盘实现

- 状态：已确认
- 决策：Branch 7 的目标是让 `ZiweiChartEngine` 不再返回 `source = "stub"` 的空排盘，而是优先通过 `iztro-py` 适配层返回真实、确定性的紫微排盘结构。
- 来源：旧项目 `/home/liam/ideas/mingmind/agents/ziwei_agent.py` 已使用 `from iztro_py import astro`，依赖名为 `iztro-py>=0.3.4,<1`。
- 约束：
  - LLM 仍不得参与排盘、历法换算、安星、定宫、四化、大限或流年计算；
  - `iztro-py` 必须封装在 Engine/Provider 层，不得泄漏到 API、Service、Agent 或 LLM 层；
  - 引入 `iztro-py` 必须使用 `uv add "iztro-py>=0.3.4,<1"` 管理，并提交 `pyproject.toml` 与 `uv.lock`；
  - `iztro-py` 旧项目用法为 `astro.by_solar_hour(solar_date, hour, gender)`，其中 `gender` 只支持 `男` / `女`；当前 `Gender.unknown` 应返回清晰不支持错误或等价错误，不得静默降级为任一性别；
  - 当前 v0.1 先使用出生地时区下的本地日期与小时，不实现真太阳时校正；如后续需要真太阳时，应作为独立任务处理；
  - `iztro-py` metadata 标注 Python 3.8-3.12，但旧项目 Python 3.13 环境可安装；mingmax 要求 Python >=3.14，因此 Branch 7 必须通过 `uv add` 和完整测试验证 Python 3.14 兼容性；
  - 若 v0.1 真实引擎只支持部分规则，必须在 `.supports/ARCHITECTURE.md`、`.supports/API_SPEC.md` 或 `.supports/TASKS.md` 中记录支持范围和未支持边界。
- 影响：前端和 API 响应不得继续固定暗示当前一定是 stub；应根据 `chart.source` 动态展示排盘来源。

## 待确认决策

### P001: 紫微排盘底层实现来源

- 选项：自研最小规则引擎、封装第三方库、先以内部接口 + fixture stub 建立闭环。
- 当前状态：Branch 1-6 已完成接口和测试替身闭环；Branch 7 开始进入真实确定性排盘实现阶段。
- 结论：优先采用旧项目已验证过的 `iztro-py>=0.3.4,<1`，通过内部 provider 适配到当前 `RawChart` / `NormalizedChart` 结构；仅当 Python 3.14 兼容性或输出质量验证失败时，再退回 v0.1 最小内部规则引擎。

### P002: 真实 LLM Provider 细节

- 选项：OpenAI-compatible `chat_completions`、OpenAI-compatible `responses`、本地兼容网关。
- 要求：具体 provider 可由本机环境配置决定；代码只依赖项目内 `LLMClient` 抽象和配置项。

### D017: Branch 8 LLM 输出必须通过 JSON 契约解析

- 状态：已确认
- 决策：基础分析、主题分析和追问问题等 LLM 输出必须按项目定义的 JSON 契约解析为内部 Schema；不得把模型返回的整段 Markdown 直接塞入 `observations`、`question` 等结构字段。Agent 负责解析，Service 只编排。
- 影响：模型返回非 JSON、空内容、缺少必填字段、字段类型错误时，应返回 `LLM_OUTPUT_INVALID`（HTTP 502），不能静默拼装伪成功结果。
- 清理：Service 不再硬编码 `uncertainty="mock"` 或 `reason="mock"`；MockLLMClient 返回符合 JSON 契约的固定内容。

### D018: Prompt 必须显式要求 JSON-only 输出

- 状态：已确认
- 决策：基础分析、主题分析和追问问题的 Prompt 必须明确要求只输出 JSON（object 或 array），不要 Markdown、不要代码块包裹。
- 影响：Agent 解析层可剥离常见模型误输出的代码块包裹，但 Prompt 侧应尽量消除这种需求。

### D019: 私密验证样本不得进入仓库

- 状态：已确认
- 决策：用于排盘准确性验证的私密出生信息和参考命盘文件（如 `.supports/TEST_INFO_EVA.md`）必须通过 `.gitignore` 排除，不得提交到仓库。自动化测试只使用合成 fixture，不使用私密样本。
- 影响：本地验证脚本只输出脱敏差异统计；验证结果记录在 TASKS.md 中，不包含真实出生日期、地点、经度或完整宫位文本。

### D020: 真太阳时校正基于经度触发

- 状态：已确认
- 决策：当 `BirthInfo` 提供 `longitude` 时，Provider 自动计算真太阳时校正（均时差 + 经度校正）确定出生时辰；不提供 `longitude` 时使用钟表时间。真太阳时计算限定在 Engine/Provider 层。
- 影响：同一出生时间有无 longitude 可能产生不同排盘结果；API 文档和前端需明确标注是否启用了真太阳时。

### D021: 宫位 index 差异降为 warning

- 状态：已确认
- 决策：不同紫微排盘系统的宫位编号起点不同（如从子起 vs 从寅起），`chart_diff` 将 index 差异归类为 warning 而非 error。major_stars、palace name、four_hua 差异仍为 error。
- 影响：使用 chart_diff 对比时，index warning 不影响 `is_match` 判定。
