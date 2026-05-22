# ziwei-doushu TS 项目借鉴分析

## 背景

参考项目路径：`/home/liam/git/ziwei-doushu`

该项目是一个 TypeScript / Next.js 紫微斗数项目，核心排盘代码集中在 `lib/ziwei/`，界面集中在 `components/` 和 `app/`。它与 mingmax 的定位不同：参考项目更像完整前端产品和内容站，mingmax 当前 v0.1 是 Python FastAPI 后端 + 简单前端 + LLM Agent 分析闭环。

本分析只评估可借鉴的工程和产品设计，不建议迁移到 Next.js，也不建议照搬其中较重的运营、SEO、合盘、会员或内容站能力。

## 总体结论

参考项目有四类值得借鉴的能力：

1. **排盘输入口径更明确**：它显式处理经度、真太阳时时辰、晚子时按次日排盘等边界。
2. **命盘结构更丰富**：它的 `ZiweiChart` 明确包含命宫、身宫、五行局、紫微位置、十二宫、大限、当前大限、星曜类型、亮度、四化、空宫借对宫等字段。
3. **确定性分析层更强**：它有格局识别、三方四正、对宫、夹宫、四化叠加等规则函数，能先给 LLM 提供结构化证据。
4. **交互式命盘体验更成熟**：它的命盘盘面、宫位详情、四化 badge、时间视图、大限/流年切换、格局卡片都能启发 mingmax 后续前端。

但不能直接照搬：

- 参考项目 README 明确说后端 API 和 AI prompt 未开源，`/api/generate`、`/api/interpret` 等能力不可直接复用。
- 本地代码存在部分引用不完整的迹象，例如 `lib/seo/knowledge.ts` 引用 `lib/ziwei/db-analysis`，但当前目录中未看到对应文件。
- 合盘和断语知识库中存在较强宿命化、恐吓式表述，不符合 mingmax 当前安全边界，需要重写为克制、可解释、可追问的表达。
- 参考项目偏前端产品和 SEO 内容站，mingmax 当前不应引入复杂前端、SEO 知识页或合盘模块。

## 可借鉴点

### 1. 出生输入与时辰口径

参考文件：

- `/home/liam/git/ziwei-doushu/components/BirthForm.tsx`
- `/home/liam/git/ziwei-doushu/lib/ziwei/share.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/cities.ts`

值得借鉴：

- 用城市经度计算真太阳时对应时辰：`(longitude - 120) * 4` 分钟。
- 表单层实时展示真太阳时时辰，降低用户输入误解。
- 晚子时规则明确：`23:00-23:59` 按次日排盘，`00:00-00:59` 按本日排盘。
- 城市经纬度字典可作为前端便利输入来源。

对 mingmax 的建议：

- Branch 9 优先把输入口径显式化，尤其是：
  - 是否使用真太阳时；
  - 使用钟表时间还是校正后时间；
  - 晚子时是否跨日；
  - 经度缺失时如何处理。
- 当前 `BirthInfo` 已有 `timezone` 和 `longitude`，但缺少“是否启用真太阳时”这样的显式开关。现在 provider 只要有 `longitude` 就自动校正，容易造成用户和参考网站口径不一致。
- 建议新增字段或内部配置：`time_correction_mode = "clock_time" | "true_solar_time"`，默认策略要写进 `.supports/API_SPEC.md` 和 `.supports/DECISIONS.md`。

### 2. 命盘 Schema 结构

参考文件：

- `/home/liam/git/ziwei-doushu/lib/ziwei/types.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/algorithm.ts`

参考项目的 `ZiweiChart` 包含：

- `birthInfo`
- `lunarInfo`
- `mingGongBranch`
- `shenGongBranch`
- `wuxingJu`
- `wuxingJuName`
- `ziweiPos`
- `palaces`
- `daXians`
- `currentAge`
- `currentDaXianIndex`

参考项目的 `Palace` 包含：

