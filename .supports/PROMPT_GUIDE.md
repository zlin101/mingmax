# PROMPT_GUIDE.md

## Prompt 总原则

Prompt 是 mingmax 的核心资产，必须独立管理。Prompt 不得大量硬编码在业务逻辑中。

所有 Prompt 必须要求模型：

- 只基于给定 `chart_facts` 结构化证据分析，不得从原始宫位列表自行推理；
- 不得虚构 `chart_facts` 中不存在的星曜、宫位、四化、对宫、三方四正、空宫借星；
- 当前支持本命盘与大限区间级辅助分析，可以引用 chart_facts 中明确提供的 decadal facts；
- 禁止引用流年、流月、流日、流时等不支持的时间层；
- 不得自行推算命宫、身宫、四化、对宫、三方四正、空宫借星等确定性关系；
- 关键判断应附带 `evidence_index` 中的证据 ID 作为可追溯依据；
- 星曜-宫位和四化-宫位描述必须与 chart_facts 中的实际绑定一致；
- 区分强结论、弱假设和待确认问题；
- 避免绝对化、恐吓式、宿命论表达；
- 输出克制、可解释、可追问；
- 必要时输出结构化结果；
- 在报告中包含免责声明。

## 证据 ID 体系

`chart_facts.evidence_index` 提供稳定的证据 ID，LLM 可引用：

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

## chart_facts 完整事实包

`chart_facts` 是本命盘的完整可用事实包，包含：

### 宫位基础信息
- `index`：宫位索引（0-11）
- `name`：宫位名称
- `heavenly_stem`：天干（如"甲"）
- `earthly_branch`：地支（如"寅"）
- `is_body_palace`：是否为身宫

### 星曜结构化事实
- `major_star_facts`：主星列表，每个星包含：
  - `name`：星名
  - `brightness`：亮度（庙/旺/得/利/平/陷）
  - `category`：类别（major/minor/adjective）
  - `evidence_id`：证据 ID（格式：`star:<宫位索引>:<星名>`）
- `minor_star_facts`：辅星列表，结构同上
- `adjective_star_facts`：杂曜列表，结构同上

### 兼容性字段（向后兼容）
- `major_stars`：主星名称字符串列表
- `minor_stars`：辅星名称字符串列表
- `adjective_stars`：杂曜名称字符串列表

### 宫位四化
- `mutagens`：该宫位的四化字典，如 `{"化禄": "紫微", "化忌": "天机"}`
- 全局四化见 `four_hua` 字典

### 宫位关系
- `opposite_palace`：对宫名称
- `san_fang_si_zheng`：三方四正宫位列表
- `is_empty`：是否为空宫
- `borrowed_from`：借星来源，包含 `palace_name` 和 `major_stars`

### 命盘全局信息
- `ming_palace`：命宫名称
- `body_palace`：身宫名称
- `five_elements_class`：五行局
- `four_hua`：全局四化字典

### 证据索引
- `evidence_index`：所有结构化事实的证据 ID 和标签列表

## 证据一致性检查

`app/agents/analysis_evidence_validator.py` 的 `validate_analysis_output()` 会在每次分析后检查：

- LLM 输出不得引用 `chart_facts` 中不存在的星曜、宫位、四化；
- 不得引用不存在的 evidence_index ID；
- 星曜-宫位绑定一致性（如”XX在YY宫”是否与 chart_facts 一致）；
- 四化-宫位绑定一致性（如”YY宫XX化Z”是否与 chart_facts 一致）；
- 禁止引用流年、流月、流日、流时等不支持的时间层（大限已支持）；
- 不得包含绝对化/恐吓式表达（”必然””一定会””注定”等）；
- 报告必须包含免责声明。

检查结果为 `list[ValidationIssue]`，severity 为 `error` 或 `warning`。ValidationIssue code 包括：

| Code | 说明 |
|------|------|
| `FABRICATED_STAR` | 引用不存在的星曜 |
| `FABRICATED_PALACE` | 引用不存在的宫位 |
| `FABRICATED_MUTAGEN` | 引用不存在的四化 |
| `FABRICATED_EVIDENCE_ID` | 引用不存在的证据 ID |
| `INVALID_STAR_PALACE_BINDING` | 星曜-宫位绑定不一致 |
| `INVALID_MUTAGEN_PALACE_BINDING` | 四化-宫位绑定不一致 |
| `UNSUPPORTED_TIME_LAYER` | 引用不支持的时间层概念 |
| `UNSAFE_EXPRESSION` | 绝对化/恐吓式表达 |
| `MISSING_DISCLAIMER` | 报告缺少免责声明 |

## 禁止输出

禁止生成类似表述：

- “你一定会失败。”
- “你必然离婚。”
- “你命中注定贫穷。”
- “你一定会有重大疾病。”

推荐表达：

> 从当前命盘结构看，这可能提示某种倾向或压力模式，更适合作为文化解释和自我观察参考，而不是确定性结论。

## 报告免责声明

Markdown 报告必须包含：

> 本分析仅供文化研究、娱乐体验与自我反思参考，不构成医学、法律、财务、心理诊断或人生决策依据。

## Prompt 文件

- `app/prompts/ziwei_analysis.md`
- `app/prompts/theme_analysis.md`
- `app/prompts/followup_questions.md`
- `app/prompts/report.md`
