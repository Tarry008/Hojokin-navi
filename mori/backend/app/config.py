from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_host: str
    app_port: int
    frontend_origin: str
    gcp_project_id: str | None
    gcp_region: str
    gcp_firestore_database: str
    gcp_storage_bucket: str | None
    use_firestore: bool
    use_vertex_ai: bool
    vertex_model: str
    vertex_temperature: float
    base_dir: Path
    backend_dir: Path
    frontend_dir: Path
    data_dir: Path


def load_settings() -> Settings:
    backend_dir = Path(__file__).resolve().parents[1]
    base_dir = Path(__file__).resolve().parents[2]
    frontend_dir = base_dir / "frontend"
    data_dir = backend_dir / "data"

    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:8000"),
        gcp_project_id=os.getenv("GCP_PROJECT_ID"),
        gcp_region=os.getenv("GCP_REGION", "asia-northeast1"),
        gcp_firestore_database=os.getenv("GCP_FIRESTORE_DATABASE", "(default)"),
        gcp_storage_bucket=os.getenv("GCP_STORAGE_BUCKET"),
        use_firestore=_to_bool(os.getenv("USE_FIRESTORE"), False),
        use_vertex_ai=_to_bool(os.getenv("USE_VERTEX_AI"), False),
        vertex_model=os.getenv("VERTEX_MODEL", "gemini-1.5-pro-002"),
        vertex_temperature=float(os.getenv("VERTEX_TEMPERATURE", "0.2")),
        base_dir=base_dir,
        backend_dir=backend_dir,
        frontend_dir=frontend_dir,
        data_dir=data_dir,
    )
