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

## 已完成任务摘要

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

### Branch 4: LLM 分析闭环

- 分支名：`feature/v0.1-analysis-flow`
- 目标：建立 Mock LLM、Prompt、Agent、Service、API 和 Markdown 报告闭环。
- 关键交付：`LLMClient` 抽象、`MockLLMClient`、Prompt loader、`ZiweiAnalysisAgent`、`AnalysisService`、`POST /api/v1/ziwei/analyze`。
- 重要决策：所有 LLM 调用经过 `LLMClient`；Prompt 独立文件；报告缺少免责声明时 Agent 兜底补齐。

### Branch 5: 真实 LLM Client

- 分支名：`feature/v0.1-real-llm-client`
- 目标：支持通过配置使用真实 OpenAI-compatible LLM，不再运行时硬编码 Mock。
- 关键交付：`app/llm/openai_compatible.py`、`llm_provider` / `llm_wire_api` / `llm_timeout_seconds` 配置、依赖装配、LLM 错误映射。
- 重要决策：`MINGMAX_LLM_PROVIDER=mock` 使用 Mock；`openai_compatible` 使用真实 Client；未知 provider/wire API/缺配置不得静默退回 mock。
- 遗留风险：真实输出质量依赖 Prompt；默认 30s 超时对完整分析可能偏短，生产建议 120s。

### Branch 6: 简单静态前端

- 分支名：`feature/v0.1-static-frontend`
- 目标：提供原生 HTML/CSS/JS 前端，用于验证出生信息输入、分析选项、错误提示和报告展示闭环。
- 关键交付：`app/web/static/index.html`、`styles.css`、`app.js`，FastAPI 静态文件挂载，根路径重定向。
- 重要决策：不引入 React/Vue/Vite/Tailwind；前端只调用 `/api/v1/ziwei/analyze`，不参与排盘或 LLM 调用。

### Branch 7: 真实紫微排盘引擎

- 分支名：`feature/v0.1-real-chart-engine`
- 目标：替换运行时 stub 排盘，使用 `iztro-py>=0.3.4,<1` 作为真实确定性紫微排盘 provider。
- 关键交付：`app/engines/providers/iztro_provider.py` 封装 `iztro-py`；`RawChart.source` 改为 `iztro_py`；前端根据 `chart.source` 展示排盘来源；`pyproject.toml` / `uv.lock` 增加依赖。
- 支持范围：公历输入、`male` / `female`、12 宫、主星/辅星/杂曜、天干/地支、四化。
- 未支持范围：农历输入、`Gender.unknown`、真太阳时校正、大限、流年。
- 遗留风险：`iztro-py` metadata 标注 Python 3.8-3.12，但已在 Python 3.14 下安装运行；后续升级依赖时需重新验证。

### Branch 8: LLM 输出质量与失败兜底

- 分支名：`feature/v0.1-llm-output-contract-and-fallback`
- 目标：修通真实 LLM 工作流，建立基础分析、主题分析和追问问题的 JSON 输出契约、结构化解析和失败兜底。
- 关键交付：`LLMOutputParseError`、JSON object/array 解析、`LLM_OUTPUT_INVALID` 502 错误映射、Prompt JSON-only 约束、MockLLMClient 分 prompt 返回契约化内容。
- 重要决策：Agent 负责解析 LLM 输出，Service 只编排；模型返回非 JSON、缺字段或字段类型错误时不得伪成功。
- 测试摘要：当时 `uv run black --check .`、`uv run isort --check-only .`、`uv run flake8 .`、`uv run pytest -q` 均通过，测试为 `123 passed`。
- 遗留风险：真实 LLM 输出质量仍依赖 prompt 和模型稳定性；报告 Markdown 暂不做结构化解析。

### Branch 9: 私密样本驱动的排盘准确性基准

- 分支名：`feature/v0.1-chart-accuracy-baseline`
- 目标：建立排盘准确性验证工具链，修复真太阳时偏差导致宫位错误，通过本地私密样本验证排盘正确性。
- 关键交付：`chart_diff.py` 结构化命盘对比工具；`time_calibration.py` 真太阳时计算；`BirthInfo.longitude`；本地私密样本验证脚本；排盘准确性相关测试。
- 重要决策：私密验证样本不得进入仓库；宫位 index 差异按 warning 处理；真太阳时默认启用，有 longitude 时精确计算，无 longitude 时按 timezone 推算近似经度。
- 测试摘要：当时 `uv run black --check .`、`uv run isort --check-only .`、`uv run flake8 .`、`uv run pytest -q` 均通过，测试为 `150 passed`。
- 遗留风险：均时差为近似值；大限、流年、流月、流日、流时暂未支持；农历输入和 `Gender.unknown` 仍不支持。