- 地支、天干、宫名；
- 星曜列表；
- 大限年龄段；
- 是否命宫、身宫、当前大限；
- 对宫；
- 是否空宫；
- 借宫来源和借到的主星。

对 mingmax 的建议：

- 当前 `NormalizedChart` 只有 `chart_id`、`source`、`summary`、`palaces`、`four_hua`，不足以支撑稳定分析。
- 建议在 Branch 9 或后续分支补充最小关键字段：
  - `ming_palace_index` 或 `ming_palace_branch`
  - `body_palace_index` 或 `body_palace_branch`
  - `lunar_info`
  - `five_elements_class`
  - `current_age`
  - `decadal_ranges`
  - `opposite_palace_index`
  - `is_empty`
  - `borrowed_from`
  - `borrowed_major_stars`
- 这样 LLM 的输入可以从“十二宫星曜列表”升级为“可验证的命盘事实图”，减少模型误读。

### 3. 星曜分类与亮度映射

参考文件：

- `/home/liam/git/ziwei-doushu/lib/ziwei/algorithm.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/constants.ts`

值得借鉴：

- 明确区分 `major`、`minor`、`lucky`、`sha`。
- 亮度从中文庙旺利陷映射为稳定枚举：`bright`、`normal`、`dim`。
- 对吉星、煞星做集合归类，便于后续规则判断和前端视觉表达。

对 mingmax 的建议：

- 当前 `Star.category` 使用字符串，建议收敛为枚举或至少在 provider 层集中映射。
- 保留原始亮度文本，同时增加归一化亮度字段，避免后续规则层反复解析中文。
- 不要把“星曜分类”交给 LLM 判断，应由 Engine/Normalizer 确定。

### 4. 四化与时间层叠加

参考文件：

- `/home/liam/git/ziwei-doushu/lib/ziwei/sihua.ts`
- `/home/liam/git/ziwei-doushu/components/TimeNav.tsx`
- `/home/liam/git/ziwei-doushu/components/PalaceCell.tsx`

值得借鉴：

- 四化表被独立放在常量层。
- 有本命、大限、流年、流月四化的纯函数接口。
- 前端通过时间视图叠加四化 badge，而不是改变原始本命盘。

对 mingmax 的建议：

- v0.1 不必完整实现大限、流年、流月，但可以先确定数据模型：
  - `native_four_hua`
  - `decadal_four_hua`
  - `annual_four_hua`
  - `overlay_source`
- 如果暂不支持动态四化，应明确返回 unsupported 或 omitted，不要让 LLM 自行补算。
- 前端后续可以借鉴“本命 / 大限 / 流年”分段视图，但数据必须来自后端确定性结构。

### 5. 三方四正、对宫、空宫借星

参考文件：

- `/home/liam/git/ziwei-doushu/lib/ziwei/patterns.ts`
- `/home/liam/git/ziwei-doushu/components/ChartBoard.tsx`

值得借鉴：

- 三方四正函数明确：本宫、对宫、两个三合宫。
- 空宫时预先计算 `borrowedFromBranch`、`borrowedFromName`、`borrowedStars`。
- 前端选中宫位时高亮三方四正，帮助用户理解分析证据。

对 mingmax 的建议：

- 在 Normalizer 中预先计算对宫、三方四正、空宫借星，而不是让 prompt 里写“请自行判断”。
- LLM prompt 可以引用这些结构化字段，例如“关系主题只允许引用夫妻宫、福德宫、迁移宫及其三方四正证据”。
- 这会显著提升 LLM 输出的可解释性和一致性。

### 6. 格局识别规则层

参考文件：

- `/home/liam/git/ziwei-doushu/lib/ziwei/patterns.ts`

值得借鉴：

- 将格局识别作为确定性规则层，而不是完全交给 LLM。
- 每个格局包含：
  - `name`
  - `level`
  - `description`
  - `palaces`
  - `conditions.required`
  - `conditions.bonus`
  - `conditions.breaking`
  - `source`
