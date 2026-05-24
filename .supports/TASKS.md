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

### Branch 15: iztro-py 原始输出快照与字段能力审计

- 分支名：`feature/v0.1-iztro-provider-snapshot-audit`
- 目标：落盘 `iztro-py` 原始输出快照和字段 inventory，确认 provider 真实字段能力，避免继续根据当前 schema 或 Prompt 需求反推 provider 能力。
- 关键交付：`provider_snapshot.py` 安全 serializer、`dump_iztro_provider_snapshot.py` 快照脚本、`.local/iztro_snapshots/` ignored 输出、`CHART_FACTS_COMPLETENESS_AUDIT.md` Branch 15 字段能力审计、D028 决策。
- 重要发现：`iztro-py` 原生提供 `lunar_date`、`chinese_date`、`earthly_branch_of_soul_palace`、`earthly_branch_of_body_palace`、`body`、`palace[].decadal`、`star.scope` 等当前未充分吸收字段。
- 重要修复：private 样本输出强制限制到 `.local/iztro_snapshots/`，拒绝农历私密样本和未知性别，inventory 不输出字符串原文样例，direct raw 调用复用真太阳时口径。
- 测试摘要：Codex 修复后 `uv run black --check .`、`uv run isort --check-only .`、`uv run flake8 .`、`uv run pytest -q` 均通过，测试为 `283 passed`；synthetic snapshot 脚本可生成 raw snapshot 和 inventory。
- 遗留风险：审计已确认 provider 信息丰富，但正式业务结构、`chart_facts`、Prompt 和 validator 尚未吸收这些字段；大限数据存在，但 mingmax 尚无大限分析能力。

## 当前任务

### Branch 16/17: 丰富命盘事实层与大限基础分析能力

- 分支名：`feature/v0.1-rich-chart-facts-and-decadal-analysis`
- 负责分工：Claude 负责开发、测试、commit 和 push；Codex 负责 code review 和验收；merge 只由项目负责人执行。
- 背景：Branch 15 已确认 `iztro-py` 原生提供多项当前未吸收字段，包括农历日期、四柱字符串、命身宫地支、身宫类型、星曜 scope、大限 decadal。当前 LLM 输出仍提示“缺乏大限、流年等时间维度”，这对大限已经不再完全准确。本轮将 Branch 16/17 合并：先吸收 provider 原生事实，再升级 `chart_facts`、Prompt 和 validator，开放大限区间级辅助分析。

#### 核心目标

将系统从“静态本命盘 + 少量 evidence 约束”升级为：

```text
iztro-py rich provider facts
  -> RawChart 完整吸收低风险原生字段
  -> NormalizedChart 保真标准化
  -> chart_facts rich package
  -> LLM 支持本命盘 + 大限区间级辅助分析
  -> validator 拦截伪造、错误绑定、越界时间层和不安全表达
```

本轮完成后：

- LLM 不应再笼统说“缺乏大限信息”；
- 可以分析“当前大限落在哪个宫、该宫星曜和本命结构对主题的倾向影响”；
- 仍不得分析流年、流月、流日、流时；
- 仍不得预测具体年份、具体事件是否发生或最终人生结果；
- 前端完整重构暂不做，只允许最小展示/调试字段补充，文墨天机式高信息密度 UI 另开后续分支。

#### 必须阅读

开发前必须阅读：

- `AGENTS.md`
- `.supports/PROJECT_CONTEXT.md`
- `.supports/DECISIONS.md`
- `.supports/ARCHITECTURE.md`
- `.supports/TASKS.md`
- `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md`
- `.supports/PROMPT_GUIDE.md`
- `.supports/API_SPEC.md`
- `app/engines/providers/iztro_provider.py`
- `app/schemas/chart.py`
- `app/engines/chart_normalizer.py`
- `app/engines/chart_facts.py`
- `app/agents/analysis_evidence_validator.py`
- `app/prompts/ziwei_analysis.md`
- `app/prompts/theme_analysis.md`
- `app/prompts/report.md`
- 文墨天机截图仅作为信息密度参考，敏感图片必须放在 .local/，不得提交到仓库。

#### 设计原则

- provider 原生事实内部尽量完整吸收；
- `chart_facts` 尽量丰富，但每类事实要标注来源、支持状态和分析边界；
- 大限数据可以进入分析，但只开放“区间级、宫位级、倾向性”分析；
- validator 不再把“大限”一概视为 unsupported；但继续禁止流年、流月、流日、流时；
- `chinese_date` 可作为四柱字符串背景事实，不开放八字分析；
- 不让 LLM 推算 provider 未给出的字段；
- 不引入 LangChain、LangGraph、CrewAI、向量数据库或复杂 Agent 框架；
- 不读取、提交或泄露 `.supports/TEST_INFO_EVA.md` 中的开发者私密信息。

