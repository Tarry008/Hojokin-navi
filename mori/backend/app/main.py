from __future__ import annotations

from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import load_settings
from .models import RecommendationResponse, UserInput, ProgramRecommendation
from .services.data_store import get_store
from .services.rag_engine import recommend_programs
from .services.vertex_llm import LLM_SCHEMA_DESCRIPTION, call_vertex_ai

load_dotenv()
settings = load_settings()
store = get_store(settings)

app = FastAPI(title="自治体給付金・補助金 判定AI", version="mvp-0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_root = settings.frontend_dir
dist_dir = frontend_root / "dist"
assets_dir = dist_dir / "assets"

if dist_dir.exists() and assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


def _llm_callback(user: UserInput, program) -> ProgramRecommendation | None:
    if not settings.use_vertex_ai:
        return None
    llm_result = call_vertex_ai(user, program, settings)
    if not llm_result:
        return None
    evidence = llm_result.evidence if llm_result.evidence else program.evidence
    return ProgramRecommendation(
        program_id=program.program_id,
        program_name=program.program_name,
        level=llm_result.level,
        confidence=round(llm_result.confidence, 2),
        reasons=llm_result.reasons,
        deadline=llm_result.deadline,
        todo=llm_result.todo,
        evidence=evidence,
    )


@app.get("/")
async def root() -> FileResponse:
    index_path = dist_dir / "index.html" if dist_dir.exists() else frontend_root / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_path)


@app.get("/api/health")
async def health() -> dict:
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z",
        "env": settings.app_env,
    }


@app.get("/api/llm/format")
async def llm_format() -> dict:
    return {"format": LLM_SCHEMA_DESCRIPTION}


@app.post("/api/recommendations", response_model=RecommendationResponse)
async def recommendations(payload: UserInput) -> RecommendationResponse:
    municipality = payload.municipality or "○○市"
    programs = store.list_programs(payload.municipality)
    if not programs:
        programs = store.list_programs()

    results = recommend_programs(payload, programs, llm_callback=_llm_callback)

    return RecommendationResponse(
        municipality=municipality,
        results=results,
        meta={"model": "gcp-vertex-optional", "version": "mvp-0.1"},
    )


@app.get("/api/programs")
async def list_programs(municipality: str | None = None) -> dict:
    programs = store.list_programs(municipality)
    return {
        "programs": [
            {
                "program_id": p.program_id,
                "program_name": p.program_name,
                "municipality": p.municipality,
                "summary": p.summary,
                "deadline": p.deadline,
            }
            for p in programs
        ]
    }


@app.get("/api/programs/{program_id}")
async def program_detail(program_id: str) -> dict:
    program = store.get_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program.model_dump()
