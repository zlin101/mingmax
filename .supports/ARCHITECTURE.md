# ARCHITECTURE.md

## 分层结构

推荐目录结构：

```text
app/
  main.py
  api/
    v1/
      routes_analysis.py
  agents/
    ziwei_analysis_agent.py
  core/
    config.py
    logging.py
  engines/
    providers/
      iztro_provider.py
    ziwei_chart_engine.py
    chart_normalizer.py
    chart_relations.py
    chart_facts.py
    chart_diff.py
    time_calibration.py
  llm/
    base.py
    mock.py
  prompts/
    ziwei_analysis.md
    theme_analysis.md
    followup_questions.md
    report.md
  schemas/
    birth.py
    chart.py
    analysis.py
  services/
    analysis_service.py
  web/
    __init__.py
    static/
      index.html
      styles.css
      app.js
tests/
  conftest.py
  test_birth_schema.py
  test_chart_engine.py
  test_chart_normalizer.py
  test_chart_relations.py
  test_chart_facts.py
  test_analysis_service.py
  test_api_analysis.py
  test_prompt_loading.py
  test_mock_llm.py
  test_frontend_static.py
```

## 模块职责

- API 层：请求校验、依赖注入、响应封装，不写复杂业务逻辑，不直接调用 LLM。
- Service 层：编排出生信息、排盘、标准化、Agent 分析和报告生成流程。
- Engine 层：负责确定性排盘、命盘标准化、宫位关系计算（`chart_relations`）、结构化事实提取（`chart_facts`），不调用 LLM；第三方紫微库通过 `engines/providers/` 适配后再由 `ZiweiChartEngine` 使用。
- Agent 层：组织 LLM 分析流程、Prompt Pipeline、追问与校准，不负责排盘或关系计算。Agent 通过 `build_chart_facts()` 生成结构化证据传给 LLM，不得将原始 `NormalizedChart` JSON 直接交给模型。`analysis_evidence_validator.py` 提供 LLM 输出证据一致性检查，纯函数，不调用外部 LLM。
- LLM 层：统一模型调用抽象，提供真实 Client 和 Mock Client。
- Schema 层：定义请求、响应、命盘、分析结果等结构化模型。
- Web 层：静态前端文件，通过 FastAPI 挂载，只调用后端 API，不直接参与排盘或 LLM 调用。Branch 12 新增命盘核验视图（4x4 十二宫盘面、宫位详情面板、命盘摘要区），只消费 API 返回的 `chart` 字段，不在前端计算排盘关系。
- Prompt 层：集中管理 Prompt 模板和输出约束。

## 数据流

```text
HTTP Request
  -> BirthInfo schema validation
  -> AnalysisService
  -> ZiweiChartEngine
  -> RawChart (with metadata: lunar_date, chinese_date, five_elements_class)
  -> ChartNormalizer (enriches with relations: opposite, san_fang_si_zheng, empty/borrowed, decadal)
  -> NormalizedChart (with current_age, current_decadal)
  -> build_chart_facts() (extracts structured evidence with metadata, decadal, scope)
  -> chart_facts (rich facts package: palaces, stars, mutagens, relations, metadata, decadal, evidence_index)
  -> ZiweiAnalysisAgent (passes chart_facts, not raw chart JSON)
  -> LLMClient (with prompts supporting natal_chart + decadal_range analysis)
  -> AnalysisResult
  -> Markdown report
  -> validate_analysis_output() (checks evidence consistency including decadal/metadata evidence IDs)
  -> HTTP Response
```

## 禁止跨层调用

- API 层不得直接调用 LLM。
- API 层不得直接执行排盘或报告拼装。
- Agent 层不得执行安星、定宫、四化、大限、流年、对宫、三方四正、空宫借星等确定性逻辑。
- Engine 层不得调用 LLM。
- `chart_relations` 和 `chart_facts` 属于 Engine 层，Agent 层只能消费其输出。
- 第三方紫微库必须通过 `ZiweiChartEngine` 和内部 provider 封装，当前 Branch 7 优先使用 `iztro-py`。
- 第三方模型 SDK 必须通过 `LLMClient` 封装。

