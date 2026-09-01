from pathlib import Path

from backend.app.agent import AgentService
from backend.app.assistant import AssistantService
from backend.app.config import Settings, get_settings
from backend.app.llm import FallbackLLMClient, LLMResult, MockLLMClient, build_llm_client
from backend.app.models import AgentRequest, AssistantRequest
from backend.app.rag import KnowledgeBase
from backend.app.router import route_request


class DirectAnswerLLM:
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResult:
        return LLMResult(
            text="```python\ndef solution():\n    return 2\n```",
            provider="fake-direct-answer",
            model="fake-model",
            used_real_api=True,
        )


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


def test_deepseek_is_default_provider(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")

    settings = get_settings()

    assert settings.llm_provider == "deepseek"
    assert settings.effective_llm_api_key == "sk-test"
    assert settings.effective_llm_base_url == "https://api.deepseek.com"
    assert settings.effective_llm_model == "deepseek-v4-flash"


def test_deepseek_client_uses_mock_fallback_without_key():
    settings = Settings(
        llm_provider="deepseek",
        deepseek_api_key=None,
        openai_api_key=None,
        allow_mock_when_no_key=True,
    )
    client = build_llm_client(settings)

    result = client.generate("system", "请生成练习题")

    assert result.provider == "mock"
    assert result.used_real_api is False


def test_deepseek_client_configuration_uses_v4_flash():
    settings = Settings(
        llm_provider="deepseek",
        deepseek_api_key="sk-test",
        allow_mock_when_no_key=False,
    )
    client = build_llm_client(settings)

    assert isinstance(client, FallbackLLMClient)
    assert client.primary.provider == "deepseek"
    assert client.primary.base_url == "https://api.deepseek.com"
    assert client.primary.model == "deepseek-v4-flash"
    assert client.primary.extra_payload["thinking"]["type"] == "disabled"


def test_assistant_runs_socratic_chat_chain(tmp_path: Path):
    service = AssistantService(llm_client=MockLLMClient(), assistant_log_path=tmp_path / "assistant.jsonl")

    response = service.chat(
        AssistantRequest(
            message="我觉得 left 直接等于 seen[ch] + 1 就可以",
            diagnosis_context="abba 用例失败，薄弱知识点为滑动窗口左边界。",
        )
    )

    assert response.answer
    assert "？" in response.answer or "?" in response.answer
    assert response.retrieved_documents
    assert response.evaluation_record["assistant_success"] is True
    assert (tmp_path / "assistant.jsonl").exists()


def test_assistant_blocks_direct_code_answer(tmp_path: Path):
    service = AssistantService(llm_client=DirectAnswerLLM(), assistant_log_path=tmp_path / "assistant.jsonl")

    response = service.chat(
        AssistantRequest(
            message="直接给我完整代码",
            diagnosis_context="学生连续在 abba 上失败。",
        )
    )

    assert "```" not in response.answer
    assert response.evaluation_record["direct_answer_blocked"] is True
    assert response.evaluation_record["assistant_success"] is True
