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
  - Branch 7 当时先使用出生地时区下的本地日期与小时，不实现真太阳时校正；Branch 9 已按 D020 补充真太阳时校正；
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

### D020: 真太阳时校正是默认行为

- 状态：已确认
- 决策：Provider 默认始终进行真太阳时校正。如果 `BirthInfo` 提供 `longitude`，使用精确经度计算；如果不提供，从 `timezone` 的 UTC offset 推算近似经度（`longitude ≈ UTC_offset_hours × 15`），此时只有均时差修正，不含经度偏差修正。真太阳时计算限定在 Engine/Provider 层。
- 影响：同一出生时间有无 longitude 可能产生不同排盘结果（因近似经度与实际经度偏差）。对于出生地经度与标准时区经线偏差较大的地区，建议显式提供 longitude。

### D021: 宫位 index 差异降为 warning

- 状态：已确认
- 决策：不同紫微排盘系统的宫位编号起点不同（如从子起 vs 从寅起），`chart_diff` 将 index 差异归类为 warning 而非 error。major_stars、palace name、four_hua 差异仍为 error。
- 影响：使用 chart_diff 对比时，index warning 不影响 `is_match` 判定。

### D022: 借鉴 TS 项目时只吸收结构化事实设计

- 状态：已确认
- 背景：`/home/liam/git/ziwei-doushu` 的 TS 项目在命盘结构、宫位关系、空宫借星、三方四正、星曜分类、前端核验视图等方面有可借鉴设计，但其产品定位、前端框架、SEO 内容和部分断语不符合 mingmax v0.1 范围。
- 决策：Branch 10 只吸收“确定性命盘结构与证据层”的设计思想，优先在 Engine/Normalizer 层补齐可验证事实，再供 LLM 解释。
- 约束：
  - 不迁移 Next.js / React / Tailwind；
  - 不复制参考项目的宿命化断语、合盘知识库或 SEO 内容页；
  - 不让 LLM 计算命宫、身宫、四化、对宫、三方四正、空宫借星等确定性关系；
  - 不一次性移植大型格局规则库，后续如做规则层必须从小型、可测试、低争议规则开始；
  - `.supports/TEST_INFO_EVA.md` 等私密样本仍不得入库或写入测试 fixture。
- 影响：后续 LLM 输出质量优化和前端核验视图应基于 `chart_facts` / `chart_evidence` 等结构化事实，而不是要求模型从原始宫位列表中自行推理。

### D023: 宫位关系和结构化证据属于 Engine 层

- 状态：已确认
- 决策：`chart_relations.py`（对宫、三方四正、空宫借星）和 `chart_facts.py`（结构化证据提取）属于 Engine 层。Normalizer 在标准化时填充宫位关系字段，Agent 通过 `build_chart_facts()` 生成传给 LLM 的 context。
- 影响：Agent 不再直接传递原始 `NormalizedChart` JSON，而是传递只包含结构化事实的 `chart_facts`。LLM 不得重新推算任何确定性关系。

### D024: 前端核验视图前先完成真实链路验证

- 状态：已确认
- 背景：Branch 10 已补充 `chart_facts` 结构化证据层，后续自然方向包括真实样本端到端验证和前端命盘核验视图。
- 决策：Branch 11 优先做真实样本端到端验证与输出校准，暂不做新的前端命盘盘面。
- 原因：如果 `chart_facts -> Prompt -> LLM 输出` 仍存在证据引用错漏、泛化分析或不安全表达，前端核验视图会放大用户对错误输出的信任。先建立脱敏、可复跑的真实链路验证，再做前端展示。
- 影响：
  - 新增 evidence validator 时应保持纯函数、可单测，不真实调用外部 LLM；
  - 私密样本只允许本地手动验证，不进入仓库或自动化测试；
  - 验证产物只记录脱敏摘要和 issue 统计；
  - 前端增强推迟到端到端链路可信度提高之后。

### D025: 前端命盘核验视图继续使用原生静态前端

- 状态：已确认
- 背景：Branch 11 已完成真实链路验证与输出校准，下一步需要让用户和开发者直观看到后端实际排出的命盘。
- 决策：Branch 12 在现有 `app/web/static/` 原生 HTML/CSS/JS 前端中实现轻量 4x4 十二宫核验视图，不引入 React、Vue、Vite、Tailwind 或新的前端构建链。
- 约束：
  - 前端只消费 API 返回的 `chart` 字段，不计算排盘、对宫、三方四正或空宫借星；
  - 不保存出生信息历史，不生成分享链接，不写入 localStorage/sessionStorage/cookie；
  - 缺失的 `five_elements_class`、`lunar_info` 等字段必须显示为暂未提供，不得前端编造；
  - 该视图定位为排盘核验工具，不是营销页或复杂产品重构。
- 影响：后续如果需要更复杂前端框架，应另开决策，不得在 Branch 12 中顺手引入。

### D026: 证据 ID 体系与增强验证框架

- 状态：已确认
- 背景：Branch 13 在已有的基础验证器（伪造星曜/宫位/四化检测、绝对化表达检测、免责声明检查）基础上，进一步约束 LLM 输出的证据可追溯性和绑定一致性。
- 决策：
  - `chart_facts.evidence_index` 为每条结构化事实提供稳定 ID（palace/star/mutagen/relation/borrowed 类型），供 LLM 引用和验证器校验；
  - 验证器新增：伪造证据 ID 检测、星曜-宫位绑定一致性检查、四化-宫位绑定一致性检查、不支持时间层检测；
  - Prompt 层统一要求 LLM 引用证据 ID，禁止引用大限/流年等时间层，禁止绝对化表达，要求星曜/四化描述与 chart_facts 绑定一致；
  - 报告新增"不确定性说明"章节。
