# CHART_FACTS_COMPLETENESS_AUDIT.md

## Purpose

审计文墨天机参考字段、`iztro-py` 原始输出、当前 `RawChart` / `NormalizedChart`、当前 `chart_facts` / Prompt 输入之间的信息流，识别已经可获得但未传给 LLM 的事实，并明确记录不可支持字段。

## 审计矩阵

### 基本信息

| 字段/信息类别 | 文墨天机参考是否包含 | iztro-py 原始输出是否可获得 | RawChart/NormalizedChart 是否保留 | chart_facts/Prompt 是否传入 | 本轮处理结论 |
|-------------|-------------------|------------------------|--------------------------|----------------------|------------|
| 性别 | ✓ | ✓ | ✓ (birth_info_snapshot) | ✓ | 已支持 |
| 经度 | ✓ | ✗ (外部输入) | ✓ (birth_info_snapshot) | ✗ | `available_but_not_exposed` - 非本轮重点 |
| 钟表时间 | ✓ | ✓ | ✓ (birth_info_snapshot) | ✗ | `available_but_not_exposed` - 非本轮重点 |
| 真太阳时 | ✓ | ✗ (本程序计算) | ✗ | ✗ | `available_but_not_exposed` - 非本轮重点 |
| 农历时间 | ✓ | ? (需验证) | ✓ (lunar_info，但可能为空) | ✗ | `provider_unknown` - 待确认 iztro-py 是否提供 |

### 四柱

| 字段/信息类别 | 文墨天机参考是否包含 | iztro-py 原始输出是否可获得 | RawChart/NormalizedChart 是否保留 | chart_facts/Prompt 是否传入 | 本轮处理结论 |
|-------------|-------------------|------------------------|--------------------------|----------------------|------------|
| 节气四柱 | ✓ | ? | ✗ | ✗ | `provider_unknown` - 待确认 |
| 非节气四柱 | ✓ | ? | ✗ | ✗ | `provider_unknown` - 待确认 |

### 命盘身份

| 字段/信息类别 | 文墨天机参考是否包含 | iztro-py 原始输出是否可获得 | RawChart/NormalizedChart 是否保留 | chart_facts/Prompt 是否传入 | 本轮处理结论 |
|-------------|-------------------|------------------------|--------------------------|----------------------|------------|
| 五行局 | ✓ | ? | ✓ (five_elements_class) | ✓ | `supported_now` |
| 命主 | ✓ | ? | ✗ | ✗ | `provider_unknown` |
| 身主 | ✓ | ? | ✗ | ✗ | `provider_unknown` |
| 子年斗君 | ✓ | ? | ✗ | ✗ | `unsupported_v0.1` |
| 身宫 | ✓ | ✓ | ✓ (is_body_palace) | ✓ | `supported_now` |

### 十二宫：宫名、天干、地支

| 字段/信息类别 | 文墨天机参考是否包含 | iztro-py 原始输出是否可获得 | RawChart/NormalizedChart 是否保留 | chart_facts/Prompt 是否传入 | 本轮处理结论 |
|-------------|-------------------|------------------------|--------------------------|----------------------|------------|
| 宫名 | ✓ | ✓ | ✓ (name) | ✓ | `supported_now` |
| 宫位 index | ✓ | ✓ | ✓ (index) | ✓ | `supported_now` |
| 天干 | ✓ | ✓ | ✓ (heavenly_stem) | ✗ | **`available_but_not_exposed` - 本轮处理** |
| 地支 | ✓ | ✓ | ✓ (earthly_branch) | ✗ | **`available_but_not_exposed` - 本轮处理** |

### 十二宫：星曜状态

| 字段/信息类别 | 文墨天机参考是否包含 | iztro-py 原始输出是否可获得 | RawChart/NormalizedChart 是否保留 | chart_facts/Prompt 是否传入 | 本轮处理结论 |
|-------------|-------------------|------------------------|--------------------------|----------------------|------------|
| 主星名称 | ✓ | ✓ | ✓ (stars with category='major') | ✓ (但为字符串列表) | `supported_now` - 需升级为结构化 |
| 辅星名称 | ✓ | ✓ | ✓ (stars with category='minor') | ✓ (但为字符串列表) | `supported_now` - 需升级为结构化 |
| 杂曜名称 | ✓ | ✓ | ✓ (stars with category='adjective') | ✓ (但为字符串列表) | `supported_now` - 需升级为结构化 |
| 星曜亮度 | ✓ | ✓ | ✓ (Star.brightness) | ✗ | **`available_but_not_exposed` - 本轮处理** |
| 星曜类别 | ✓ | ✓ | ✓ (Star.category) | ✗ (隐式区分) | **`available_but_not_exposed` - 本轮显式处理** |
| 生年四化 | ✓ | ✓ | ✓ (four_hua + palace.four_hua) | ✓ | `supported_now` |
| 自化/向心/离心 | ✓ (倪师体系) | ? | ✗ | ✗ | `provider_unknown` / `unsupported_v0.1` |

### 宫位关系

