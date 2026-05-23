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
- 遗留风险：validator 目前主要做全局名称存在性检查，尚不能判断"某星是否真的落在某宫"这类宫星绑定关系错误。

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

### Branch 14: 命盘事实完整度审计与 Prompt 输入增强

- 分支名：`feature/v0.1-chart-facts-completeness-audit`
- 目标：审计文墨天机字段、iztro-py 输出、当前 schema 和 chart_facts/Prompt 之间的信息流，补齐已可获得但未传给 LLM 的事实。
- 关键交付：`CHART_FACTS_COMPLETENESS_AUDIT.md`、结构化星曜事实（name/brightness/category/evidence_id）、宫位天干地支、Prompt 完整事实包描述、D027 决策。
- 重要决策：先审计字段来源再补齐 Prompt 输入事实，不让 LLM 补算缺失字段；证据 ID 与 evidence_index 保持一致。
- 测试摘要：Codex 验收时 260 passed；修复了 P1（辅星/杂曜 evidence_id 未写入 evidence_index）和 P2（mutagens 分支重复赋值）。
- 遗留风险：审计文档中仍有 provider_unknown 字段（农历信息、四柱、神煞等），后续需单独验证 provider 能力而非让 LLM 补算。

## 当前任务

### Branch 15: iztro-py 原始输出快照与字段能力审计

- 分支名：`feature/v0.1-iztro-provider-snapshot-audit`
- 负责分工：Claude 负责开发、测试、commit、push；Codex 负责 code review 和验收；merge 只由项目负责人执行。
- 背景：Branch 13/14 已建立 evidence 体系并增强 `chart_facts`，但没有先完整落盘和审计 `iztro-py` 原始返回对象，导致农历、四柱、大限、命主/身主、五行局等字段仍停留在 `provider_unknown`。本分支不是继续扩展 Prompt，而是先把 provider 能力边界搞清楚。

#### 目标

建立一个可复用的 provider 审计工具链：

```text
BirthInfo / synthetic sample
  -> 调用 iztro-py
  -> 生成可序列化 raw provider snapshot
  -> 生成字段 inventory
  -> 更新字段完整度审计文档
  -> 再决定后续哪些字段进入正式业务结构
```

本分支完成后，项目应能回答：

- `iztro-py` 顶层 astrolabe 实际有哪些 public 字段；
- 每个 palace 实际有哪些字段；
- major/minor/adjective star 实际有哪些字段；
- 四化、大限、五行局、命宫/身宫、农历、四柱等字段是否真实存在；
- 哪些字段来自 `iztro-py` 原生，哪些只能由 mingmax 派生，哪些需要额外历法库，哪些暂不支持；
- `/home/liam/git/ziwei-doushu` 参考项目中传给 LLM 的 chart 字段，哪些可以在 mingmax 中复用，哪些不应复用。

#### 必须阅读

开发前先阅读：

- `AGENTS.md`
- `.supports/PROJECT_CONTEXT.md`
- `.supports/DECISIONS.md`
- `.supports/ARCHITECTURE.md`
- `.supports/TASKS.md`
- `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md`
- `/home/liam/git/ziwei-doushu/lib/ziwei/types.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/algorithm.ts`
- `/home/liam/git/ziwei-doushu/components/ChatPanel.tsx`
- `/home/liam/git/ziwei-doushu/components/InsightPanel.tsx`

#### 实现范围

1. 新增 provider raw snapshot 工具

   建议文件：

   - `scripts/dump_iztro_provider_snapshot.py`

   要求：

   - 使用合成出生信息作为默认样本，不读取 `.supports/TEST_INFO_EVA.md`；
   - 允许通过参数传入本地私密样本路径，但输出必须进入 ignored 本地目录，例如 `.local/iztro_snapshots/`；
   - 不把真实出生日期、地点、经度、姓名或完整私密命盘写入仓库；
   - 直接调用当前 `iztro-py` 能力，必要时同时记录 `ZiweiChartEngine` / provider 包装后的结果，但重点是原始对象；
   - 输出 JSON 文件，例如：

     ```text
     .local/iztro_snapshots/<timestamp>-raw-provider-snapshot.json
     .local/iztro_snapshots/<timestamp>-field-inventory.md
     ```