- 约束：
  - 验证器保持纯函数、不调用外部 LLM；
  - 证据 ID 格式在 `chart_facts.py` 中集中定义，验证器和 Prompt 通过字符串模式引用，不硬编码业务规则；
  - 不引入知识库、格局规则库或命盘解读库，v0.1 仅做证据框架和约束层。
- 影响：后续 LLM 输出质量和可追溯性提升；如果未来添加新证据类型，需同步更新 chart_facts、validator 和 Prompt。

### D027: 命盘事实完整度审计与 Prompt 输入增强

- 状态：已确认
- 背景：Branch 13 解决了 LLM 输出证据追踪问题，但 `chart_facts` 仍偏骨架化，与文墨天机的完整盘面信息相比信息密度不足。
- 决策：
  - 先审计"文墨天机字段 -> iztro-py 原始输出 -> RawChart/NormalizedChart -> chart_facts/Prompt"的信息流，补齐已经可获得但未传给 LLM 的事实；
  - 将星曜从简单字符串升级为结构化事实对象，包含 `name`、`brightness`、`category`、`evidence_id`；
  - 补充宫位天干地支（`heavenly_stem`、`earthly_branch`）到 `chart_facts`；
  - 保持 `evidence_index` 与结构化星曜/四化事实中的 `evidence_id` 一致；
  - Prompt 更新为"完整事实包"思路，描述可用的星曜亮度、宫位干支、四化、宫位关系等事实；
  - 明确记录 v0.1 不支持的字段（大限、流年、四柱、神煞等），Prompt 和 validator 继续禁止 LLM 自行补算。
- 约束：
  - 不伪造或补算 provider 未提供的字段；
  - 不改动公开 API 响应结构；
  - 不引入知识库、格局规则库或复杂 Agent 框架。
- 影响：LLM 输入信息密度提升，基于更完整的结构化事实进行分析；审计文档记录了已支持、可获得但未暴露、provider 未确认、v0.1 不支持的字段状态。

### D028: provider 字段取舍必须先基于原始输出快照

- 状态：已确认
- 背景：Branch 13/14 提前围绕 `chart_facts`、Prompt 和 evidence 体系扩展，但没有先系统落盘和审计 `iztro-py` 原始返回对象，导致部分字段长期停留在 `provider_unknown`，字段取舍依据不够扎实。
- 决策：
  - 后续涉及紫微排盘字段、Prompt 输入事实、schema 扩展或 provider 支持边界时，必须先生成 `iztro-py` 原始输出的可序列化快照；
  - 快照用于审计 provider 顶层对象、palace、star、四化、大限、五行局、命宫/身宫、农历、四柱等字段是否真实存在；
  - 字段进入 `RawChart`、`NormalizedChart`、`chart_facts` 或 Prompt 之前，必须先明确其来源：`iztro-py` 原生、mingmax 派生、额外历法库、人工规则表或暂不支持；
  - 私密出生样本只允许输出到本地 ignored 路径，仓库内只能保留合成样本或脱敏审计结论；
  - 不再根据当前 schema 或 Prompt 需求反推 provider 能力，也不让 LLM 补算 provider 未确认字段。
- 影响：Branch 15 先做 provider 原始快照和字段能力审计，再决定是否扩展正式业务结构；后续 Prompt 丰富度必须建立在确定性事实边界之上。

### D029: 丰富事实输入优先于最小事实约束

- 状态：已确认
- 背景：Branch 13/14 先强化了 evidence 与 validator，但事实输入仍偏瘦；Branch 15 已确认 `iztro-py` 原生提供农历日期、四柱字符串、命身宫地支、身宫类型、星曜 scope、大限 decadal 等更多信息。
- 决策：
  - `iztro-py` 原生事实应优先完整吸收到内部结构，再由 `chart_facts` 组织为 rich facts package；
  - LLM 输入应尽可能丰富，但必须带来源、支持状态和分析边界，而不是用减少事实输入来保证安全；
  - validator 的职责是拦截伪造事实、错误绑定、越界分析和不安全表达，不应成为削弱事实输入的手段；
  - 大限数据可以进入内部结构和 `chart_facts`，并开放"大限区间级辅助分析"；但流年、流月、流日、流时仍不支持，不能预测具体年份或具体事件发生；
  - `chinese_date` 可作为四柱字符串事实进入命盘背景，但 v0.1 仍不开放八字分析。
- 影响：Branch 16/17 合并为一次较大的事实层与大限基础分析能力重构；前端参考文墨天机的信息密度设计另开后续分支，不与本轮混做。

### D030: 桌面端高信息密度命盘工作台

- 状态：已确认
- 背景：Branch 12 的前端是简单表单 + 840px 线性布局，未展示 Branch 16/17 新增的 metadata、decadal、scope、structured analysis 等字段。
- 决策：Branch 18 将前端升级为桌面工作台布局（max-width 1440px），4x4 盘面 + 侧边详情面板并排，结构化分析段落替代 JSON.stringify 展示。
- 约束：
  - 仅桌面端，不做移动端适配（移除 600px media query）；
  - 不引入 React/Vue/Vite/Tailwind 或前端构建链；
  - 所有动态内容使用 textContent/DOM 节点，不使用 innerHTML（XSS 安全）；
  - 不写入 localStorage/sessionStorage/cookie；
  - 前端只消费 API 返回字段，不计算排盘关系。
- 影响：前端展示信息密度显著提升，current decadal 宫位高亮，分析结果按信号强度分层展示。