## v0.1 最小闭环

Branch 1-6 允许使用可预测的 Engine stub 和 Mock/真实 LLM Client 建立 API、Service、Agent、Prompt、Report、Web 的完整闭环。Branch 7 开始使用 `iztro-py` provider 替换运行时 stub 排盘，保持 `BirthInfo -> ZiweiChartEngine -> RawChart -> NormalizedChart -> ZiweiAnalysisAgent` 数据流不变。

## 排盘准确性验证

### 输入口径

`BirthInfo` 支持可选 `longitude` 字段（东经度数）：

- 默认始终进行真太阳时校正。
- 如果提供 `longitude`，使用其精确值计算真太阳时偏移（均时差 + 经度校正）。
- 如果不提供 `longitude`，从 `timezone` 的 UTC offset 推算近似经度（`longitude ≈ UTC_offset_hours × 15`），此时只有均时差修正，不含经度偏差修正。

### 真太阳时计算

`time_calibration.py` 中的 `true_solar_time_offset()` 使用均时差近似公式和经度校正计算真太阳时偏移。`infer_longitude_from_timezone()` 从时区 UTC offset 推算近似经度作为默认值。`iztro_provider.py` 只消费校正结果，不持有时间校正常量或公式。

### 字段保真

`ChartNormalizer` 直接透传 `RawChart` 的 `palaces`、`four_hua`，不丢弃或修改字段，并额外填充宫位关系（对宫、三方四正、空宫判断、借星）。`chart_diff.py` 提供结构化对比工具用于验证。

### 宫位关系计算

`app/engines/chart_relations.py` 提供纯函数：`opposite_palace_index()`、`san_fang_si_zheng_indexes()`、`is_empty_palace()`、`borrowed_from_index()`、`borrowed_major_stars()`。所有关系在 Engine/Normalizer 层计算，Agent 和 LLM 层不得重新推算。

### 结构化证据层

`app/engines/chart_facts.py` 的 `build_chart_facts()` 从 `NormalizedChart` 生成结构化事实字典，包含命宫/身宫定位、四化、每个宫位的主星/辅星/杂曜/化曜/天干地支/对宫/三方四正/空宫借星，以及 `evidence_index`（稳定证据 ID 列表）。Agent 通过此函数构建传给 LLM 的 context，不再传递原始 chart JSON。

星曜以结构化对象形式提供：`major_star_facts`、`minor_star_facts`、`adjective_star_facts`，每个包含 `name`、`brightness`（亮度）、`category`（类别）、`evidence_id`（证据 ID）。证据 ID 格式：`star:<宫位索引>:<星名>`。

宫位包含天干地支：`heavenly_stem`（天干）、`earthly_branch`（地支）。

### 证据 ID 体系

`chart_facts.evidence_index` 为每条结构化事实提供稳定 ID，供 LLM 引用和验证器校验：

| 类型 | ID 格式 | 示例 |
|------|---------|------|
| 宫位 | `palace:<idx>` | `palace:0` |
| 星曜 | `star:<idx>:<name>` | `star:0:紫微` |
| 四化 | `mutagen:<idx>:<field>:<name>` | `mutagen:0:hua_lu:紫微` |
| 对宫 | `relation:<idx>:opposite:<opp>` | `relation:0:opposite:6` |
| 三方四正 | `relation:<idx>:sfsz:<idxes>` | `relation:0:sfsz:0,4,6,8` |
| 借星 | `borrowed:<idx>:from:<opp>:<name>` | `borrowed:8:from:2:太阴` |
| 大限 | `decadal:<idx>:<start>-<end>` | `decadal:0:10-19` |
| 元数据 | `metadata:<field>` | `metadata:lunar_date` |

### 支持的分析层

`chart_facts` 包含 `supported_analysis_layers` 和 `unsupported_analysis_layers` 字段明确定义分析边界：

**支持的分析层：**
- `natal_chart`：本命盘分析，基于出生时刻的静态命盘结构
- `decadal_range`：大限区间级辅助分析，可以引用 chart_facts 中明确提供的 decadal facts

