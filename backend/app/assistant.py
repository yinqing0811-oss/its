from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from .config import Settings, get_settings
from .llm import LLMClientProtocol, build_llm_client
from .models import AssistantRequest, AssistantResponse
from .rag import KnowledgeBase


DIRECT_SOLUTION_MARKERS = ("```", "代码如下", "完整代码如下", "最终答案是", "直接答案")


class AssistantService:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        llm_client: Optional[LLMClientProtocol] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        assistant_log_path: Optional[Path] = None,
    ):
        self.settings = settings or get_settings()
        self.knowledge_base = knowledge_base or KnowledgeBase(self.settings.knowledge_base_path)
        self.llm_client = llm_client or build_llm_client(self.settings)
        self.assistant_log_path = assistant_log_path or self.settings.assistant_log_path

    def chat(self, request: AssistantRequest) -> AssistantResponse:
        response_id = str(uuid.uuid4())
        query = " ".join(
            part
            for part in [
                request.message,
                request.problem_title,
                request.problem_context or "",
                request.diagnosis_context or "",
                request.student_profile or "",
            ]
            if part
        )
        retrieved = self.knowledge_base.search(query, top_k=request.top_k)
        llm_result = self.llm_client.generate(
            system_prompt=self._system_prompt(request),
            user_prompt=self._user_prompt(request, retrieved),
        )

        raw_answer = self._mock_answer(request, retrieved) if llm_result.provider == "mock" else llm_result.text
        answer, direct_answer_blocked = self._enforce_socratic_boundary(raw_answer, request, retrieved)
        evaluation_record = {
            "response_id": response_id,
            "timestamp": int(time.time()),
            "student_id": request.student_id,
            "retrieved_doc_ids": [doc.id for doc in retrieved],
            "retrieval_top_score": retrieved[0].score if retrieved else 0,
            "llm_used": llm_result.used_real_api,
            "llm_provider": llm_result.provider,
            "socratic_question_count": answer.count("?") + answer.count("？"),
            "direct_answer_blocked": direct_answer_blocked,
            "assistant_success": bool(answer.strip()) and "```" not in answer,
        }
        self._record_chat({"request": request.model_dump(), "evaluation": evaluation_record, "answer": answer})

        return AssistantResponse(
            response_id=response_id,
            answer=answer,
            retrieved_documents=retrieved,
            llm_provider=llm_result.provider,
            llm_model=llm_result.model,
            llm_used=llm_result.used_real_api,
            safety_policy=[
                "不直接给完整代码",
                "不直接给最终答案",
                "优先追问学生思路",
                "结合诊断模型与本地知识库",
            ],
            evaluation_record=evaluation_record,
        )

    @staticmethod
    def _system_prompt(request: AssistantRequest) -> str:
        return (
            "你是 Python ITS 系统中的苏格拉底式智能小助手，服务对象是有一点 Python 基础、"
            "正在准备项目和算法题的学生。你的目标是引导学生自己发现问题，而不是替学生完成答案。"
            "必须遵守：不直接给完整代码；不直接给最终答案；每次最多提示一个关键点；"
            "优先使用追问、反例、测试用例和变量状态跟踪；回答控制在 180 字以内。"
            f"教师配置的人设与边界：{request.assistant_policy}"
        )

    @staticmethod
    def _user_prompt(request: AssistantRequest, docs: list[Any]) -> str:
        evidence = "\n".join(f"- [{doc.id}] {doc.title}: {doc.content}" for doc in docs)
        history = "\n".join(
            f"{message.role}: {message.content}" for message in request.conversation[-6:]
        )
        return (
            f"学生问题: {request.message}\n"
            f"当前题目: {request.problem_title}\n"
            f"题目背景: {request.problem_context}\n"
            f"诊断上下文: {request.diagnosis_context}\n"
            f"学生画像: {request.student_profile}\n"
            f"近期对话:\n{history or '暂无'}\n"
            f"本地知识库检索结果:\n{evidence}\n"
            "请只输出给学生看的下一轮引导，不要输出完整代码或最终答案。"
        )

    @staticmethod
    def _mock_answer(request: AssistantRequest, docs: list[Any]) -> str:
        focus = docs[0].tags[0] if docs and docs[0].tags else "当前薄弱点"
        return (
            f"我先不直接给答案。我们围绕“{focus}”看一个小问题："
            "你能用当前这组输入说出关键变量每一步应该保持什么不变量吗？"
        )

    @staticmethod
    def _enforce_socratic_boundary(
        answer: str,
        request: AssistantRequest,
        docs: list[Any],
    ) -> tuple[str, bool]:
        clean_answer = answer.strip()
        direct_answer_blocked = any(marker in clean_answer for marker in DIRECT_SOLUTION_MARKERS)

        if not clean_answer or direct_answer_blocked:
            focus = docs[0].tags[0] if docs and docs[0].tags else request.problem_title
            clean_answer = (
                "我先不直接给完整代码。"
                f"围绕“{focus}”，你能先说出当前状态应该满足什么条件吗？"
                "再用一个会失败的测试用例验证你的判断。"
            )

        if len(clean_answer) > 500:
            clean_answer = clean_answer[:497].rstrip() + "..."

        if "?" not in clean_answer and "？" not in clean_answer:
            clean_answer = f"{clean_answer} 你能先用一个具体测试用例解释自己的判断吗？"

        return clean_answer, direct_answer_blocked

    def _record_chat(self, payload: dict[str, Any]) -> None:
        self.assistant_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.assistant_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
