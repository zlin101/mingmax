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

## 当前任务

### Branch 11: 真实样本端到端验证与输出校准

- 分支名：`task-v0.1-e2e-real-sample-validation`
- 任务性质：验证和校准，不是新增大型功能。
- 背景：Branch 10 后，主链路已经具备 `BirthInfo -> iztro-py -> NormalizedChart -> chart_facts -> Prompt -> LLM -> AnalysisResponse`。但目前还缺少一次可复跑、脱敏、端到端的真实样本验证，无法确认“程序排出的事实、Prompt 打包方式、LLM 输出引用证据”在真实模型下是否一致、克制、可解释。

### 反思与取舍

Branch 10 已经把后端证据层补上，这时有两个自然方向：

1. 做前端命盘核验视图，让用户先看到程序算出的盘，再看 LLM 分析。
2. 做端到端真实样本验证，确认排盘事实、Prompt 和 LLM 输出之间没有明显错漏。

本轮选择第 2 个。原因是前端核验视图会放大现有链路的可信度问题：如果 `chart_facts` 选择不当、Prompt 引导不够、LLM 引用了不存在的事实，前端越完整，用户越容易相信错误输出。先把后端真实链路验清楚，再做前端展示，更符合当前“程序负责算准，LLM 负责讲透”的原则。

本任务的目标不是证明紫微解释“绝对准确”，而是建立一套最低限度的验收机制：

- 程序排出的结构化事实可检查；
- Prompt 传给 LLM 的上下文可脱敏保存；
- LLM 输出不能引用不存在的宫位、星曜、四化或关系；
- 遇到证据不足时，输出应降低确定性或提出追问；
- 私密样本不进入仓库，验证产物也不能泄露出生信息。

### 必须完成

1. 新增端到端验证脚本
   - 建议路径：`scripts/verify_e2e_real_sample.py`。
   - 输入：本地私密样本文件路径，例如 `.supports/TEST_INFO_EVA.md`，但该文件不得提交。
   - 输出：脱敏验证摘要，不包含真实出生日期、出生地、经度、完整原始样本或完整 prompt。
   - 脚本应覆盖：
     - 读取私密样本并构造 `BirthInfo`；
     - 调用 `ZiweiChartEngine` 和 `ChartNormalizer`；
     - 生成 `chart_facts`；
     - 调用 `AnalysisService` 或等价端到端流程；
     - 输出验证摘要和发现的问题。

2. 新增 LLM 输出证据一致性检查
   - 新增可测试的纯函数模块，建议路径：`app/agents/analysis_evidence_validator.py` 或等价模块。
   - 输入：`chart_facts`、`AnalysisResult`、`ThemeAnalysis`、`FollowupQuestion`、`report_markdown`。
   - 检查项至少包括：
     - 输出中不得出现 `chart_facts` 不存在的星曜名称；
     - 输出中不得出现 `chart_facts` 不存在的宫位名称；
     - 输出中不得出现 `chart_facts` 不存在的四化；
     - 不得出现绝对化或恐吓式表述，例如“必然”“一定会”“注定”“绝对失败”等；
     - report 必须包含免责声明。
   - 检查结果应结构化返回，例如 `ValidationIssue(severity, code, message)`，不要只打印字符串。

3. 校准 Prompt
   - 根据验证器结果微调 `app/prompts/*.md`。
   - 重点不是让模型输出更玄，而是让模型：
     - 明确引用 `chart_facts` 中已有证据；
     - 缺证据时说“不足以支持强结论”；
     - 不把主题分析写成泛泛鸡汤；
     - 不把追问写成暗示性、诱导性问题。

4. 增强端到端可观测性
   - 允许脚本输出脱敏后的阶段摘要：
     - `chart.source`
     - 命宫/身宫名称
     - `chart_facts` 中宫位数量
     - LLM provider 类型
     - validation issue 统计
   - 不输出：
     - 真实生日、出生地、经度；
     - API Key、base URL、模型私密配置；
     - 完整私密样本；
     - 完整 prompt；
     - 完整 LLM 原文，除非已脱敏且用户本地手动选择。

5. 更新文档
   - `.supports/DEVELOPMENT_GUIDE.md`：新增端到端私密样本验证命令和隐私要求。
   - `.supports/PROMPT_GUIDE.md`：记录证据一致性检查要求。
   - `.supports/ARCHITECTURE.md`：记录 E2E 验证脚本和 evidence validator 所在职责。
   - `.supports/DECISIONS.md`：记录“先做真实链路验证，再做前端核验视图”的决策。

### 明确不做

- 不提交 `.supports/TEST_INFO_EVA.md` 或任何私密样本。
- 不在自动化测试中真实调用外部 LLM。
- 不把开发者本人的出生信息、地点、经度、命盘全文写入 repo、日志 fixture 或文档。
- 不做新的前端命盘盘面。
- 不实现大限、流年、流月、流日、流时。
- 不引入 LangChain、LangGraph、CrewAI、向量数据库或任务队列。
- 不把证据一致性检查做成“紫微断语正确性裁判”；它只检查引用事实是否存在、表达是否安全、报告是否完整。

### TDD 建议

Claude 执行时应先写或更新测试，再实现代码：

1. `tests/test_analysis_evidence_validator.py`
   - valid output 没有 issue。
   - 输出引用不存在的星曜时返回 issue。
   - 输出引用不存在的宫位时返回 issue。
   - 输出引用不存在的四化时返回 issue。
   - 输出包含绝对化/恐吓式词汇时返回 issue。
   - report 缺免责声明时返回 issue。

2. `tests/test_private_chart_sample_script.py`
   - 验证脚本缺少文件时返回清晰错误。
   - 验证脚本输出不包含输入样本中的敏感字段。
   - 验证脚本支持 mock LLM，不真实调用外部模型。

3. `tests/test_prompt_loading.py`
   - 验证 prompt 包含 `chart_facts`、证据不足降级、不虚构事实、JSON-only 等硬约束。

4. `tests/test_analysis_service.py`
   - 使用 Mock LLM 走完整 service 流程，并对输出执行 evidence validator。

### 验收命令

Claude 完成后必须执行：

```bash
uv run black --check .
uv run isort --check-only .
uv run flake8 .
uv run pytest -q
```

手动真实模型验证可以执行，但只能在本机私密环境中进行，结果记录必须脱敏：

```bash
MINGMAX_LLM_PROVIDER=openai_compatible \
uv run python scripts/verify_e2e_real_sample.py .supports/TEST_INFO_EVA.md
```

如脚本支持 `--mock-llm` 或等价选项，应优先让自动化测试使用 mock 路径。

### Codex 验收关注点

- 是否真正验证 `chart_facts -> prompt -> LLM 输出` 的证据一致性。
- validator 是否是纯函数、可单测、无外部 LLM 依赖。
- 私密样本是否仍只存在本地，仓库内无真实出生信息泄露。
- 脚本输出是否脱敏，错误信息是否不会泄露 API Key、base URL 或样本内容。
- Prompt 校准是否提升证据引用约束，而不是增加宿命化断语。
- 是否没有引入超出 v0.1 范围的大型框架或复杂基础设施。
- 是否为后续前端命盘核验视图留下清晰接口，而不是提前实现前端。
