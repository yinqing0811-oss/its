from __future__ import annotations

from typing import Any

from .models import RetrievedDocument


def _unique_tags(docs: list[RetrievedDocument], limit: int = 6) -> list[str]:
    tags: list[str] = []
    for doc in docs:
        for tag in doc.tags:
            if tag not in tags:
                tags.append(tag)
    return tags[:limit]


class LessonPlanTool:
    name = "lesson_planner"

    def build(self, teacher_request: str, docs: list[RetrievedDocument], llm_text: str) -> dict[str, Any]:
        tags = _unique_tags(docs)
        focus = tags[:4] or ["Python 基础", "问题拆解", "代码诊断"]
        return {
            "type": "structured_lesson_plan",
            "title": f"Python 教学方案：{teacher_request[:32]}",
            "target_learners": "有一定 Python 基础，准备做项目/算法题的学生",
            "knowledge_focus": focus,
            "duration_minutes": 15 if "15" in teacher_request else 40,
            "objectives": [
                f"学生能说清 {focus[0]} 的核心概念",
                "学生能用测试用例解释代码行为",
                "学生能根据诊断反馈修正一个常见错误",
            ],
            "lesson_flow": [
                {"stage": "诊断导入", "minutes": 3, "activity": "展示最近提交中的典型失败用例，要求学生先预测输出。"},
                {"stage": "概念讲解", "minutes": 5, "activity": "结合本地知识库材料讲解关键概念、边界条件和常见误区。"},
                {"stage": "示范拆解", "minutes": 5, "activity": "教师用一段短代码演示状态变量如何变化，并标出诊断点。"},
                {"stage": "即时练习", "minutes": 10, "activity": "学生完成一题同构练习，系统记录测试通过数和错误类型。"},
                {"stage": "复盘迁移", "minutes": 5, "activity": "根据学生模型输出复习点和下一题推荐。"},
            ],
            "assessment": {
                "observable_metrics": ["任务路由正确", "测试用例通过率", "错误类型减少", "提示依赖下降"],
                "exit_ticket": "请学生写出一个能暴露边界错误的测试用例，并说明原因。",
            },
            "rag_sources": [{"id": doc.id, "title": doc.title, "score": doc.score} for doc in docs],
            "llm_draft": llm_text,
        }


class ExerciseGenerationTool:
    name = "exercise_generator"

    def build(self, teacher_request: str, docs: list[RetrievedDocument], llm_text: str) -> dict[str, Any]:
        tags = _unique_tags(docs)
        focus = tags[:4] or ["Python", "算法题", "测试用例"]
        return {
            "type": "exercise_set",
            "title": f"Python 练习题包：{teacher_request[:32]}",
            "difficulty_policy": "A/B/C 三档分层，先诊断基础，再暴露边界，最后迁移到项目任务。",
            "knowledge_focus": focus,
            "exercises": [
                {
                    "level": "A",
                    "title": f"{focus[0]} 概念确认题",
                    "prompt": "阅读一段短代码，写出关键变量每一步的变化，并说明最终输出。",
                    "diagnosis_focus": ["概念理解", "状态跟踪"],
                    "test_cases": ["常规输入", "空输入"],
                },
                {
                    "level": "B",
                    "title": f"{focus[0]} 边界处理编程题",
                    "prompt": "实现一个函数，并至少补充 2 个能暴露边界错误的自定义测试用例。",
                    "diagnosis_focus": ["边界条件", "隐藏用例"],
                    "test_cases": ["重复值", "最小规模", "极端位置"],
                },
                {
                    "level": "C",
                    "title": "项目化迁移小任务",
                    "prompt": "把算法封装成可复用函数，输出结构化结果，并写出复杂度分析。",
                    "diagnosis_focus": ["模块化", "复杂度分析", "代码质量"],
                    "test_cases": ["多组输入", "异常输入", "性能输入"],
                },
            ],
            "rubric": [
                "是否覆盖 Q 矩阵标注知识点",
                "是否包含固定、边界和隐藏测试",
                "是否能让诊断模型识别错误类型",
            ],
            "rag_sources": [{"id": doc.id, "title": doc.title, "score": doc.score} for doc in docs],
            "llm_draft": llm_text,
        }


TOOLS = {
    LessonPlanTool.name: LessonPlanTool(),
    ExerciseGenerationTool.name: ExerciseGenerationTool(),
}