### Branch 10: 命盘结构与证据层重构

- 分支名：`task-v0.1-chart-structure-evidence-refactor`
- 目标：基于 TS 参考项目的结构设计，新增确定性宫位关系和 `chart_facts` 证据层，让 LLM 基于程序计算出的事实解释命盘。
- 关键交付：`chart_relations.py`、`chart_facts.py`、`NormalizedChart`/`Palace` 关系字段、Agent context 改为结构化证据、Prompt 证据约束、相关测试和文档。
- 重要决策：宫位关系和结构化证据属于 Engine/Normalizer；Agent 不再传原始 chart JSON；LLM 不得推算对宫、三方四正、空宫借星等确定性关系。
- 测试摘要：Claude 提交前已执行格式化、lint 和测试；Codex review 后问题已在合入 develop 前修复。
- 遗留风险：`chart_facts` 仍是 dict 结构，后续如继续扩展应考虑 TypedDict 或 Pydantic schema；大限、流年、流月、流日、流时仍未支持。

### Branch 11: 真实样本端到端验证与输出校准

- 分支名：`feature/v0.1-e2e-validation-and-calibration`
- 目标：建立脱敏、可复跑的真实样本端到端验证链路，检查 `chart_facts -> Prompt -> LLM 输出` 的证据一致性和安全表达。
- 关键交付：`scripts/verify_e2e_real_sample.py`、`app/agents/analysis_evidence_validator.py`、Prompt 证据约束增强、mock/real LLM 验证路径、相关测试和文档。
- 重要决策：前端核验视图之前先完成真实链路验证；validator 只检查事实引用、安全表达和免责声明，不充当紫微断语正确性裁判。
- 测试摘要：Claude 提交前已执行格式化、lint 和测试；Codex review 后 P1/P2 问题已修复并合入 develop。
- 遗留风险：validator 目前主要做全局名称存在性检查，尚不能判断”某星是否真的落在某宫”这类宫星绑定关系错误。

### Branch 12: 前端命盘核验视图

- 分支名：`task-v0.1-chart-verification-view`
- 目标：在现有原生 HTML/CSS/JS 前端中新增轻量 4x4 十二宫命盘核验视图，让用户直观看到后端排出的紫微盘。
- 关键交付：`index.html` 命盘核验区（summary/grid/detail）、`styles.css` 4x4 CSS Grid 布局与响应式、`app.js` 宫位渲染与详情面板、iztro provider 宫位级四化完整捕获修复、前端测试（HTML 结构、JS 渲染、badge、点击详情、缺失字段、无 localStorage）。
- 重要决策：前端只消费 API 返回的 chart，不计算排盘；宫位 index 到网格位置为固定常量映射；不引入前端框架。
- 测试摘要：`uv run black --check .`、`uv run isort --check-only .`、`uv run flake8 .`、`uv run pytest -q` 均通过，测试为 `225 passed`。
- 遗留风险：iztro 宫位级四化虽已修复为完整捕获，但前端依赖后端正确填充 `palace.four_hua`；大限、流年、流月、流日、流时仍未支持。

### Branch 13: LLM 分析能力增强：分析框架、证据绑定与安全校验

- 分支名：`feature/v0.1-llm-analysis-evidence-framework`
- 目标：让 LLM 输出基于可追溯 evidence id，并强化 validator 对伪造证据、宫星绑定、四化绑定和未支持时间层的拦截。
- 关键交付：`chart_facts.evidence_index`、增强版 `analysis_evidence_validator.py`、Prompt evidence id/禁止时间层约束、MockLLMClient 适配、相关测试和文档。
- 重要决策：Branch 13 不引入知识库、格局规则库或复杂 Agent 框架；本轮只做证据框架和约束层。
- 测试摘要：Codex 复审时 `uv run black --check .`、`uv run isort --check-only .`、`uv run flake8 .`、`uv run pytest -q` 均通过，测试为 `250 passed`。
- 遗留风险：自然语言绑定识别仍是保守规则，无法覆盖所有中文表达变体；该风险不阻塞本轮合入，后续可迭代。

