# ITS Python 智能教学系统 v1.5 DeepSeek Agent MVP

这是一个面向 Python 编程学习的 ITS（Intelligent Tutoring System，智能教学系统）最小可运行 Agent 项目。它在原 v1.3 前端原型基础上，新增了 FastAPI 后端、DeepSeek API 接入、本地教学知识库 RAG、任务路由、工具调用和自动评估报告。

## 已实现链路

```text
教师输入教学需求
        ↓
Agent 识别任务类型
        ↓
检索本地教学知识库
        ↓
调用大模型生成教学方案
        ↓
调用工具生成练习题或结构化教案
        ↓
输出结果并记录评估数据
```

## 功能范围

- 前端页面：学生/教师身份入口、教师工作台、学生模型、教学模型、领域模型、练习发放、在线编程与诊断、智能小助手。
- 后端服务：基于 FastAPI 的 Agent API。
- 任务路由：识别 `lesson_plan` 和 `exercise_generation` 两类任务。
- 本地 RAG：`backend/app/data/knowledge_base.jsonl` 中包含 30 条 Python 教学知识。
- 工具调用：内置 `lesson_planner` 和 `exercise_generator` 两个工具。
- 大模型 API：默认接入 DeepSeek Chat Completions API，同时保留 OpenAI-compatible 配置。
- 自动评估：25 条测试数据，输出路由准确率、工具调用成功率和生成质量粗评分。

## 环境准备

建议使用 Python 3.10+。Python 3.9 也可运行，当前项目已做兼容。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 配置 DeepSeek API

复制环境变量样例：

```bash
cp .env.example .env
```

然后在 `.env` 中填写：

```text
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_THINKING=disabled
DEEPSEEK_REASONING_EFFORT=high
LLM_PROVIDER=deepseek
```

如果没有配置 `DEEPSEEK_API_KEY`，系统会进入本地 mock 演示模式，方便跑通页面和评估；配置 key 后，后端会真实调用 DeepSeek API。

模型建议：

- `deepseek-v4-flash`：默认推荐，适合课堂教案、练习题和学生小助手高频对话。
- `deepseek-v4-pro`：适合更复杂的代码诊断、项目方案设计或需要更强推理的场景。

说明：截至 2026-09-01，DeepSeek 官方推荐使用 `deepseek-v4-flash` 或 `deepseek-v4-pro`。旧模型名 `deepseek-chat`、`deepseek-reasoner` 已在 2026-07-24 后停止作为推荐接入口。

可选：如果要切回其它 OpenAI-compatible 服务，可以把 `LLM_PROVIDER` 改成 `openai`，并填写 `OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_BASE_URL`。

## 启动后端

```bash
uvicorn backend.app.main:app --reload --port 8000 --env-file .env
```

也可以不使用 `.env`，直接在 shell 中设置环境变量后运行：

```bash
uvicorn backend.app.main:app --reload --port 8000
```

健康检查：

```text
http://localhost:8000/api/health
```

## 启动前端

另开一个终端：

```bash
python -m http.server 5174
```

然后访问：

```text
http://localhost:5174/
```

进入教师端后，在首页输入教学需求，例如：

```text
生成 Python A 班 15 分钟滑动窗口补弱课
```

点击箭头即可调用后端 Agent。

## API 示例

```bash
curl -X POST http://localhost:8000/api/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_request": "生成 6 道哈希表练习题，按 A/B/C 三档分层",
    "class_profile": "Python A 班，学生有基础，准备做算法题。",
    "top_k": 4
  }'
```

## 自动评估

运行：

```bash
LLM_PROVIDER=mock python backend/run_evaluation.py
```

输出文件：

- `reports/evaluation_report.md`
- `reports/evaluation_results.json`

当前评估结果：

- 测试样本数：25
- 任务路由准确率：100.00%
- 工具调用成功率：100.00%
- 平均生成质量分：99.20 / 100

## 目录结构

```text
backend/
  app/
    agent.py          # Agent 编排链路
    main.py           # FastAPI 入口
    router.py         # 任务路由
    rag.py            # 本地知识库检索
    llm.py            # DeepSeek API / OpenAI-compatible / mock 客户端
    tools.py          # 教案生成、练习题生成工具
    evaluation.py     # 自动评估逻辑
    data/
      knowledge_base.jsonl
      evaluation_cases.json
tests/
reports/
index.html
script.js
styles.css
```

## 测试

```bash
pytest -q
```

当前单元测试：

```text
5 passed
```

## 说明

当前版本是 Agent MVP，已经具备真实链路和工程结构，但 Python 在线判题沙箱仍是前端演示逻辑。下一阶段建议增加数据库、真实代码执行沙箱、用户鉴权和教师人工评分闭环。