| 字段/信息类别 | 文墨天机参考是否包含 | iztro-py 原始输出是否可获得 | RawChart/NormalizedChart 是否保留 | chart_facts/Prompt 是否传入 | 本轮处理结论 |
|-------------|-------------------|------------------------|--------------------------|----------------------|------------|
| 对宫 | ✓ | ✗ (但可计算) | ✓ (opposite_palace_index) | ✓ | `supported_now` |
| 三方四正 | ✓ | ✗ (但可计算) | ✓ (san_fang_si_zheng_indexes) | ✓ | `supported_now` |
| 空宫借星 | ✓ | ✗ (但可计算) | ✓ (is_empty + borrowed_from_index + borrowed_major_stars) | ✓ | `supported_now` |

### 神煞

| 字段/信息类别 | 文墨天机参考是否包含 | iztro-py 原始输出是否可获得 | RawChart/NormalizedChart 是否保留 | chart_facts/Prompt 是否传入 | 本轮处理结论 |
|-------------|-------------------|------------------------|--------------------------|----------------------|------------|
| 岁前星 | ✓ | ? | ✗ | ✗ | `provider_unknown` |
| 将前星 | ✓ | ? | ✗ | ✗ | `provider_unknown` |
| 十二长生 | ✓ | ? | ✗ | ✗ | `unsupported_v0.1` |
| 太岁煞禄 | ✓ | ? | ✗ | ✗ | `unsupported_v0.1` |

### 时间层

| 字段/信息类别 | 文墨天机参考是否包含 | iztro-py 原始输出是否可获得 | RawChart/NormalizedChart 是否保留 | chart_facts/Prompt 是否传入 | 本轮处理结论 |
|-------------|-------------------|------------------------|--------------------------|----------------------|------------|
| 大限 | ✓ | ? | ✗ | ✗ | `unsupported_v0.1` |
| 小限 | ✓ | ? | ✗ | ✗ | `unsupported_v0.1` |
| 流年 | ✓ | ? | ✗ | ✗ | `unsupported_v0.1` |
| 限流叠宫 | ✓ | ? | ✗ | ✗ | `unsupported_v0.1` |

## 关键发现

### 已可获得但 chart_facts 未暴露字段（本轮处理）

1. **Star.brightness**：`iztro-py` 已提供，`iztro_provider.py` 已读取并存储到 `Star.brightness`，但 `chart_facts.py` 只保留星曜名称字符串。
2. **Star.category**：`iztro-py` 已提供，`iztro_provider.py` 已读取并存储到 `Star.category`，但 `chart_facts.py` 隐式区分（通过筛选 category），未显式传递给 LLM。
3. **Palace.heavenly_stem**：`iztro-py` 已提供，`iztro_provider.py` 已读取并存储到 `Palace.heavenly_stem`，但 `chart_facts.py` 未传递。
4. **Palace.earthly_branch**：`iztro-py` 已提供，`iztro_provider.py` 已读取并存储到 `Palace.earthly_branch`，但 `chart_facts.py` 未传递。

### 待确认 provider 能力字段（本轮记录，不处理）

1. **农历信息**：`NormalizedChart.lunar_info` 字段存在但可能为空，需确认 `iztro-py` 是否提供。
2. **四柱**：不清楚 `iztro-py` 是否提供节气四柱或非节气四柱。
3. **命主、身主**：不清楚 `iztro-py` 是否提供。
4. **自化/向心/离心**：倪师体系特有，`iztro-py` 可能不支持。
5. **神煞**：岁前星、将前星、十二长生、太岁煞禄等，需确认 `iztro-py` 是否提供。

### v0.1 明确不支持字段

1. **大限、流年、流月、流日、流时**：时间层计算。
2. **子年斗君**：时间层相关。
3. **自化/向心/离心**：倪师体系特有，即使 provider 提供也本轮不做。
4. **神煞系统**：岁前星、将前星、十二长生、太岁煞禄等。

## Branch 15: iztro-py 原始输出快照与字段能力审计

Branch 15 通过直接调用 `iztro-py` 并序列化原始对象，确认了以下字段能力：

### 已确认的 iztro-py 原生字段

| 字段 | iztro-py 字段路径 | 类型 | 样例值 | mingmax 当前状态 |
|------|------------------|------|-------|-----------------|
| 五行局 | `astrolabe.five_elements_class` | str | "土五局" | ✓ 已支持 (`five_elements_class`) |
| 农历日期 | `astrolabe.lunar_date` | str | "一九九〇年四月廿一" | ✗ 未暴露 (lunar_info 为空) |
| 中文日期 | `astrolabe.chinese_date` | str | "庚午 辛巳 庚辰 癸未" | ✗ 未暴露 |
| 身宫地支 | `astrolabe.earthly_branch_of_body_palace` | str | "ziEarthly" | ✗ 未暴露 |
| 命宫地支 | `astrolabe.earthly_branch_of_soul_palace` | str | "xuEarthly" | ✗ 未暴露 |
| 身宫类型 | `astrolabe.body` | str | "huoxingMin" | ✗ 未暴露 |
| 大限信息 | `palace[].decadal` | Decadal object | {heavenly_stem, earthly_branch, range} | ✗ 未暴露 |
| 宫位天干 | `palace[].heavenly_stem` | str | "wuHeavenly" | ✓ 已暴露 (heavenly_stem) |
| 宫位地支 | `palace[].earthly_branch` | str | "yinEarthly" | ✓ 已暴露 (earthly_branch) |
| 星曜名称 | `star.name` | str | "tianchu" | ✓ 已暴露 |
| 星曜类型 | `star.type` | str | "adjective" | ✓ 已暴露 (category) |
| 星曜范围 | `star.scope` | str | "origin" | ✗ 未暴露 |