## 当前任务

### Branch 14: 命盘事实完整度审计与 Prompt 输入增强

- 建议分支名：`feature/v0.1-chart-facts-completeness-audit`
- 负责人分工：Claude 负责开发、测试、commit、push；Codex 负责 code review 和验收；merge 只由项目负责人执行。

#### 背景与反思

Branch 13 已解决“LLM 输出能否被证据追踪和 validator 拦截”的第一层问题，但它并没有充分解决“LLM 拿到的命盘事实是否足够完整”的问题。

用户最初设想与文墨天机类似：先得到足够准确、足够完整的星盘信息，再放进 Prompt，让 LLM 负责解释、组织、表达和建议。当前 mingmax 已经采用更工程化的方式：

```text
准确排盘 -> NormalizedChart -> chart_facts -> evidence id -> Prompt -> LLM -> validator -> 前端展示
```

但当前 `chart_facts` 仍偏骨架化，和文墨天机 Prompt 中的完整盘面信息相比，信息密度明显不足。即使把 `major_stars: ["紫微"]` 升级为结构化对象，也只是补了星曜保真，不等于追平文墨天机的完整信息。

本轮核心判断：

> Branch 14 不应盲目加字段，而应先审计“文墨天机字段 -> iztro-py 原始输出 -> RawChart/NormalizedChart -> chart_facts/Prompt”的信息流，补齐已经可获得但未传给 LLM 的事实，并明确记录不可支持字段。

#### 目标

1. 建立一份命盘事实完整度审计文档，对比文墨天机参考字段、`iztro-py` 原始输出、当前 `RawChart` / `NormalizedChart`、当前 `chart_facts` / Prompt 输入。
2. 补齐“底层 provider 已经提供或当前 schema 已经保留，但 `chart_facts` 没有传给 LLM”的字段。
3. 将星曜从简单字符串升级为结构化事实对象，至少包含 `name`、`brightness`、`category`、`evidence_id`。
4. 将宫位基础信息、星曜信息、宫位四化、借星、对宫、三方四正等 Prompt 输入整理成更接近“完整命盘事实包”的结构。
5. 明确记录文墨天机有、但当前 v0.1 不支持或 provider 不提供的字段，Prompt 和 validator 必须继续禁止 LLM 自行补算。

#### 非目标

- 不实现大限、流年、流月、流日、流时计算。
- 不实现四柱、神煞、十二长生、命主、身主、子年斗君、自化、飞宫四化等 provider 未确定支持的字段。
- 不把 `.supports/TEST_INFO_EVA.md` 的完整命盘文本或个人信息写入仓库。
- 不照搬文墨天机的多流派大而全断语、逐年吉凶、重大事件时间范围。
- 不引入知识库、格局规则库、复杂 Agent 框架或复杂前端框架。
- 不改动公开 API 响应结构，除非审计后确认必要，并同步更新 `.supports/API_SPEC.md`。
- 不提交、打印或记录 `.supports/TEST_INFO_EVA.md` 中的个人信息、完整命盘文本或任何可识别隐私内容。

#### 参考材料

- 必读：
  - `AGENTS.md`
  - `.supports/PROJECT_CONTEXT.md`
  - `.supports/DECISIONS.md`
  - `.supports/ARCHITECTURE.md`
  - `.supports/PROMPT_GUIDE.md`
  - `.supports/API_SPEC.md`
  - `.supports/DEVELOPMENT_GUIDE.md`
  - `.supports/ZIWEI_TS_REFERENCE_REVIEW.md`
- 可本地参考但不得提交内容：
  - `.supports/TEST_INFO_EVA.md`
- 参考项目：
  - `/home/liam/git/ziwei-doushu/lib/ziwei/types.ts`
  - `/home/liam/git/ziwei-doushu/lib/ziwei/algorithm.ts`
  - `/home/liam/git/ziwei-doushu/lib/ziwei/constants.ts`
  - `/home/liam/git/ziwei-doushu/lib/ziwei/sihua.ts`

#### 建议文件改动

