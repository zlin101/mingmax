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

## 当前任务

### Branch 10: 命盘结构与证据层重构

- 分支名：`task-v0.1-chart-structure-evidence-refactor`
- 参考文档：`.supports/ZIWEI_TS_REFERENCE_REVIEW.md`
- 任务性质：基于参考 TS 项目的结构设计进行后端重构，为后续 LLM 输出稳定性和前端命盘核验视图打基础。

### 目标

当前 `NormalizedChart` 只包含 `chart_id`、`source`、`summary`、`palaces`、`four_hua`，Agent 直接把整张 chart JSON 交给 LLM。这个结构不足以稳定表达“命宫/身宫/三方四正/对宫/空宫借星/星曜分类/亮度”等确定性事实。

本分支目标是新增一层确定性命盘事实与宫位关系结构，让程序先算出可验证证据，再交给 LLM 解释。LLM 仍只负责讲透，不负责排盘或推算关系。

### 必须完成

1. 扩充命盘 Schema
   - 在 `app/schemas/chart.py` 中补充可由程序确定的结构字段。
   - `NormalizedChart` 至少应包含：
     - `ming_palace_index` 或等价命宫定位字段；
     - `body_palace_index` 或等价身宫定位字段；
     - `lunar_info`，若 provider 暂不能稳定提供，可设计为可选结构并明确 omitted；
     - `five_elements_class` 或等价五行局字段，若 provider 暂不能稳定提供，可设计为可选结构并明确 omitted；
     - `chart_facts` 或等价结构化事实集合。
   - `Palace` 至少应包含：
     - `opposite_palace_index`；
     - `san_fang_si_zheng_indexes`；
     - `is_empty`；
     - `borrowed_from_index`；
     - `borrowed_major_stars`；
     - 可选的归一化星曜亮度字段，例如 `normalized_brightness`。

2. 新增宫位关系计算
   - 新增 `app/engines/chart_relations.py` 或等价模块。
   - 由 Engine/Normalizer 层确定：
     - 对宫；
     - 三方四正；
     - 空宫判断；
     - 空宫借对宫主星。
   - 不允许把这些关系交给 Prompt 或 LLM 自行推断。

3. 新增确定性证据层
   - 新增 `app/engines/chart_facts.py` 或等价模块。
   - 从 `NormalizedChart` 生成 `chart_facts` / `chart_evidence`。
   - 证据应只包含结构化事实，例如宫位、星曜、四化、三方四正路径、空宫借星来源。
   - 不输出“必然发财”“必然离婚”“重大疾病”等宿命化结论。

4. 更新 Agent 输入
   - `ZiweiAnalysisAgent` 的 context 应优先提供结构化事实和必要命盘摘要，而不是无约束地要求模型自行解读原始宫位列表。
   - Prompt 应明确要求：
     - 只能引用给定 `chart_facts` / `chart_evidence`；
     - 不得虚构不存在的星曜、宫位、四化、大限或流年；
     - 证据不足时必须降低确定性或提出追问。

5. 更新文档
   - `.supports/API_SPEC.md`：记录新增 chart 字段和兼容性说明。
   - `.supports/ARCHITECTURE.md`：记录 `chart_relations` / `chart_facts` 所在层级和数据流。
   - `.supports/PROMPT_GUIDE.md`：记录 LLM 必须基于结构化证据输出。
   - `.supports/DECISIONS.md`：记录本分支只借鉴 TS 项目的结构设计，不迁移框架、不复制断语。

### 明确不做

- 不迁移 Next.js / React / Tailwind。
- 不实现 SEO 内容页。
- 不实现合盘。
- 不引入 LangChain、LangGraph、CrewAI、向量数据库或任务队列。
- 不一次性移植参考项目的大型格局规则库。
- 不照搬参考项目中的宿命化断语或高风险文本。
- 不把 `.supports/TEST_INFO_EVA.md` 或任何私密出生信息写入代码、测试、文档或提交记录。
- 不让 LLM 计算命宫、身宫、四化、三方四正、空宫借星。

### TDD 建议

Claude 执行时应先写或更新测试，再实现代码：

1. `tests/test_chart_relations.py`
   - 验证 12 宫 index 的对宫计算。
   - 验证三方四正返回本宫、对宫、两个三合宫，且结果稳定去重。
   - 验证非法 index 报清晰错误。

2. `tests/test_chart_normalizer_accuracy.py`
   - 验证 Normalizer 不丢失 provider 已提供字段。
   - 验证每个 Palace 都带有对宫与三方四正字段。
   - 验证空宫时借对宫主星；非空宫不生成借星。

3. `tests/test_chart_schema.py`
   - 验证新增字段默认值、可选字段和序列化结果。
   - 验证 API chart 响应不包含私密出生信息。

4. `tests/test_agent_parsing.py` 或 `tests/test_analysis_service.py`
   - 验证 Agent 传给 LLM 的 context 包含 `chart_facts` / `chart_evidence`。
   - 验证 prompt 明确禁止模型虚构未给定事实。

5. `tests/test_prompt_loading.py`
   - 验证相关 prompt 包含结构化证据约束、JSON-only 约束和安全边界。

### 验收命令

Claude 完成后必须执行：

```bash
uv run black --check .
uv run isort --check-only .
uv run flake8 .
uv run pytest -q
```

如果引入依赖，必须使用 `uv add` 或 `uv add --dev`，并说明原因。本任务预计不需要新增依赖。

### Codex 验收关注点

- 分层是否仍清晰：关系和事实计算属于 Engine/Normalizer，不属于 Agent 或 Prompt。
- API/Service/Agent 是否没有直接依赖 `iztro-py`。
- LLM context 是否更收敛，并优先引用结构化证据。
- 新增字段是否向后兼容，前端和现有 API 测试是否不被无意破坏。
- 测试是否覆盖关系计算、空宫借星、context 构造和 prompt 约束。
- 是否没有提交私密样本或泄露出生信息。
- 是否没有复制参考 TS 项目的宿命化内容。