#### 阶段 1：Schema 与 provider 字段吸收

建议修改：

- `app/schemas/chart.py`
- `app/engines/providers/iztro_provider.py`
- `app/engines/chart_normalizer.py`
- 相关 tests

需要新增或调整的结构：

1. `Star.scope: str | None`
   - 来源：`star.scope`
   - 仅保存 provider 原生值，不翻译、不推断。

2. `DecadalRange`
   - 字段建议：
     - `start_age: int`
     - `end_age: int`
     - `heavenly_stem: str | None`
     - `earthly_branch: str | None`
     - `palace_index: int | None`
     - `palace_name: str | None`
   - 来源：`palace.decadal`
   - 如果 `range` 缺失或格式异常，不能编造年龄段。

3. `ChartMetadata` 或等价结构
   - 字段建议：
     - `lunar_date: str | None`
     - `chinese_date: str | None`
     - `soul_palace_earthly_branch: str | None`
     - `body_palace_earthly_branch: str | None`
     - `body: str | None`
   - 注意：`chinese_date` 是四柱字符串事实，不代表本系统开放八字分析。

4. `RawChart` / `NormalizedChart`
   - 必须透传 `metadata` 或等价字段；
   - `Palace` 必须可承载 `decadal`；
   - Normalizer 不得丢弃 provider 原生事实。

5. 当前大限识别
   - 可以新增 `current_age`、`current_decadal` 或等价字段；
   - 年龄口径必须文档化，建议本轮先采用“虚岁/排盘常用年龄”或明确“周岁近似”，不要含糊。
   - 如果口径无法确定，先只提供全部 decadal 列表，不高亮当前大限；不要伪精确。

测试要求：

- provider 能提取 `lunar_date`、`chinese_date`、命身宫地支、`body`；
- provider 能提取 `star.scope`；
- provider 能提取每宫 `decadal`；
- normalizer 完整透传 metadata、scope、decadal；
- 异常/缺失 decadal 不导致排盘失败；
- 不使用私密样本作为测试 fixture。

#### 阶段 2：Rich chart_facts

建议修改：

- `app/engines/chart_facts.py`
- `tests/test_chart_facts.py`

`chart_facts` 需要新增：

- `metadata`
  - `lunar_date`
  - `chinese_date`
  - `soul_palace_earthly_branch`
  - `body_palace_earthly_branch`
  - `body`
  - `supported_analysis_layers`
  - `unsupported_analysis_layers`

- `palaces[].decadal`
  - 起止年龄；
  - 所在宫；
  - 宫干支；
  - evidence_id，例如 `decadal:<palace_index>:<start>-<end>`。

- `star.scope`
  - 加入 `major_star_facts`、`minor_star_facts`、`adjective_star_facts`。

- `evidence_index`
  - 新增 `metadata`、`decadal` 类型证据；
  - 保持现有 `palace/star/mutagen/relation/borrowed` 不破坏。

支持边界建议：

```json
"supported_analysis_layers": ["natal_chart", "decadal_range"],
"unsupported_analysis_layers": ["annual", "monthly", "daily", "hourly", "bazi"]
```

测试要求：

- rich facts 包含 metadata；
- 星曜 facts 包含 scope；
- decadal facts 和 evidence_index 一致；
- supported/unsupported analysis layers 存在且语义正确；
- 旧 evidence id 仍保持兼容。

#### 阶段 3：Prompt 与 LLM 输出边界重构

建议修改：

- `app/prompts/ziwei_analysis.md`
- `app/prompts/theme_analysis.md`
- `app/prompts/report.md`
- `app/llm/mock.py`
- 相关 tests

Prompt 必须从旧口径：

```text
禁止引用大限、流年、流月、流日、流时等时间层概念——当前系统仅支持本命盘分析。
```

改为新口径：

```text
当前系统支持本命盘分析与大限区间级辅助分析。
可以引用 chart_facts 中明确提供的 decadal facts，说明某一大限区间对应宫位、星曜、四化与主题倾向。
不得分析流年、流月、流日、流时。
不得预测具体年份、具体事件发生与否、婚期、发财年份、疾病发生时间或最终人生结果。
不得基于 chinese_date 展开八字分析。
```

LLM 输出结构可以保持现有 JSON 契约，但内容必须允许：

