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

## 当前任务

### Branch 13: LLM 分析能力增强：分析框架、证据绑定与安全校验

- 建议分支名：`feature/v0.1-llm-analysis-evidence-framework`
- 负责人分工：Claude 负责开发、测试、commit、push；Codex 负责 code review 和验收；merge 只由项目负责人执行。

#### 背景与反思

Branch 12 之后，mingmax 已经具备完整主链路：

```text
BirthInfo -> ZiweiChartEngine -> RawChart -> NormalizedChart -> chart_facts -> Prompt -> LLM -> 前端展示
```

当前问题不再是“能否把真实模型接上”或“用户能否看到命盘”，而是 LLM 输出质量仍不够稳定：模型可能泛化分析、引用不精确、把星曜和宫位绑定错，或在证据不足时给出过强判断。

文墨天机提示词的优点是会把完整命盘信息交给模型，并明确要求模型按十二宫、四化、主题领域、建议和免责声明组织分析。mingmax 可以借鉴这种“完整命盘上下文 + 明确分析路径”的方式，但不能照搬其多流派大而全、逐年吉凶、重大事件时间范围等要求，因为当前 v0.1 还没有确定性支持大限、流年、流月、流日、流时，也不能让 LLM 自行补算这些内容。

`/home/liam/git/ziwei-doushu` 的 TS 项目仍有可借鉴点：小型确定性规则层、星曜/宫位/四化的结构化知识组织、证据先行再解释的产品思路。但本任务不迁移其前端框架、不照搬断语、不做 SEO/合盘/会员等超出 v0.1 的能力。

本轮核心判断：

> 不是让 LLM 更会“算”，而是让 LLM 在程序给定的命盘事实和有限知识框架内，更稳定地组织分析，并让程序能校验它是否乱引证据。

#### 目标

1. 为 `chart_facts` 增加稳定、可引用的 evidence id，让宫位、星曜、四化、对宫、三方四正、空宫借星等事实可被 LLM 引用和程序校验。
2. 强化 `analysis_evidence_validator`，从“全局名称是否存在”升级到“宫位-星曜/宫位-四化绑定是否真实”。
3. 升级 Prompt 分析框架，借鉴文墨天机“完整命盘上下文 + 多维度分析路径”的优点，但保持 mingmax 的结构化证据、安全边界和 v0.1 范围。
4. 可选增加轻量、低争议的紫微信息组织层，辅助 LLM 解释宫位、十四主星、四化等基础含义；不得加入宿命化断语。该项不是本分支硬性验收目标，只有在不扩大范围、不影响 evidence/validator 主线时才做。
5. 保持 API 尽量兼容；除非必要，不在本任务中大改前端或响应结构。

#### 非目标

- 不实现大限、流年、流月、流日、流时计算。
- 不要求 LLM 对未支持的限流信息做逐年分析。
- 不引入 LangChain、LangGraph、CrewAI、向量数据库或复杂 Agent 框架。
- 不引入 React、Vue、Next.js、Vite、Tailwind 或新的前端构建链。
- 不复制文墨天机或 TS 项目的宿命化断语。
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
  - `/home/liam/git/ziwei-doushu/lib/ziwei/patterns.ts`
  - `/home/liam/git/ziwei-doushu/lib/ziwei/constants.ts`
  - `/home/liam/git/ziwei-doushu/lib/ziwei/sihua.ts`

#### 建议文件改动

- 修改：`app/engines/chart_facts.py`
  - 在现有 `chart_facts` 中增加 `evidence_index` 或等价结构。
  - 每个证据项必须有稳定 id、类型、标签和可校验 payload。
  - 建议 id 格式：
    - `palace:<index>`
    - `star:<palace_index>:<star_name>`
    - `mutagen:<palace_index>:<hua_lu|hua_quan|hua_ke|hua_ji>:<star_name>`
    - `relation:<palace_index>:opposite:<opposite_index>`
    - `relation:<palace_index>:sfsz:<index_a>,<index_b>,<index_c>,<index_d>`
    - `borrowed:<palace_index>:from:<opposite_index>:<star_name>`

- 修改：`app/agents/analysis_evidence_validator.py`
  - 基于 `chart_facts` 构建宫位、星曜、四化、关系的查验索引。
  - 能发现以下错误：
    - LLM 说“某星在某宫”，但该星不在该宫；
    - LLM 说“某宫有某化曜”，但该宫没有该四化；
    - LLM 引用不存在的 evidence id；
    - LLM 把对宫、三方四正关系说错；
    - LLM 使用大限、流年、流月、流日、流时等当前未支持事实。
  - 保持纯函数，不调用外部 LLM。

- 修改：`app/prompts/ziwei_analysis.md`
  - 要求模型按固定分析路径输出：
    - 命盘结构摘要；
    - 较强信号；
    - 弱假设；
    - 宫位交叉验证；
    - 不确定性；
    - 安全提醒。
  - 每条强信号和交叉验证必须引用 evidence id 或明确引用 `chart_facts` 中的宫位/星曜/四化事实。
  - 明确禁止对未提供的大限、流年、流月、流日、流时进行分析。

- 修改：`app/prompts/theme_analysis.md`
  - 主题分析必须只使用主题相关宫位及其三方四正/对宫证据。
  - 证据不足时必须输出“当前结构不足以支持强结论”或等价克制表达。

- 修改：`app/prompts/followup_questions.md`
  - 追问必须服务于校准解释方向，不得暗示用户必然遭遇某类事件。
  - `related_chart_factors` 应优先引用 evidence id 或结构化事实标签。

- 修改：`app/prompts/report.md`
  - 报告结构保留免责声明。
  - 新增“证据依据/不确定性”要求。
  - 禁止输出未支持的限流逐年判断。

