# AGENTS.md

## 项目名称

mingmax

## 项目定位

mingmax 是一个面向 Agent 的综合分析项目，当前以紫微斗数为起点，后续逐步扩展到八字、MBTI、其他心理测评与多体系交叉验证。

当前阶段为 `v0.1`，只聚焦「紫微斗数 + LLM Agent 分析」闭环。

核心原则：

> 程序负责算准，LLM 负责讲透，Agent 负责组织分析流程、追问与校准。

---

## 当前范围

v0.1 只实现：

- 出生信息输入；
- 程序化紫微排盘；
- 命盘标准化为内部结构；
- 基于 LLM 的紫微语义分析；
- 主题分析；
- 宫位交叉验证；
- 追问问题生成；
- Markdown 报告生成。

除非用户明确要求，否则不要实现：

- 八字模块；
- MBTI 模块；
- 大五人格等其他测评模块；
- 多体系交叉验证；
- 用户系统；
- 支付系统；
- 复杂前端；
- 向量数据库；
- 任务队列；
- 复杂多 Agent 框架。

---

## 技术栈

| 类别 | 选型 | 版本要求 |
|------|------|----------|
| 语言 | Python | >=3.14 |
| Web 框架 | FastAPI | latest |
| 包管理 | **uv** | latest |
| 代码格式化 | Black | >=26.3.1 |
| import 排序 | isort | >=8.0.1 |
| 代码检查 | flake8 | >=7.3.0 |
| 测试 | pytest | >=9.0.3 |
| 异步测试 | pytest-asyncio | latest |
| 测试覆盖率 | pytest-cov | >=7.1.0 |
| 提交规范 | gitlint（pre-commit 钩子） | — |

---

## 开发前必须阅读

在进行任何非琐碎开发任务前，必须先阅读：

- `AGENTS.md`
- `.supports/PROJECT_CONTEXT.md`
- `.supports/DECISIONS.md`
- `.supports/ARCHITECTURE.md`
- `.supports/TASKS.md`

如果 `.supports/` 下的文件不存在，应优先创建简洁初始版本，而不是直接开始写业务代码。

---

## 包管理：uv

**所有包管理操作必须使用 `uv`，禁止使用 `pip` 或 `poetry`。**

```bash
uv add <package>          # 添加运行时依赖
uv add --dev <package>    # 添加开发依赖
uv sync                   # 同步/安装所有依赖
uv run <command>          # 在项目虚拟环境中运行命令
uv lock                   # 更新 uv.lock
```

生成代码时如引入新依赖，必须告知执行 `uv add` 命令。

不要在代码注释、README 或文档中写 `pip install`。

---

## 文档职责

`AGENTS.md` 只保留顶层、稳定、长期有效的项目约束。

详细且会频繁变化的内容放入 `.supports/`：

- `.supports/PROJECT_CONTEXT.md`  
  项目背景、目标、当前阶段、范围边界。

- `.supports/DECISIONS.md`  
  已确认的架构决策、技术选型和关键约束。

- `.supports/ARCHITECTURE.md`  
  系统结构、分层设计、数据流、模块职责。

- `.supports/TASKS.md`  
  当前任务、已完成工作、待办事项和开发节点。

- `.supports/PROMPT_GUIDE.md`  
  Prompt 设计规则、LLM 输出要求、报告风格、安全边界。

- `.supports/API_SPEC.md`  
  API 契约、请求/响应示例、错误格式。

- `.supports/DEVELOPMENT_GUIDE.md`  
  代码风格、测试规范、依赖管理、常用命令。

涉及架构、API 契约、数据 Schema、Prompt 流程、LLM 行为、紫微排盘逻辑等变化时，必须更新对应 `.supports/` 文档。

重要设计决策必须记录到 `.supports/DECISIONS.md`。

---

## 架构原则

项目必须保持清晰分层。

推荐顶层分层：

