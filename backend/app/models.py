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


class AssistantMessage(BaseModel):
    role: Literal["student", "assistant"]
    content: str = Field(..., min_length=1, max_length=1200)


class AssistantRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1200, description="学生当前输入的问题或想法")
    student_id: str = Field(default="student-demo", description="学生标识")
    problem_title: str = Field(default="最长无重复子串", description="当前练习题标题")
    problem_context: Optional[str] = Field(
        default="给定字符串 s，返回其中不含重复字符的最长子串长度。",
        description="当前题目或任务描述",
    )
    diagnosis_context: Optional[str] = Field(
        default="诊断模型提示：abba 用例暴露滑动窗口 left 回退风险，薄弱知识点为滑动窗口左边界。",
        description="诊断模型输出的错误类型、薄弱点或提示建议",
    )
    student_profile: Optional[str] = Field(
        default="学生有 Python 基础，准备做项目/算法题；当前提示依赖为中等。",
        description="学生模型中的能力、掌握度和学习习惯摘要",
    )
    assistant_policy: Optional[str] = Field(
        default="不直接给完整代码，不直接给最终答案；先提问，再给一个关键线索；连续失败后才允许给伪代码框架。",
        description="教师端配置的小助手人设和答案边界",
    )
    conversation: list[AssistantMessage] = Field(default_factory=list, description="近期对话历史")
    top_k: int = Field(default=4, ge=1, le=8, description="RAG 检索返回条数")


class AssistantResponse(BaseModel):
    response_id: str
    answer: str
    retrieved_documents: list[RetrievedDocument]
    llm_provider: str
    llm_model: str
    llm_used: bool
    safety_policy: list[str]
    evaluation_record: dict[str, Any]