- 可新增：`app/knowledge/ziwei/basic.py`
  - 这是可选增强，不是本分支必须交付。
  - 只放低争议、中性、可安全改写的基础解释素材。
  - 建议先覆盖：
    - 十二宫主题含义；
    - 十四主星中性关键词；
    - 四化通用解释；
    - 证据强弱说明。
  - 不放“必然”“注定”“大凶”“一定离婚/破财/疾病”等断语。

- 修改：`app/agents/ziwei_analysis_agent.py`
  - 如果引入基础知识层，只能作为 prompt context 的辅助材料。
  - 不得让 Agent 推算命盘事实。

- 修改或新增测试：
  - `tests/test_chart_facts.py`
  - `tests/test_analysis_evidence_validator.py`
  - `tests/test_prompt_loading.py`
  - 视实现情况新增 `tests/test_ziwei_knowledge.py`

- 更新文档：
  - `.supports/PROMPT_GUIDE.md`
  - `.supports/ARCHITECTURE.md`
  - `.supports/DECISIONS.md`
  - 如 API 响应结构发生变化，必须同步更新 `.supports/API_SPEC.md`。

#### 建议 TDD 步骤

执行优先级：

1. 必做：`chart_facts` evidence index。
2. 必做：validator 对 evidence id、宫星绑定、四化绑定、未支持时间层的校验。
3. 必做：Prompt 分析框架和禁止项更新。
4. 必做：MockLLMClient 与现有链路适配。
5. 可选：基础知识层。只有前四项完成且测试稳定后才允许加入。

1. 在 `tests/test_chart_facts.py` 中先写失败测试：
   - `build_chart_facts()` 输出 `evidence_index`；
   - 每个宫位有 `palace:<index>` 证据；
   - 每个主星有 `star:<palace_index>:<star_name>` 证据；
   - 每个四化有 `mutagen:<palace_index>:<field>:<star_name>` 证据；
   - 对宫和三方四正关系有 relation 证据。

2. 实现 `chart_facts` evidence index：
   - 保持原有 `palaces`、`ming_palace`、`body_palace`、`four_hua` 字段兼容；
   - 新增字段不应破坏现有前端和 API 测试。

3. 在 `tests/test_analysis_evidence_validator.py` 中写失败测试：
   - 引用不存在 evidence id 返回 `FABRICATED_EVIDENCE`；
   - “紫微在夫妻宫”但紫微实际不在夫妻宫时返回 `INVALID_STAR_PALACE_BINDING`；
   - “夫妻宫有化忌”但实际没有时返回 `INVALID_MUTAGEN_PALACE_BINDING`；
   - 输出“大限/流年/流月/流日/流时”但 `chart_facts` 未提供时返回 `UNSUPPORTED_TIME_LAYER_REFERENCE`；
   - 安全表达和免责声明现有测试继续通过。

4. 实现 validator 增强：
   - 先从 evidence id 校验做起；
   - 再做中文短语级宫星绑定识别；
   - 识别能力保持保守，宁可少拦截，也不要误杀中性描述；
   - 对难以确定的自然语言绑定可先 warning，不要随意 error。

5. 更新 Prompt：
   - 引导模型使用 evidence id；
   - 引导模型按分析框架输出；
   - 明确未支持范围；
   - 保持 JSON-only 输出契约。

6. 如新增基础知识层：
   - 先写测试保证知识条目不包含禁止词；
   - 知识层只提供中性关键词，不直接生成结论；
   - Agent 只把相关基础知识作为辅助 context，不改变排盘事实。

7. 更新 MockLLMClient：
   - mock 输出应符合新 prompt 和 validator 要求；
   - 不要让 mock 输出未支持的大限/流年内容。

8. 更新文档：
   - `PROMPT_GUIDE.md` 记录新分析框架和 evidence id 规则；
   - `ARCHITECTURE.md` 记录 evidence index 和 validator 职责；
   - `DECISIONS.md` 新增“LLM 分析必须基于 evidence id/结构化事实，不得分析未支持时间层”的决策；
   - `TASKS.md` 在完成后记录测试摘要、遗留风险。

#### 验收标准

- `chart_facts` 中存在稳定 evidence index，且不破坏现有 API/前端消费。
- Prompt 明确要求 LLM 使用结构化证据，不得分析未支持的大限/流年等时间层。
- Validator 能校验 evidence id、宫星绑定、宫位四化绑定和未支持时间层引用。
- Mock LLM 全链路仍可运行，输出不包含 stub/unsupported/time-layer 幻觉。
- 基础知识层不是硬性验收项；若实现，必须只包含中性、低争议、安全表达素材，并有测试覆盖禁止词。
- 私密样本文件仍未被 git 跟踪，测试和文档不得包含其中的个人信息或完整命盘文本。
- 如真实 LLM 手动验证，记录只能是脱敏摘要和 issue 统计。

#### 必跑命令

```bash
uv run black --check .
uv run isort --check-only .
uv run flake8 .
uv run pytest -q
```

如修改前端静态文件，额外确认现有前端测试仍覆盖并通过。

#### 风险与注意事项

- 自然语言中的宫星绑定识别不应追求一次到位，先覆盖清晰模式，例如“<星曜>在<宫位>”“<宫位>见<星曜>”“<宫位>有<化曜>”。
- 不要因为文墨天机提示词提到多流派，就让模型输出三合、飞星、河洛、钦天四化等当前程序没有确定性支持的内容。
- 不要为了提升分析感而牺牲可验证性；所有结论应能回到 `chart_facts` 或基础知识层。
- 如果发现需要改变公开 API 结构，必须先在 commit 中同步更新 `.supports/API_SPEC.md` 并说明兼容影响。
