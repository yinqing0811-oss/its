from __future__ import annotations

from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import AgentService
from .config import get_settings
from .models import AgentRequest, AgentResponse, KnowledgeSearchResponse


settings = get_settings()
service = AgentService(settings=settings)

app = FastAPI(title=settings.app_name, version="1.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, Union[str, bool]]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "llm_provider": settings.llm_provider,
        "has_openai_key": bool(settings.openai_api_key),
    }


@app.post("/api/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest) -> AgentResponse:
    try:
        return service.run(request)
    except Exception as exc:  # pragma: no cover - FastAPI should expose a clean error.
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/knowledge/search", response_model=KnowledgeSearchResponse)
def search_knowledge(query: str, top_k: int = 4) -> KnowledgeSearchResponse:
    return KnowledgeSearchResponse(query=query, results=service.knowledge_base.search(query, top_k=top_k))


@app.get("/api/evaluations")
def evaluation_records(limit: int = 50) -> dict[str, object]:
    return {"records": service.read_records(limit=limit)}