- 在 `strong_signals` / `weak_hypotheses` / `cross_checks` 中引用 decadal evidence id；
- 在 `uncertainty` 中准确说明“支持大限区间级分析，但不支持流年等更细时间层”。

测试要求：

- Prompt 文本不再说系统完全缺乏大限；
- Prompt 明确禁止流年/流月/流日/流时；
- Prompt 明确禁止具体年份事件预测；
- Mock LLM 输出适配新边界，不再生成过时 uncertainty。

#### 阶段 4：validator 调整

建议修改：

- `app/agents/analysis_evidence_validator.py`
- 相关 tests

必须调整：

- `UNSUPPORTED_TIME_TERMS` 不再包含“大限”；
- 新增或调整规则，禁止：
  - `流年`
  - `流月`
  - `流日`
  - `流时`
  - 具体年份预测类表达，如“2028 年必然结婚”“某年一定发财”等；
- 支持校验 decadal evidence id：
  - `decadal:<idx>:<start>-<end>` 不存在时应报 `FABRICATED_EVIDENCE_ID`；
  - 引用 chart_facts 中不存在的大限区间应报错。

测试要求：

- 文本提到 chart_facts 中存在的大限不报 `UNSUPPORTED_TIME_LAYER`；
- 文本提到流年/流月/流日/流时报 `UNSUPPORTED_TIME_LAYER`；
- 伪造 decadal evidence id 报 `FABRICATED_EVIDENCE_ID`；
- 绝对化大限断语仍报 `UNSAFE_EXPRESSION`。

#### 阶段 5：API / 前端最小兼容

本轮不做文墨天机式完整 UI 重构，但需要保证：

- API 返回的 chart JSON 包含新增 metadata、star.scope、palace.decadal；
- 静态前端不因新增字段报错；
- 如改前端，只允许在命盘摘要/宫位详情中最小展示：
  - 农历日期；
  - 四柱字符串；
  - 大限年龄段；
  - 星曜 scope。

不做：

- 不重构完整盘面布局；
- 不新增底部流年/流月/流日/流时切换；
- 不实现飞星、三合、四化模式切换；
- 不新增复杂前端框架。

#### 文档更新

必须更新：

- `.supports/ARCHITECTURE.md`
  - 更新数据流与 rich facts package；
  - 明确大限区间级分析支持范围。

- `.supports/API_SPEC.md`
  - 更新 chart schema 示例；
  - 标注新增 metadata、scope、decadal。

- `.supports/PROMPT_GUIDE.md`
  - 更新 Prompt 边界；
  - 明确支持本命盘 + 大限区间级辅助分析；
  - 明确不支持流年/流月/流日/流时和八字分析。

- `.supports/CHART_FACTS_COMPLETENESS_AUDIT.md`
  - 将相关字段从“未暴露”更新为“已吸收/已传入 facts/分析支持状态”。

- `.supports/DECISIONS.md`
  - 如实现中确认年龄口径或 decadal schema，需要追加决策。

#### 明确不做

- 不实现流年、流月、流日、流时；
- 不做八字分析；
- 不预测具体年份、具体事件发生时间或最终人生结果；
- 不照抄文墨天机 UI；
- 不引入新的复杂前端框架；
- 不读取 `.supports/TEST_INFO_EVA.md` 或提交任何私密样本；
- 不把 `.local/` 快照文件加入仓库；
- 不删除 Branch 13/14 的 evidence/validator 体系，而是在 richer facts 基础上调整其职责。

#### 推荐 TDD 步骤

1. 先写 schema/provider 失败测试，再实现字段提取；
2. 再写 normalizer 透传测试；
3. 再写 chart_facts rich package 测试；
4. 再写 Prompt 文本边界测试；
5. 再写 validator 时间层测试；
6. 最后补 API/前端最小兼容测试和文档。

#### 建议测试命令

```bash
uv run black --check .
uv run isort --check-only .
uv run flake8 .
uv run pytest -q
```

#### 验收标准

- `iztro-py` 已确认的低风险原生字段被正式吸收到内部结构；
- `chart_facts` 成为 rich facts package，而不是只含少量 evidence 骨架；
- LLM Prompt 支持大限区间级辅助分析，不再声称完全缺乏大限；
- validator 允许合法大限引用，但继续阻止流年/流月/流日/流时和具体年份预测；
- API/前端不因新增字段回归；
- 文档准确描述：支持本命盘 + 大限区间级辅助分析，不支持流年等细时间层；
- 所有格式、lint、测试命令通过；
- Codex review 重点检查：字段来源、schema 边界、大限分析是否越界、validator 是否过严或过松、是否泄露私密信息。
