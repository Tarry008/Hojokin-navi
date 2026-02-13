from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Optional


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
    use_mysql: bool
    cloudsql_host: str
    cloudsql_port: int
    cloudsql_unix_socket: Optional[str]
    cloudsql_user: str
    cloudsql_password: str
    cloudsql_database: str
    cloudsql_connect_timeout: int
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
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
        use_mysql=_to_bool(os.getenv("USE_MYSQL"), True),
        cloudsql_host=os.getenv("CLOUDSQL_HOST", "127.0.0.1"),
        cloudsql_port=int(os.getenv("CLOUDSQL_PORT", "3307")),
        cloudsql_unix_socket=os.getenv("CLOUDSQL_UNIX_SOCKET"),
        cloudsql_user=os.getenv("CLOUDSQL_USER", "root"),
        cloudsql_password=os.getenv("CLOUDSQL_PASSWORD", ""),
        cloudsql_database=os.getenv("CLOUDSQL_DATABASE", "hojokin_db"),
        cloudsql_connect_timeout=int(os.getenv("CLOUDSQL_CONNECT_TIMEOUT", "5")),
        gcp_project_id=os.getenv("GCP_PROJECT_ID"),
        gcp_region=os.getenv("GCP_REGION", "asia-northeast1"),
        gcp_firestore_database=os.getenv("GCP_FIRESTORE_DATABASE", "(default)"),
        gcp_storage_bucket=os.getenv("GCP_STORAGE_BUCKET"),
        use_firestore=_to_bool(os.getenv("USE_FIRESTORE"), False),
        use_vertex_ai=_to_bool(os.getenv("USE_VERTEX_AI"), False),
        vertex_model=os.getenv("VERTEX_MODEL", "gemini-2.5-flash"),
        vertex_temperature=float(os.getenv("VERTEX_TEMPERATURE", "0.2")),
        base_dir=base_dir,
        backend_dir=backend_dir,
        frontend_dir=frontend_dir,
        data_dir=data_dir,
    )
