from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from .config import Settings


@dataclass(frozen=True)
class LLMResult:
    text: str
    provider: str
    model: str
    used_real_api: bool


class LLMClientProtocol(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResult:
        ...


class MockLLMClient:
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResult:
        is_exercise = "exercise_generation" in user_prompt or "练习题" in user_prompt
        if is_exercise:
            text = (
                "建议生成分层练习：先用基础题确认概念，再用边界题暴露错误模式，"
                "最后用项目小任务检查迁移能力。每题都要附知识点、难度和测试用例。"
            )
        else:
            text = (
                "建议采用诊断导入、关键概念讲解、教师示范、学生练习、即时诊断和复盘总结的结构。"
                "课堂重点应围绕学生薄弱知识点展开，并保留可观察的评价指标。"
            )
        return LLMResult(text=text, provider="mock", model="deterministic-mock", used_real_api=False)


class OpenAICompatibleClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResult:
        if not self.settings.openai_api_key:
            if self.settings.allow_mock_when_no_key:
                return MockLLMClient().generate(system_prompt, user_prompt)
            raise RuntimeError("OPENAI_API_KEY is required when mock fallback is disabled.")

        url = f"{self.settings.openai_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.settings.openai_model,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=40.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        text = data["choices"][0]["message"]["content"]
        return LLMResult(
            text=text,
            provider="openai-compatible",
            model=self.settings.openai_model,
            used_real_api=True,
        )


def build_llm_client(settings: Settings) -> LLMClientProtocol:
    if settings.llm_provider.lower() == "mock":
        return MockLLMClient()
    return OpenAICompatibleClient(settings)
