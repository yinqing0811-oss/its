from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any, Optional

from .agent import AgentService
from .config import REPORTS_DIR, get_settings
from .llm import MockLLMClient
from .models import AgentRequest


def _contains_keyword(payload: dict[str, Any], keyword: str) -> bool:
    return keyword.lower() in json.dumps(payload, ensure_ascii=False).lower()


def _quality_score(output: dict[str, Any], expected_keywords: list[str]) -> float:
    required_score = 0
    if output.get("rag_sources"):
        required_score += 20
    if output.get("knowledge_focus"):
        required_score += 20
    if output.get("type") == "structured_lesson_plan" and output.get("lesson_flow"):
        required_score += 30
    if output.get("type") == "exercise_set" and output.get("exercises"):
        required_score += 30
    keyword_hits = sum(1 for keyword in expected_keywords if _contains_keyword(output, keyword))
    keyword_score = 30 * keyword_hits / max(len(expected_keywords), 1)
    return round(min(100, required_score + keyword_score), 1)


def evaluate(output_dir: Optional[Path] = None) -> dict[str, Any]:
    settings = get_settings()
    cases = json.loads(settings.evaluation_cases_path.read_text(encoding="utf-8"))
    service = AgentService(settings=settings, llm_client=MockLLMClient())

    rows = []
    for case in cases:
        response = service.run(
            AgentRequest(
                teacher_request=case["teacher_request"],
                class_profile="评估模式：使用固定学生画像，不调用真实大模型。",
                top_k=4,
            )
        )
        route_ok = response.route.task_type == case["expected_task_type"]
        tool_ok = response.tool_name == case["expected_tool"] and response.evaluation_record["tool_success"]
        quality = _quality_score(response.output, case["expected_keywords"])
        rows.append(
            {
                "id": case["id"],
                "request": case["teacher_request"],
                "expected_task_type": case["expected_task_type"],
                "predicted_task_type": response.route.task_type,
                "expected_tool": case["expected_tool"],
                "actual_tool": response.tool_name,
                "route_ok": route_ok,
                "tool_ok": tool_ok,
                "quality_score": quality,
                "retrieved_doc_ids": response.evaluation_record["retrieved_doc_ids"],
            }
        )

    total = len(rows)
    summary = {
        "total_cases": total,
        "route_accuracy": round(sum(row["route_ok"] for row in rows) / total, 4),
        "tool_success_rate": round(sum(row["tool_ok"] for row in rows) / total, 4),
        "average_quality_score": round(mean(row["quality_score"] for row in rows), 2),
        "cases": rows,
    }

    report_dir = output_dir or REPORTS_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "evaluation_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (report_dir / "evaluation_report.md").write_text(_render_markdown(summary), encoding="utf-8")
    return summary


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# ITS Agent MVP 测试报告",
        "",
        "## 评估目标",
        "",
        "本报告使用 25 条人工标注测试数据，评估最小可运行 Agent 链路中的任务路由准确率、工具调用成功率和生成质量粗评分。",
        "",
        "评估运行使用 `MockLLMClient` 固定输出，目的是稳定检测路由、RAG、工具调用和结构化输出。生产运行时配置 `OPENAI_API_KEY` 后会调用真实大模型 API。",
        "",
        "## 指标汇总",
        "",
        f"- 测试样本数：{summary['total_cases']}",
        f"- 任务路由准确率：{summary['route_accuracy']:.2%}",
        f"- 工具调用成功率：{summary['tool_success_rate']:.2%}",
        f"- 平均生成质量分：{summary['average_quality_score']:.2f} / 100",
        "",
        "## 明细",
        "",
        "| ID | 期望类型 | 预测类型 | 工具 | 路由正确 | 工具成功 | 质量分 | 检索文档 |",
        "|---|---|---|---|---|---|---:|---|",
    ]
    for row in summary["cases"]:
        lines.append(
            "| {id} | {expected_task_type} | {predicted_task_type} | {actual_tool} | {route_ok} | {tool_ok} | {quality_score} | {docs} |".format(
                id=row["id"],
                expected_task_type=row["expected_task_type"],
                predicted_task_type=row["predicted_task_type"],
                actual_tool=row["actual_tool"],
                route_ok="是" if row["route_ok"] else "否",
                tool_ok="是" if row["tool_ok"] else "否",
                quality_score=row["quality_score"],
                docs=", ".join(row["retrieved_doc_ids"]),
            )
        )

    lines.extend(
        [
            "",
            "## 结论",
            "",
            "- 当前 MVP 已具备教师输入、任务路由、本地知识库检索、LLM 生成、工具结构化输出和评估记录的完整链路。",
            "- 路由器采用可解释关键词规则，适合作为最小版本；后续可用这批评估数据扩展为训练集，替换为分类模型。",
            "- 生成质量评分是轻量规则分，主要检查结构完整性、知识点覆盖和关键词命中；后续建议加入教师人工评分和学生学习效果指标。",
        ]
    )
    return "\n".join(lines) + "\n"
