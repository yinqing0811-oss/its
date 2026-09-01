from __future__ import annotations

from .models import RouteDecision


LESSON_KEYWORDS = {
    "教案": 2.5,
    "教学方案": 2.5,
    "课堂": 2.0,
    "课程": 1.8,
    "讲解": 1.8,
    "补弱课": 2.5,
    "复习课": 2.2,
    "项目课": 2.2,
    "教学设计": 2.5,
    "教学流程": 2.2,
    "讲评课": 3.0,
    "培训课": 2.6,
    "学习路径": 2.4,
    "第一节课": 2.4,
    "流程": 1.2,
    "15分钟": 1.0,
    "分钟": 0.8,
}

EXERCISE_KEYWORDS = {
    "练习题": 2.8,
    "题目": 2.2,
    "出题": 2.5,
    "题单": 2.4,
    "作业": 2.0,
    "测试": 1.8,
    "测验": 2.0,
    "练习": 1.8,
    "用例": 1.8,
    "选择题": 2.0,
    "编程题": 2.2,
    "分层练习": 2.5,
}


def _score(text: str, keywords: dict[str, float]) -> float:
    lowered = text.lower()
    return sum(weight for keyword, weight in keywords.items() if keyword.lower() in lowered)


def route_request(teacher_request: str) -> RouteDecision:
    """Route a teacher request to the smallest useful tool.

    The router is intentionally explainable. It can later be replaced by a
    classifier, but the first MVP should let teachers and developers understand
    why a task went to a given tool.
    """

    lesson_score = _score(teacher_request, LESSON_KEYWORDS)
    exercise_score = _score(teacher_request, EXERCISE_KEYWORDS)

    if exercise_score > lesson_score:
        confidence = min(0.96, 0.58 + (exercise_score - lesson_score) * 0.08)
        return RouteDecision(
            task_type="exercise_generation",
            tool_name="exercise_generator",
            confidence=round(confidence, 2),
            reason="需求中出现练习、题目、作业或测试用例信号，优先路由到练习题生成工具。",
        )

    confidence = min(0.96, 0.62 + max(lesson_score - exercise_score, 0) * 0.07)
    if lesson_score == 0 and exercise_score == 0:
        confidence = 0.55

    return RouteDecision(
        task_type="lesson_plan",
        tool_name="lesson_planner",
        confidence=round(confidence, 2),
        reason="需求更接近课堂组织、讲解流程或补弱教学，路由到结构化教案生成工具。",
    )