- 规则中大量使用三方四正、夹宫、煞星数量、庙旺落陷等可计算条件。

对 mingmax 的建议：

- 不建议一次性移植 1000+ 行规则库。
- 建议先实现小型规则层：`app/engines/chart_patterns.py`，只覆盖 5-10 个基础、低争议、可测试的结构：
  - 命宫主星摘要；
  - 空宫借对宫；
  - 三方四正主星集合；
  - 本命四化落宫；
  - 煞星集中提示；
  - 当前大限宫位提示。
- 输出应是结构化证据，不直接给宿命化结论。LLM 再基于这些证据生成克制表达。

### 7. 知识库组织

参考文件：

- `/home/liam/git/ziwei-doushu/lib/classics/index.ts`
- `/home/liam/git/ziwei-doushu/lib/classics/data/*`
- `/home/liam/git/ziwei-doushu/lib/seo/knowledge.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/heming-knowledge.ts`

值得借鉴：

- 古籍文本、星曜知识、合盘方法论与算法代码分离。
- 古籍检索是静态数据 + 本地搜索，不依赖外部服务。
- 内容有结构化入口，便于页面展示或 prompt 引用。

对 mingmax 的建议：

- v0.1 可以先新增轻量知识资产目录，例如 `app/knowledge/ziwei/` 或 `.supports/KNOWLEDGE_GUIDE.md`。
- 只收录可追溯、可安全改写、可引用的短条目，不要直接塞大段断语给 LLM。
- 知识条目建议结构：
  - `topic`
  - `source`
  - `claim`
  - `safe_expression`
  - `risk_level`
  - `applicable_chart_factors`
- 合盘知识库不属于 v0.1 范围，暂不做。

### 8. 前端命盘体验

参考文件：

- `/home/liam/git/ziwei-doushu/components/ChartBoard.tsx`
- `/home/liam/git/ziwei-doushu/components/PalaceCell.tsx`
- `/home/liam/git/ziwei-doushu/components/ChartSummary.tsx`
- `/home/liam/git/ziwei-doushu/components/PatternsCard.tsx`
- `/home/liam/git/ziwei-doushu/components/StarDetailPanel.tsx`

值得借鉴：

- 4x4 十二宫盘面比纯文本报告更适合核验排盘准确性。
- 宫位单元格显示宫名、干支、主星、吉星、煞星、四化、大限年龄。
- 选中宫位后高亮三方四正。
- 中央区域展示命宫、身宫、五行局、当前大限。
- 摘要卡片先展示确定性事实，再进入解释。

对 mingmax 的建议：

- 当前简单前端可以保留，但下一个前端增强任务应优先做“排盘核验视图”，不是营销页。
- 建议最小前端增强：
  - 十二宫 4x4 静态盘；
  - 命宫/身宫标记；
  - 星曜分类颜色；
  - 四化 badge；
  - 点击宫位展示三方四正；
  - 原始 JSON 折叠面板，方便 debug。

### 9. 隐私处理

参考文件：

- `/home/liam/git/ziwei-doushu/app/chart/page.tsx`
- `/home/liam/git/ziwei-doushu/lib/ziwei/history.ts`

值得借鉴：

- 参考项目主动关闭分享功能，原因是分享卡可能暴露出生日期和城市。
- 历史记录只保存在浏览器 localStorage，避免默认上传服务端。

对 mingmax 的建议：

- 继续保持 `.supports/TEST_INFO_EVA.md` 私密样本不得入库。
- 前端历史记录如后续实现，应默认本地存储，并提供清除能力。
- 分享功能必须先设计脱敏策略，不应直接把出生信息放 URL。

## 不建议借鉴或需要谨慎处理的点

### 1. 不要引入 Next.js / React 作为当前主线

