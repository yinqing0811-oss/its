from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[1]
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
RUNTIME_DIR = PROJECT_ROOT / "runtime"


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = field(default_factory=lambda: os.getenv("ITS_APP_NAME", "ITS Agent MVP"))
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "deepseek"))

    deepseek_api_key: Optional[str] = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY"))
    deepseek_base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    deepseek_model: str = field(default_factory=lambda: os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"))
    deepseek_thinking: str = field(default_factory=lambda: os.getenv("DEEPSEEK_THINKING", "disabled"))
    deepseek_reasoning_effort: str = field(default_factory=lambda: os.getenv("DEEPSEEK_REASONING_EFFORT", "high"))

    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    llm_temperature: float = field(default_factory=lambda: _env_float("LLM_TEMPERATURE", 0.3))
    allow_mock_when_no_key: bool = field(default_factory=lambda: _env_bool("ITS_ALLOW_MOCK_LLM", True))
    knowledge_base_path: Path = field(
        default_factory=lambda: Path(os.getenv("ITS_KB_PATH", str(DATA_DIR / "knowledge_base.jsonl")))
    )
    evaluation_cases_path: Path = field(
        default_factory=lambda: Path(os.getenv("ITS_EVAL_CASES_PATH", str(DATA_DIR / "evaluation_cases.json")))
    )
    run_log_path: Path = field(
        default_factory=lambda: Path(os.getenv("ITS_RUN_LOG_PATH", str(RUNTIME_DIR / "agent_runs.jsonl")))
    )

    @property
    def normalized_provider(self) -> str:
        return self.llm_provider.strip().lower()

    @property
    def deepseek_thinking_enabled(self) -> bool:
        return self.deepseek_thinking.strip().lower() in {"1", "true", "yes", "on", "enabled"}

    @property
    def effective_llm_api_key(self) -> Optional[str]:
        if self.normalized_provider == "deepseek":
            return self.deepseek_api_key or self.openai_api_key
        if self.normalized_provider == "mock":
            return None
        return self.openai_api_key

    @property
    def effective_llm_base_url(self) -> str:
        if self.normalized_provider == "deepseek":
            return self.deepseek_base_url
        return self.openai_base_url

    @property
    def effective_llm_model(self) -> str:
        if self.normalized_provider == "deepseek":
            return self.deepseek_model
        if self.normalized_provider == "mock":
            return "deterministic-mock"
        return self.openai_model

    @property
    def effective_key_env_name(self) -> str:
        if self.normalized_provider == "deepseek":
            return "DEEPSEEK_API_KEY"
        return "OPENAI_API_KEY"


def get_settings() -> Settings:
    return Settings()