2. 新增安全 serializer

   要求：

   - 能递归遍历 `iztro-py` 返回对象、palace、star 等对象；
   - 支持基本类型、list、tuple、dict、enum、pydantic model；
   - 记录对象类型名；
   - 跳过 callable；
   - 限制递归深度，避免循环引用；
   - 对不可序列化字段降级为字符串或类型描述；
   - 不使用 `print` 作为库内日志；脚本入口可以输出简短完成信息。

   建议放置：

   - `app/engines/providers/provider_snapshot.py`

3. 生成字段 inventory

   字段清单至少覆盖：

   - astrolabe 顶层字段；
   - palace 字段；
   - major star 字段；
   - minor star 字段；
   - adjective star 字段；
   - mutagen / 四化相关字段；
   - decadal / 大限相关字段；
   - five elements / 五行局相关字段；
   - soul/body palace / 命宫身宫相关字段；
   - lunar / 农历相关字段；
   - pillars / 四柱相关字段。

   inventory 不需要包含私密样本值，只需要字段路径、类型、是否存在、样例值摘要。

4. 对齐 TS 参考项目

   更新或新增文档，建议优先更新：

   - `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md`

   需要新增一个“TS 参考项目字段对齐”小节，明确：

   - `BirthInfo` 字段哪些已支持；
   - `LunarInfo` 在 TS 项目中来自 `lunar-javascript`，不要误认为 iztro 原生；
   - `Star.type = lucky/sha` 是 TS 项目规则映射，不是 iztro 原生结构；
   - `ziweiPos`、`currentAge`、`currentDaXianIndex` 属于派生字段；
   - `daXianAge` 是否能从 `iztro-py` 原始对象中拿到；
   - TS 项目把完整 `chart` 发给 LLM，而 mingmax 当前保持 `chart_facts + evidence_id + validator`，只借鉴字段丰富度，不照搬整包 chart 入 prompt。

5. 更新审计结论

   将 `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md` 中能够确认的 `provider_unknown` 改成明确状态：

   - `provider_supported`
   - `derived_by_mingmax`
   - `requires_extra_calendar_library`
   - `unsupported_by_provider`
   - `unsupported_v0.1`
   - `needs_followup`

   不确定的字段必须写明“为什么仍不确定”，不能只保留空泛的 `?`。

#### 明确不做

- 不在本分支继续优化 LLM Prompt 文风；
- 不让 LLM 补算任何 provider 未确认字段；
- 不一次性把所有发现字段加入公开 API；
- 不大规模改 `RawChart` / `NormalizedChart` / `chart_facts` schema；
- 不实现大限、流年、流月、流日、流时分析；
- 不引入 LangChain、LangGraph、CrewAI、向量数据库或复杂 Agent 框架；
- 不读取、提交或泄露 `.supports/TEST_INFO_EVA.md` 中的开发者私密信息；
- 不把 `.local/iztro_snapshots/` 中的私密快照提交到仓库。

#### 允许的小范围业务修复

如果审计发现当前已经有明确字段可得、且 mingmax 已有 schema 承载但 provider 漏取，可以做小范围修复，但必须满足：

- 修改范围小；
- 有单元测试；
- 文档说明字段来源；
- 不改变公开 API 契约的主要结构；
- 不把本分支变成“字段大扩张”。

#### 测试要求

至少补充：

- serializer 能处理嵌套对象、list、dict、enum、callable、循环引用或重复引用；
- snapshot 脚本默认使用合成样本，不读取私密样本；
- 输出目录默认为 `.local/iztro_snapshots/`；
- inventory 生成不包含私密输入原文；
- `.local/iztro_snapshots/` 被 `.gitignore` 排除；
- 文档中不包含 `.supports/TEST_INFO_EVA.md` 的真实出生信息。

建议执行：

```bash
uv run black --check .
uv run isort --check-only .
uv run flake8 .
uv run pytest -q
```

#### 验收标准

- 可以通过一条 `uv run ...` 命令生成 raw provider snapshot 和 field inventory；
- 仓库内不包含任何私密样本值或真实个人出生信息；
- `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md` 能清楚说明 `iztro-py` 到底支持哪些字段；
- TS 参考项目字段来源被明确拆分为 iztro 原生、TS 派生、额外历法库、暂不复用；
- Branch 13/14 遗留的 `provider_unknown` 至少被系统性收敛，不再继续靠猜；
- Codex review 时重点检查隐私边界、serializer 安全性、字段来源判断、是否过度扩张业务 schema。