mingmax 当前 v0.1 的前端目标是简单验证工具，不是完整内容站。引入 Next.js 会增加构建、部署、状态管理和前后端边界复杂度，违背当前“简单、可测试、可替换”的原则。

### 2. 不要照搬宿命化断语

参考项目的合盘和部分星曜断语中存在强烈判断，例如婚姻、疾病、灾祸、死亡等绝对化表达。mingmax 必须保持当前安全边界：文化研究、娱乐体验、自我反思，不输出恐吓式或确定性结论。

### 3. 不要把 SEO 知识页作为 v0.1 目标

参考项目有 14 主星 × 多主题的 SEO 内容页能力，但 mingmax 当前没有内容站目标。知识库可以借鉴结构，不应扩展成 SEO 工程。

### 4. 不要依赖参考项目的未开源 API

README 明确说明开源版不含后端 API 和 AI prompt。mingmax 应继续保留自己的 API -> Service -> Engine -> Agent -> LLM 分层。

### 5. 不要把参考项目作为准确性唯一标准

参考项目和文墨天机、`iztro-py` 可能存在流派、时辰、真太阳时、晚子时、闰月、四化口径差异。它更适合作为“结构设计参考”和“对比样本来源”，不是唯一真值。

## 建议落地顺序

### P0：服务当前 Branch 9

1. 显式化时间口径：钟表时间、真太阳时、晚子时跨日。
2. 扩充 `NormalizedChart` 的关键字段：命宫、身宫、五行局、农历信息、大限范围、对宫、空宫借星。
3. 新增字段级 chart diff，用脱敏 snapshot 验证 provider / normalizer 保真。
4. 本地私密样本只输出脱敏差异摘要。

### P1：提升 LLM 稳定性

1. 新增确定性 `chart_facts` / `chart_evidence` 层。
2. Prompt 中要求 LLM 只引用这些事实，不得自行推算。
3. 对每个主题生成 `supporting_evidence` 时引用宫位、星曜、四化和三方四正路径。

### P2：前端核验视图

1. 用原生 HTML/CSS/JS 做 4x4 十二宫盘。
2. 支持命宫、身宫、四化、高亮三方四正。
3. 展示 chart source、时间口径和是否启用真太阳时。

### P3：小型规则库

1. 先做 5-10 个低争议规则。
2. 规则只输出结构化证据和风险等级。
3. LLM 负责把证据解释为克制表达。

## 对 Claude 的后续任务建议

如果让 Claude 执行下一步，可以把任务收敛为：

> 参考 `/home/liam/git/ziwei-doushu` 的 `types.ts`、`algorithm.ts`、`share.ts`、`patterns.ts`，在 mingmax 中增强排盘结构保真，不迁移前端框架、不照搬断语。优先补齐 `NormalizedChart` 的命宫、身宫、五行局、农历信息、对宫、空宫借星、三方四正字段，并新增脱敏 chart diff 测试。不得提交 `.supports/TEST_INFO_EVA.md`，不得将私密样本写入代码或测试。

## 参考文件清单

- `/home/liam/git/ziwei-doushu/lib/ziwei/types.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/algorithm.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/constants.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/sihua.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/patterns.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/share.ts`
- `/home/liam/git/ziwei-doushu/lib/ziwei/cities.ts`
- `/home/liam/git/ziwei-doushu/components/ChartBoard.tsx`
- `/home/liam/git/ziwei-doushu/components/PalaceCell.tsx`
- `/home/liam/git/ziwei-doushu/components/TimeNav.tsx`
- `/home/liam/git/ziwei-doushu/components/BirthForm.tsx`
- `/home/liam/git/ziwei-doushu/components/ChartSummary.tsx`
- `/home/liam/git/ziwei-doushu/components/PatternsCard.tsx`
- `/home/liam/git/ziwei-doushu/lib/classics/index.ts`
- `/home/liam/git/ziwei-doushu/lib/seo/knowledge.ts`
- `/home/liam/git/ziwei-doushu/app/chart/page.tsx`
