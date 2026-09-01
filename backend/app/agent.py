from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from .config import Settings, get_settings
from .llm import LLMClientProtocol, build_llm_client
from .models import AgentRequest, AgentResponse
from .rag import KnowledgeBase
from .router import route_request
from .tools import TOOLS


class AgentService:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        llm_client: Optional[LLMClientProtocol] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        run_log_path: Optional[Path] = None,
    ):
        self.settings = settings or get_settings()
        self.knowledge_base = knowledge_base or KnowledgeBase(self.settings.knowledge_base_path)
        self.llm_client = llm_client or build_llm_client(self.settings)
        self.run_log_path = run_log_path or self.settings.run_log_path

    def run(self, request: AgentRequest) -> AgentResponse:
        run_id = str(uuid.uuid4())
        route = route_request(request.teacher_request)
        query = f"{request.teacher_request} {request.class_profile or ''}"
        retrieved = self.knowledge_base.search(query, top_k=request.top_k)
        llm_result = self.llm_client.generate(
            system_prompt=self._system_prompt(route.task_type),
            user_prompt=self._user_prompt(request, route.task_type, retrieved),
        )

        tool = TOOLS[route.tool_name]
        output = tool.build(request.teacher_request, retrieved, llm_result.text)
        evaluation_record = {
            "run_id": run_id,
            "timestamp": int(time.time()),
            "task_type": route.task_type,
            "tool_name": tool.name,
            "route_confidence": route.confidence,
            "retrieved_doc_ids": [doc.id for doc in retrieved],
            "retrieval_top_score": retrieved[0].score if retrieved else 0,
            "llm_used": llm_result.used_real_api,
            "llm_provider": llm_result.provider,
            "output_type": output.get("type"),
            "tool_success": bool(output.get("type") and output.get("rag_sources")),
        }
        self._record_run({"request": request.model_dump(), "evaluation": evaluation_record})

        return AgentResponse(
            run_id=run_id,
            route=route,
            retrieved_documents=retrieved,
            llm_provider=llm_result.provider,
            llm_model=llm_result.model,
            llm_used=llm_result.used_real_api,
            tool_name=tool.name,
            output=output,
            evaluation_record=evaluation_record,
        )

    @staticmethod
    def _system_prompt(task_type: str) -> str:
        return (
            "你是 Python 编程 ITS 系统里的教师 Agent。你需要根据教师需求、本地知识库材料和学生画像，"
            "生成可执行、可诊断、可评估的教学输出。不要直接替学生完成最终代码，要强调引导、测试和诊断。"
            f"当前任务类型是 {task_type}。"
        )

    @staticmethod
    def _user_prompt(request: AgentRequest, task_type: str, docs: list[Any]) -> str:
        evidence = "\n".join(
            f"- [{doc.id}] {doc.title}: {doc.content}" for doc in docs
        )
        return (
            f"任务类型: {task_type}\n"
            f"教师需求: {request.teacher_request}\n"
            f"班级画像: {request.class_profile}\n"
            f"本地知识库检索结果:\n{evidence}\n"
            "请先给出教学思路，再指出需要生成的结构化产物。"
        )

    def _record_run(self, payload: dict[str, Any]) -> None:
        self.run_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.run_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def read_records(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.run_log_path.exists():
            return []
        lines = self.run_log_path.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines[-limit:] if line.strip()]
        return records
