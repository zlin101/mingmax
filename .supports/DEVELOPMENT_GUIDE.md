# DEVELOPMENT_GUIDE.md

## 开发前阅读

任何非琐碎开发任务开始前，必须阅读：

- `AGENTS.md`
- `.supports/PROJECT_CONTEXT.md`
- `.supports/DECISIONS.md`
- `.supports/ARCHITECTURE.md`
- `.supports/TASKS.md`

涉及 Prompt、API、测试或开发命令时，还应阅读：

- `.supports/PROMPT_GUIDE.md`
- `.supports/API_SPEC.md`
- `.supports/DEVELOPMENT_GUIDE.md`

## 包管理

所有依赖管理使用 uv：

```bash
uv add <package>
uv add --dev <package>
uv sync
uv run <command>
uv lock
```

禁止在代码、README 或文档中写 `pip install`。

## 分支规则

每次开发任务下达后，Codex 负责先在 `.supports/TASKS.md` 写明建议新建分支和分支名称。Claude 开发前必须确认分支计划，并在对应分支上开发和测试。

分支命名建议：

```text
feature/<version>-<scope>
fix/<version>-<scope>
docs/<version>-<scope>
chore/<version>-<scope>
```

示例：

```text
docs/v0.1-context-and-plan
feature/v0.1-project-foundation
feature/v0.1-chart-core
feature/v0.1-analysis-flow
```

分支计划至少包含：

- 任务名称；
- 建议分支名；
- 分支用途；
- 分支起点；
- 交付后验收人。

## Commit 与 Push 规则

每个分支只服务一个明确任务范围。不要把多个阶段的工作混在同一个分支里。

Commit 规则：

- 每个分支至少包含一个 commit。
- 复杂分支按可验收子任务拆成多个 commit。
- commit 前必须完成该 commit 相关的本地测试、格式化或静态检查。
- 不把格式化、依赖升级、业务逻辑、文档大改混在同一个 commit，除非它们是同一任务的必要组成。
- commit message 使用 Conventional Commits。

Commit message 示例：

```text
docs: add v0.1 planning docs
chore: configure project tooling
feat: add birth info schemas
feat: add chart engine stub
test: cover chart normalization
fix: handle invalid birth timezone
```

Push 规则：

- 分支开发完成、自测通过、相关 `.supports/` 文档更新后再 push。
- push 后由 Claude 提供分支名、commit 列表、测试命令和结果、未完成事项或风险。
- Codex 基于 Claude 提供的信息进行 code review 和验收，不主动参与测试执行。
- Claude 不得自行 merge。
- Codex 不得自行 merge。
- merge 只由项目负责人执行。

依赖锁文件规则：

- 使用 uv 变更依赖后，必须提交 `pyproject.toml` 和 `uv.lock`。
- 新增依赖必须说明用途和必要性。
- 不得引入超出 v0.1 范围的重型依赖。

配置与环境变量规则：

- 真实密钥、真实 `.env`、本机私有配置不得提交。
- 如新增环境变量，必须同步更新 `.env.example`。
- 配置项必须通过 `Settings` 管理，不得在业务代码中硬编码。
- 环境变量命名使用大写蛇形命名，例如 `MINGMAX_LLM_MODEL`。

CI / pre-commit 规则：

- 第一阶段至少保留可本地执行的检查命令：`uv run black .`、`uv run isort .`、`uv run flake8 .`、`uv run pytest`。
- 如配置 pre-commit 或 CI，必须使用 uv 运行命令。
- gitlint 或 commit 校验若启用，必须兼容 Conventional Commits。

## 建议命令

安装开发依赖：

```bash
uv add fastapi pydantic pydantic-settings
uv add --dev pytest pytest-asyncio pytest-cov httpx black isort flake8
```

运行格式化和检查：

```bash
uv run black .
uv run isort .
uv run flake8 .
```

运行测试：

```bash
uv run pytest
uv run pytest --cov=app
```

## 代码规范

- Python >=3.14。
- 行宽上限 120 字符。
- 所有函数参数和返回值必须有类型注解。
- IO 操作优先使用 `async/await`。
- FastAPI 依赖通过 `Depends` 注入。
- 配置通过 `Settings` 管理，不硬编码端口、地址、模型名、API Key 或路径。
- 使用统一 logger，不使用 `print` 输出运行日志。
- 默认不写注释或 docstring，除非紫微规则、历法边界或第三方库行为确实需要说明。

## 测试规范

Claude 负责开发和测试执行。Codex 负责 code review 和验收，不参与测试执行。

测试要求：

- 测试文件放在 `tests/`。
- 文件命名为 `test_<模块名>.py`。
- 公共 fixture 放在 `tests/conftest.py`。
- 外部 LLM API 必须 mock。
- 单元测试不得依赖开发者本机环境变量。
- API 测试优先使用 `httpx.AsyncClient` 和 `ASGITransport`。
- 确定性逻辑必须测试。

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

## 本地私密样本验证

使用 `scripts/verify_private_chart_sample.py` 对本地私密验证文件做排盘准确性对比：

```bash
uv run python scripts/verify_private_chart_sample.py .supports/TEST_INFO_EVA.md
```

隐私要求：

- `.supports/TEST_INFO_EVA.md` 必须保持未跟踪，不得 `git add`（已在 `.gitignore` 中）。
- 输出只允许脱敏差异统计，不得包含真实出生日期、地点、经度、完整宫位文本或任何可识别信息。
- 自动化测试只使用合成 fixture，不使用私密样本。

## 端到端私密样本验证

使用 `scripts/verify_e2e_real_sample.py` 对本地私密验证文件做完整链路验证（排盘 + chart_facts + LLM 输出 + 证据一致性检查）：

```bash
# 使用 mock LLM（不调用外部模型）
uv run python scripts/verify_e2e_real_sample.py .supports/TEST_INFO_EVA.md --mock-llm

# 使用真实 LLM（需要本机配置 MINGMAX_LLM_PROVIDER=openai_compatible 等）
MINGMAX_LLM_PROVIDER=openai_compatible \
uv run python scripts/verify_e2e_real_sample.py .supports/TEST_INFO_EVA.md
```

隐私要求同上。验证输出为脱敏 JSON，包含 chart 来源、宫位数量、LLM 模式和证据一致性 issue 统计，不包含真实出生信息。

## Code Review 验收口径

Codex review 时优先检查：

- 是否有跨层调用；
- 是否让 LLM 参与确定性排盘；
- 是否绕过统一 LLM 抽象；
- Prompt 是否散落在业务逻辑中；
- 是否缺少确定性逻辑测试；
- 是否真实调用外部 LLM API；
- 是否引入超出 v0.1 范围的依赖；
- Markdown 报告是否包含免责声明；
- `.supports/` 文档是否随架构、API、Schema、Prompt 或测试策略变化同步更新。

Codex review 输出格式：

```text
Blockers:
- 阻塞合并的问题；没有则写 None。

Required Changes:
- 必须修改但不一定阻塞讨论的问题；没有则写 None。

Notes:
- 非阻塞建议、后续风险或观察；没有则写 None。

Verdict:
- Approved / Changes requested / Needs owner decision
```