- API 层：请求校验与响应封装；
- Service 层：业务流程编排；
- Engine 层：确定性排盘、命盘标准化、规则计算；
- Agent 层：LLM 分析流程与 Prompt Pipeline；
- LLM 层：模型调用抽象；
- Schema 层：请求、响应、命盘、分析结果模型。

禁止跨层滥用：

- API 层不得直接调用 LLM；
- API 层不得直接写复杂业务逻辑；
- Agent 层不得直接负责紫微排盘；
- 第三方紫微库必须通过内部 Engine 封装；
- Prompt 不应大量硬编码在业务逻辑中；
- 外部模型 SDK 不得散落在业务代码中。

---

## 代码风格

### 必须遵守

1. **行宽上限 120 字符**，Black 已配置。
2. **默认不写注释**，代码即文档。仅当逻辑极其复杂、无法通过命名和结构表达时，才允许加入极简注释。
3. **类型注解**：所有函数参数和返回值必须有类型注解。
4. **异步优先**：IO 操作使用 `async/await`，包括 网络请求、外部 API 调用、异步数据库访问等。
5. **依赖注入**：通过 FastAPI `Depends` 传递依赖，不创建全局单例。
6. **配置集中管理**：端口、地址、模型名称、API Key、路径等配置必须通过 `Settings` 管理，不得硬编码。
7. **日志分级输出**：使用项目统一 logger，不使用 `print` 输出运行日志。
8. **小函数优先**：函数应聚焦单一职责，避免在一个函数中混合校验、业务编排、外部调用和响应拼装。

正确示例：

```python
async def get_cluster_info(
    cluster_id: str,
    service: ClusterService = Depends(get_cluster_service),
) -> ClusterInfo:
    return await service.fetch_info(cluster_id)
```

错误示例：

```python
def get_cluster_info(cluster_id):
    service = ClusterService()
    return service.fetch_info(cluster_id)
```

### 导入顺序

导入顺序由 isort 自动处理，分为：

1. 标准库；
2. 第三方库；
3. 本项目模块。

示例：

```python
from pathlib import Path

from fastapi import Depends
from pydantic import BaseModel

from app.services.chart_service import ChartService
```

### 注释与 docstring

默认不写注释和 docstring。

允许写注释的情况：

- 算法或历法逻辑较复杂；
- 紫微排盘规则存在特殊边界；
- 代码背后存在重要业务假设；
- 临时兼容第三方库的不直观行为。

不允许写无意义注释，例如：

```python
# 获取用户信息
user = get_user()
```

---

## 紫微排盘原则

紫微排盘必须由确定性程序完成，不允许让 LLM 直接推算命盘。

正确流程：

```text
BirthInfo -> ZiweiChartEngine -> RawChart -> NormalizedChart -> ZiweiAnalysisAgent
```

错误流程：

```text
BirthInfo -> LLM 直接排盘
```

LLM 可以解释命盘，但不得负责安星、定宫、四化、大限、流年等基础排盘逻辑。

---

## LLM 使用原则

LLM 用于：

- 命盘语义解释；
- 主题分析；
- 宫位关系说明；
- 交叉验证；
- 冲突解释；
- 追问问题生成；
- 报告生成；
- 术语通俗化表达。

LLM 不用于：

- 排盘计算；
- 日期/历法换算；
- 星曜落宫计算；
- 核心确定性业务逻辑；
- 未经验证的命盘事实生成。

所有 LLM 调用必须通过项目统一的 LLM 抽象层，不得在业务代码中散落调用第三方模型 SDK。

---

## Prompt 原则

Prompt 是项目核心资产。

Prompt 内容应放在独立文件或清晰隔离的 Prompt 模块中，不应散落硬编码在业务代码里。

Prompt 必须要求模型：

- 只基于给定结构化命盘分析；
- 不得虚构不存在的星曜、宫位、四化、大限或流年；
- 区分强结论、弱假设和待确认问题；
- 在需要时输出结构化结果；
- 避免绝对化、恐吓式、宿命论表达；
- 必要时包含娱乐、文化研究、自我反思用途声明。

---

## 输出安全边界

