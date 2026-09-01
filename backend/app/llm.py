from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol

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


class ChatCompletionsClient:
    def __init__(
        self,
        provider: str,
        api_key: Optional[str],
        api_key_env_name: str,
        base_url: str,
        model: str,
        extra_payload: Optional[dict[str, Any]] = None,
    ):
        self.provider = provider
        self.api_key = api_key
        self.api_key_env_name = api_key_env_name
        self.base_url = base_url
        self.model = model
        self.extra_payload = extra_payload or {}

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResult:
        if not self.api_key:
            raise RuntimeError(f"{self.api_key_env_name} is required when mock fallback is disabled.")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        payload.update(self.extra_payload)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=40.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500]
            raise RuntimeError(
                f"{self.provider} API request failed with HTTP {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"{self.provider} API request failed: {exc}") from exc

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected {self.provider} API response shape: {data}") from exc

        return LLMResult(
            text=text,
            provider=self.provider,
            model=self.model,
            used_real_api=True,
        )


class FallbackLLMClient:
    def __init__(self, primary: ChatCompletionsClient, allow_mock_when_no_key: bool):
        self.primary = primary
        self.allow_mock_when_no_key = allow_mock_when_no_key

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResult:
        if not self.primary.api_key and self.allow_mock_when_no_key:
            return MockLLMClient().generate(system_prompt, user_prompt)
        return self.primary.generate(system_prompt, user_prompt)


def _build_deepseek_client(settings: Settings) -> ChatCompletionsClient:
    extra_payload: dict[str, Any] = {
        "thinking": {"type": "enabled" if settings.deepseek_thinking_enabled else "disabled"},
    }
    if settings.deepseek_thinking_enabled:
        extra_payload["reasoning_effort"] = settings.deepseek_reasoning_effort
    else:
        extra_payload["temperature"] = settings.llm_temperature

    return ChatCompletionsClient(
        provider="deepseek",
        api_key=settings.effective_llm_api_key,
        api_key_env_name=settings.effective_key_env_name,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
        extra_payload=extra_payload,
    )


def _build_openai_compatible_client(settings: Settings) -> ChatCompletionsClient:
    provider = "openai-compatible" if settings.normalized_provider == "openai" else settings.normalized_provider
    return ChatCompletionsClient(
        provider=provider,
        api_key=settings.openai_api_key,
        api_key_env_name="OPENAI_API_KEY",
        base_url=settings.openai_base_url,
        model=settings.openai_model,
        extra_payload={"temperature": settings.llm_temperature},
    )


def build_llm_client(settings: Settings) -> LLMClientProtocol:
    if settings.normalized_provider == "mock":
        return MockLLMClient()

    if settings.normalized_provider == "deepseek":
        primary = _build_deepseek_client(settings)
    else:
        primary = _build_openai_compatible_client(settings)

    return FallbackLLMClient(primary=primary, allow_mock_when_no_key=settings.allow_mock_when_no_key)