- 新增：`.supports/CHART_FACTS_COMPLETENESS_AUDIT.md`
  - 记录字段完整度审计矩阵。
  - 建议表格列：
    - `字段/信息类别`
    - `文墨天机参考是否包含`
    - `iztro-py 原始输出是否可获得`
    - `RawChart/NormalizedChart 是否保留`
    - `chart_facts/Prompt 是否传入`
    - `本轮处理结论`
  - 字段至少覆盖：
    - 基本信息：性别、经度、钟表时间、真太阳时、农历时间；
    - 四柱：节气四柱、非节气四柱；
    - 命盘身份：五行局、命主、身主、子年斗君、身宫；
    - 十二宫：宫名、天干、地支、主星、辅星、小星/杂曜；
    - 星曜状态：亮度、类别、生年四化、自化/向心/离心；
    - 宫位关系：对宫、三方四正、空宫借星；
    - 神煞：岁前星、将前星、十二长生、太岁煞禄；
    - 时间层：大限、小限、流年、限流叠宫。
  - 审计文档只能记录字段类别和支持状态，不得粘贴私密样本的完整命盘内容。

- 修改：`app/engines/providers/iztro_provider.py`
  - 审计 provider 当前从 `iztro-py` 原始对象中读取了哪些字段。
  - 如 `iztro-py` 原始输出中已存在星曜亮度、星曜类别、宫干支、农历信息等字段但当前未透传，应补齐到 `RawChart` / `Palace`。
  - 不要在 provider 中实现 LLM 分析或断语逻辑。

- 修改：`app/schemas/chart.py`
  - 如现有 `Star` / `Palace` / `NormalizedChart` 已能承载字段，优先复用。
  - 仅当 provider 可稳定提供且 Prompt 有明确需求时，才新增字段。
  - 允许优先补齐：
    - `Star.brightness`
    - `Star.category`
    - `Palace.heavenly_stem`
    - `Palace.earthly_branch`
    - `NormalizedChart.lunar_info`
    - 现有 schema 中已定义但未完整进入 `chart_facts` 的字段。

- 修改：`app/engines/chart_facts.py`
  - 将宫位事实升级为更完整的 Prompt 输入结构。
  - 星曜字段建议从字符串列表升级为对象列表：
    - `{"name": "紫微", "brightness": "庙", "category": "major", "evidence_id": "star:0:紫微"}`
  - 保持 `evidence_index` 与星曜对象中的 `evidence_id` 一致。
  - 对宫、三方四正、空宫借星、四化等现有事实继续保留。
  - 如果为了兼容旧 Prompt/测试保留简单字符串字段，也必须新增结构化字段，命名需清晰，例如 `major_star_facts`。

- 修改：`app/prompts/ziwei_analysis.md`
  - 明确 `chart_facts` 是“完整可用事实包”，模型必须优先使用星曜亮度、宫位干支、四化、对宫、三方四正等已提供事实。
  - 继续禁止分析未支持的大限、流年、神煞、四柱等字段。
  - 不得因为参考文墨天机的完整盘面风格，就要求模型自行补算未提供字段。

- 修改：`app/prompts/theme_analysis.md`
  - 主题分析应优先引用结构化星曜事实和 evidence id。
  - 证据不足或字段未支持时必须降级表达。

- 修改：`app/prompts/report.md`
  - 报告可以更充分使用完整事实包，但不得输出 unsupported 字段。

- 修改：`app/agents/ziwei_analysis_agent.py`
  - 如 `chart_facts` 增大明显，需要保证 context 仍为结构化 JSON。
  - 不在 Agent 中写排盘逻辑或字段补算逻辑。

- 修改或新增测试：
  - `tests/test_chart_facts.py`
  - `tests/test_chart_normalizer.py`
  - `tests/test_chart_engine.py` 或 provider 相关测试
  - `tests/test_prompt_loading.py`
  - 如新增字段进入 schema，补充相应 schema/fixture 测试。

- 更新文档：
  - `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md`
  - `.supports/PROMPT_GUIDE.md`
  - `.supports/ARCHITECTURE.md`
  - `.supports/DECISIONS.md`
  - 如 API 响应结构发生变化，必须同步更新 `.supports/API_SPEC.md`。

#### 建议 TDD 步骤

执行优先级：

1. 必做：完成字段完整度审计文档。
2. 必做：补齐已经可获得但未进入 `chart_facts` / Prompt 的事实。
3. 必做：结构化星曜事实进入 `chart_facts`，并与 evidence id 对齐。
4. 必做：Prompt 更新为“完整事实包”思路，同时继续禁止 unsupported 字段。
5. 必做：测试覆盖字段保真、Prompt 约束和现有链路兼容。