mingmax 的输出必须克制、可解释、可追问，避免绝对化判断。

禁止生成类似表述：

- “你一定会失败。”
- “你必然离婚。”
- “你命中注定贫穷。”
- “你一定会有重大疾病。”

推荐表达：

> 从当前命盘结构看，这可能提示某种倾向或压力模式，更适合作为文化解释和自我观察参考，而不是确定性结论。

报告必须包含免责声明：

> 本分析仅供文化研究、娱乐体验与自我反思参考，不构成医学、法律、财务、心理诊断或人生决策依据。

---

## 测试规范

确定性逻辑必须测试。

测试文件统一放在 `tests/` 目录，命名格式为：

```text
test_<模块名>.py
```

使用 `conftest.py` 管理公共 fixtures。

外部依赖必须 mock，保证单元测试可独立运行，包括：

- LLM API；
- 数据库；
- 网络请求；
- 第三方服务；
- 文件系统中的非临时路径。

覆盖目标：

- 核心逻辑覆盖率 >80%；
- 单元测试不得真实调用外部 LLM API；
- 单元测试不得依赖开发者本机环境变量；
- API 测试优先使用 `httpx.AsyncClient` 和 `ASGITransport`。

至少覆盖：

- 出生信息 Schema 校验；
- 紫微排盘 Engine 封装；
- 命盘标准化；
- Service 流程编排；
- API 请求/响应结构；
- Prompt 文件存在性或加载逻辑；
- Mock LLM Client 行为；
- 输出免责声明存在性；
- 异常分支和边界输入。

```python
# tests/conftest.py
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

```python
# tests/test_satellites.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_satellites(client: AsyncClient) -> None:
    response = await client.get("/api/v1/satellites")

    assert response.status_code == 200
```

---

## 开发规则

执行开发任务时必须遵守：

1. 先阅读必要上下文文档；
2. 再查看当前代码结构；
3. 明确本次任务边界；
4. 不做超出任务范围的大规模重构；
5. 确定性逻辑必须补充或更新测试；
6. 涉及设计变化时更新对应 `.supports/` 文档；
7. 重要设计决策必须写入 `.supports/DECISIONS.md`；
8. 最后总结修改文件、测试结果和设计决策。

---

## 依赖与框架原则

v0.1 保持简单、可测试、可替换。

除非任务明确要求，否则不要引入重型依赖。

优先原则：

- 开发语言采用 Python 3.14；
- 后端框架采用 FastAPI；
- 环境管理采用 uv；
- 如果用到数据库，优先采用 SQLite；
- 配置通过 Settings 管理；
- 日志使用统一 logger；
- Agent 框架根据任务复杂度评估后再决定，默认不引入复杂 Agent 框架；
- 敏感信息必须通过环境变量或配置隔离，不得硬编码。

避免引入：

- LangChain；
- LangGraph；
- CrewAI；
- 向量数据库；
- 任务队列；
- 复杂工作流引擎；
- 不必要的 ORM；
- 复杂前端框架。

优先使用小而清晰的 Python 后端结构。

---

## 命名规则

项目名称统一使用：

**mingmax**

禁止再使用旧名称：

- MindMind
- MINDmind
- mindmind

除非是在历史迁移说明中。

---

## 禁止事项

- ❌ 不要使用 `pip install`，一切依赖通过 `uv add` 管理。
- ❌ 不要在路由函数中写业务逻辑。
- ❌ 不要使用 Python 3.13 以下的新语法特性。
- ❌ 不要硬编码配置值，端口号、地址、模型名、路径等一律走 `Settings`。
- ❌ 不要使用全局变量存储请求级别的数据。
- ❌ 不要创建全局 service 单例。
- ❌ 不要在单元测试中真实调用外部 LLM API。
- ❌ 不要生成无意义注释。
- ❌ 不要让 LLM 直接推算命盘。
- ❌ 不要在业务代码中散落 Prompt 字符串。
- ❌ 不要引入超出 v0.1 范围的大型框架或复杂基础设施。