**不支持的分析层：**
- `annual`：流年分析
- `monthly`：流月分析  
- `daily`：流日分析
- `hourly`：流时分析
- `bazi`：八字四柱分析

### 元数据信息

`chart_facts.metadata` 包含命盘背景信息：
- `lunar_date`：农历日期字符串
- `chinese_date`：四柱字符串
- `five_elements_class`：五行局
- `soul_palace_earthly_branch`：命宫地支
- `body_palace_earthly_branch`：身宫地支
- `body`：身宫类型

这些信息可作为命盘背景引用，但不得展开为八字分析或四柱推演。

### 对比工具

`app/engines/chart_diff.py` 提供 `diff_charts()` 函数，将 `NormalizedChart` 与 `ExpectedChartSnapshot` 进行字段级对比，返回差异列表（severity: error/warning）。

### 本地验证脚本

`scripts/verify_private_chart_sample.py` 接受本地文件路径，解析参考命盘文本，与 mingmax 排盘结果对比，输出脱敏差异摘要。不得提交私密验证文件。

### 端到端验证脚本

`scripts/verify_e2e_real_sample.py` 接受本地私密样本文件路径，运行完整 `BirthInfo -> 排盘 -> chart_facts -> LLM -> 验证` 流程，输出脱敏验证摘要和证据一致性 issue 统计。支持 `--mock-llm` 选项用于自动化测试。输出不包含真实出生日期、地点、经度、API Key 或完整 LLM 原文。

### LLM 输出证据一致性检查

`app/agents/analysis_evidence_validator.py` 提供 `validate_analysis_output()`，纯函数，检查 LLM 输出是否：
- 引用 `chart_facts` 中不存在的星曜、宫位、四化
- 引用不存在的 evidence_index ID
- 星曜-宫位绑定不一致（如"XX在YY宫"但实际不在）
- 四化-宫位绑定不一致（如"YY宫XX化Z"但实际不在）
- 引用流年、流月、流日、流时等不支持的时间层（大限已支持）
- 包含绝对化/恐吓式表达
- 报告是否包含免责声明

返回 `list[ValidationIssue]`，不调用外部 LLM。ValidationIssue code 包括 FABRICATED_STAR、FABRICATED_PALACE、FABRICATED_MUTAGEN、FABRICATED_EVIDENCE_ID、INVALID_STAR_PALACE_BINDING、INVALID_MUTAGEN_PALACE_BINDING、UNSUPPORTED_TIME_LAYER、UNSAFE_EXPRESSION、MISSING_DISCLAIMER。

### 前端命盘核验视图

### 定位

Branch 12 在现有原生 HTML/CSS/JS 前端中新增命盘核验视图。该视图的定位是排盘核验工具，让用户和开发者在前端直观看到后端排出的紫微盘，再阅读 LLM 分析结果。

### 页面结构

- **命盘摘要区**（`#chart-summary`）：展示来源、chart_id、命宫、身宫、五行局、农历信息。缺失字段显示"暂未提供"。
- **4x4 十二宫盘面**（`#chart-grid`）：CSS Grid 4×4 布局，12 个宫位按 earthly branch 固定位置排列，中间 2×2 为品牌/摘要区。每个宫位显示宫名、天干地支、主星、辅星数量、四化 badge、命宫/身宫标记、空宫/借星标记。
- **宫位详情面板**（`#palace-detail`）：点击或键盘选中宫位后展示完整信息——全部星曜按 category 分组、对宫、三方四正、空宫状态、借星来源、本宫四化。
- **响应式**：桌面端 4×4 盘面，移动端自动切换为 2 列列表布局。

### 前端不计算的原则

- 宫位 index 到网格位置的映射是固定常量（基于 iztro 宫位顺序），不是排盘计算。
- 所有对宫、三方四正、空宫、借星数据来自 API 返回的 chart 字段。
- 前端不写入 localStorage/sessionStorage/cookie。

### 未支持范围

- 农历输入
- `Gender.unknown`
- 真太阳时精确校正（无 longitude 时使用时区推算近似经度，偏差可能较大）
- 大限、流年、流月、流日、流时
