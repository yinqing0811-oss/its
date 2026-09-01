from pathlib import Path

from backend.app.agent import AgentService
from backend.app.config import get_settings
from backend.app.llm import MockLLMClient
from backend.app.models import AgentRequest
from backend.app.rag import KnowledgeBase
from backend.app.router import route_request


def test_router_identifies_lesson_plan():
    decision = route_request("为 Python A 班设计 15 分钟滑动窗口补弱课")

    assert decision.task_type == "lesson_plan"
    assert decision.tool_name == "lesson_planner"
    assert decision.confidence > 0.6


def test_router_identifies_exercise_generation():
    decision = route_request("生成 6 道哈希表练习题，按 A/B/C 三档分层")

    assert decision.task_type == "exercise_generation"
    assert decision.tool_name == "exercise_generator"
    assert decision.confidence > 0.6


def test_knowledge_base_retrieves_relevant_documents():
    kb = KnowledgeBase(get_settings().knowledge_base_path)
    results = kb.search("滑动窗口 abba left 不能回退", top_k=3)

    assert results
    assert results[0].id == "kb001"


def test_agent_runs_full_lesson_chain(tmp_path: Path):
    service = AgentService(llm_client=MockLLMClient(), run_log_path=tmp_path / "runs.jsonl")

    response = service.run(
        AgentRequest(
            teacher_request="设计一节滑动窗口补弱课，讲清楚 abba 的边界错误",
            class_profile="学生已经会字典，但边界条件薄弱。",
        )
    )

    assert response.route.task_type == "lesson_plan"
    assert response.output["type"] == "structured_lesson_plan"
    assert response.output["lesson_flow"]
    assert response.evaluation_record["tool_success"] is True
    assert (tmp_path / "runs.jsonl").exists()


def test_agent_runs_full_exercise_chain(tmp_path: Path):
    service = AgentService(llm_client=MockLLMClient(), run_log_path=tmp_path / "runs.jsonl")

    response = service.run(
        AgentRequest(
            teacher_request="生成 4 道复杂度分析练习题，覆盖双重循环超时",
            class_profile="学生准备刷算法题。",
        )
    )

    assert response.route.task_type == "exercise_generation"
    assert response.output["type"] == "exercise_set"
    assert len(response.output["exercises"]) == 3
    assert response.evaluation_record["tool_success"] is True