1. 先创建 `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md`：
   - 不要写私密样本内容。
   - 对每类字段标记：`supported_now`、`available_but_not_exposed`、`provider_unknown`、`unsupported_v0.1`。
   - 明确本轮只处理 `available_but_not_exposed`。

2. 在 `tests/test_chart_facts.py` 中先写失败测试：
   - 星曜事实对象包含 `name`、`brightness`、`category`、`evidence_id`；
   - `evidence_id` 必须存在于 `evidence_index`；
   - 宫位事实包含 `heavenly_stem`、`earthly_branch`；
   - `is_body_palace`、`is_empty`、`borrowed_from`、`opposite_palace`、`san_fang_si_zheng` 仍保留；
   - `four_hua` / `mutagens` 仍保留且不破坏 validator。

3. 审计 `app/engines/providers/iztro_provider.py` 和相关测试：
   - 确认 provider 是否已读取星曜亮度、类别、宫干支、农历信息。
   - 若已有字段但未透传，补到 `RawChart` / `Palace` / `NormalizedChart`。
   - 若 provider 不提供，记录到审计文档，不要在代码中伪造。

4. 修改 `build_chart_facts()`：
   - 保持现有字段尽量兼容；
   - 新增结构化 star facts；
   - 如保留旧字符串列表，确保新旧字段不会互相矛盾；
   - `evidence_index` 仍由同一事实生成，避免 ID 与事实不一致。

5. 更新 Prompt：
   - 描述 `chart_facts` 中可用事实范围；
   - 要求 LLM 使用亮度、宫干支、四化、宫位关系等已提供事实；
   - 明确 `unsupported_v0.1` 字段不得分析；
   - 保持 JSON-only 输出契约。

6. 更新 MockLLMClient：
   - mock 输出不需要模拟完整读盘，但不得引用 unsupported 字段；
   - 如果 prompt 改动影响测试，更新 mock 使全链路继续通过。

7. 更新文档：
   - `PROMPT_GUIDE.md` 记录完整事实包与 unsupported 字段边界；
   - `ARCHITECTURE.md` 记录 `chart_facts` 事实保真职责；
   - `DECISIONS.md` 新增“先审计字段来源，再补齐 Prompt 输入事实，不让 LLM 补算缺失字段”的决策；
   - `TASKS.md` 在完成后记录测试摘要、遗留风险。

#### 验收标准

- `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md` 存在，且不包含私密样本完整内容或可识别个人信息。
- 审计文档清楚区分：已支持、可获得但未暴露、provider 未确认、v0.1 不支持。
- `chart_facts` 中星曜事实至少包含 `name`、`brightness`、`category`、`evidence_id`。
- `chart_facts` 中宫位事实包含可获得的天干、地支、命身、空宫、借星、对宫、三方四正、四化信息。
- `evidence_index` 与结构化星曜/四化事实中的 evidence id 一致。
- Prompt 明确使用完整事实包，同时继续禁止 LLM 分析未支持的大限、流年、神煞、四柱等字段。
- 现有 API/前端测试不应因 Prompt 输入增强而破坏。
- 私密样本文件仍未被 git 跟踪，测试和文档不得包含其中的个人信息或完整命盘文本。

#### 必跑命令

```bash
uv run black --check .
uv run isort --check-only .
uv run flake8 .
uv run pytest -q
```

如修改前端静态文件，额外确认现有前端测试仍覆盖并通过。

#### 风险与注意事项

- 不要把文墨天机完整命盘文本写进仓库；只能借鉴字段类别和信息组织方式。
- 不要用 LLM、Prompt 或手写常量去补算 provider 没有的确定性命盘字段。
- 不要为了“看起来更完整”伪造大限、流年、四柱、神煞、自化等字段。
- 不要让 `chart_facts` 变成无边界的大 JSON dump；只暴露 LLM 分析需要且来源明确的事实。
- 如果发现 `iztro-py` 根本无法提供关键字段，应记录为后续 provider 能力评估，而不是本轮硬做。
- 如果发现需要改变公开 API 结构，必须先在 commit 中同步更新 `.supports/API_SPEC.md` 并说明兼容影响。