### TS 参考项目字段来源分析

| TS 字段 | 实际来源 | mingmax 是否应复用 |
|---------|---------|-------------------|
| `LunarInfo` (lunarYear, lunarMonth, lunarDay, isLeapMonth) | 来自 `lunar-javascript` 库，**非** iztro 原生 | ✗ 需额外历法库，iztro 只提供字符串 |
| `Star.type = 'lucky'\|'sha'` | TS 项目规则映射，**非** iztro 原生类型 | ✗ iztro 原生类型为 major/minor/adjective |
| `Star.brightness` | iztro 原生有 `brightness` 字段 | ✓ 可复用 |
| `Star.siHua` | iztro 原生有 `mutagen` 字段 | ✓ 可复用（已作为四化） |
| `DaXian` (大限) | iztro 原生有 `decadal` 对象 | ✓ 可复用，但 v0.1 不实现大限分析 |
| `ziweiPos` | 派生字段（计算紫微星位置） | ✗ mingmax 可自行计算 |
| `currentAge`, `currentDaXianIndex` | 派生字段（基于用户年龄） | ✗ mingmax 可自行计算 |

### 更新后的字段状态

| 字段类别 | Branch 14 状态 | Branch 15 确认状态 | 说明 |
|---------|---------------|-------------------|------|
| 五行局 | `supported_now` | `provider_supported` | iztro 原生提供，mingmax 已支持 |
| 农历日期 | `provider_unknown` | `provider_supported` | iztro 原生提供字符串，mingmax 未暴露 |
| 中文日期/四柱 | `provider_unknown` | `provider_supported` | iztro 提供四柱字符串，mingmax 未暴露 |
| 大限信息 | `unsupported_v0.1` | `provider_supported` | iztro 原生提供，v0.1 不做分析 |
| 身宫地支 | `provider_unknown` | `provider_supported` | iztro 原生提供，mingmax 可计算 |
| 命宫地支 | `provider_unknown` | `provider_supported` | iztro 原生提供，mingmax 可计算 |
| 星曜范围 | `provider_unknown` | `provider_supported` | iztro 原生提供，mingmax 未暴露 |

### 可直接暴露的字段（无需 schema 变更）

以下字段 `iztro-py` 已提供且 mingmax schema 已能承载，建议优先暴露：

1. **农历信息** (`lunar_date`) - 从 `astrolabe.lunar_date` 到 `NormalizedChart.lunar_info`
2. **中文日期/四柱** (`chinese_date`) - 新增字段到 `NormalizedChart`
3. **身宫地支** (`earthly_branch_of_body_palace`) - 可用于验证或派生字段
4. **命宫地支** (`earthly_branch_of_soul_palace`) - 可用于验证或派生字段

### 需要额外派生的字段

以下字段 TS 项目有但 iztro 不直接提供结构化数据：

1. **结构化 LunarInfo** (lunarYear, lunarMonth, lunarDay, isLeapMonth) - 需要解析 `lunar_date` 字符串或引入 `lunar-javascript` 类库
2. **命主、身主** - 需要额外规则计算，iztro 不提供
3. **自化/向心/离心** - 倪师体系特有，iztro 不支持

### 不应复用的 TS 项目设计

1. **Star.type = 'lucky'\|'sha'** - TS 项目自定义映射，iztro 原生为 major/minor/adjective，应保持 iztro 分类
2. **完整 chart 对象入 Prompt** - mingmax 使用 `chart_facts + evidence_id + validator` 模式，不照搬 TS 的整包 chart 入 prompt


## 本轮处理计划

### 必做

1. 将 `chart_facts` 中星曜字段从字符串列表升级为结构化对象：
   ```python
   major_stars: [
     {"name": "紫微", "brightness": "庙", "category": "major", "evidence_id": "star:0:紫微"}
   ]
   ```
2. 补充宫位天干地支到 `chart_facts`。
3. 更新 Prompt 描述完整事实包，禁止 unsupported 字段。
4. 确保 `evidence_index` 与结构化星曜/四化事实中的 `evidence_id` 一致。

### 不做

1. 不补算、伪造 `iztro-py` 不提供的字段。
2. 不实现大限、流年、流月、流日、流时。
3. 不引入神煞、四柱、自化等未确认字段。
4. 不改动公开 API 响应结构。
