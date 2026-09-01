from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


TaskType = Literal["lesson_plan", "exercise_generation"]


class AgentRequest(BaseModel):
    teacher_request: str = Field(..., min_length=2, description="教师输入的自然语言教学需求")
    class_profile: Optional[str] = Field(
        default="Python A 班，学生有基础，准备做项目/算法题，近期薄弱点集中在边界条件和复杂度分析。",
        description="班级或学生画像补充信息",
    )
    top_k: int = Field(default=4, ge=1, le=8, description="RAG 检索返回条数")


class RouteDecision(BaseModel):
    task_type: TaskType
    tool_name: str
    confidence: float
    reason: str


class RetrievedDocument(BaseModel):
    id: str
    title: str
    tags: list[str]
    content: str
    score: float


class AgentResponse(BaseModel):
    run_id: str
    route: RouteDecision
    retrieved_documents: list[RetrievedDocument]
    llm_provider: str
    llm_model: str
    llm_used: bool
    tool_name: str
    output: dict[str, Any]
    evaluation_record: dict[str, Any]


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[RetrievedDocument]
