from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[1]
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
RUNTIME_DIR = PROJECT_ROOT / "runtime"


@dataclass(frozen=True)
class Settings:
    app_name: str = "ITS Agent MVP"
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    allow_mock_when_no_key: bool = os.getenv("ITS_ALLOW_MOCK_LLM", "1") == "1"
    knowledge_base_path: Path = Path(os.getenv("ITS_KB_PATH", str(DATA_DIR / "knowledge_base.jsonl")))
    evaluation_cases_path: Path = Path(os.getenv("ITS_EVAL_CASES_PATH", str(DATA_DIR / "evaluation_cases.json")))
    run_log_path: Path = Path(os.getenv("ITS_RUN_LOG_PATH", str(RUNTIME_DIR / "agent_runs.jsonl")))


def get_settings() -> Settings:
    return Settings()
