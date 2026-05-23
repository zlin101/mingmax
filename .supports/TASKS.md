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

暂无新任务。
