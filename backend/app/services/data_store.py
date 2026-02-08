from __future__ import annotations

from typing import Union

from ..config import Settings
from .local_store import LocalStore
from .firestore_store import FirestoreStore
from .mysql_store import MySQLStore


ProgramStore = Union[LocalStore, FirestoreStore, MySQLStore]


def get_store(settings: Settings) -> ProgramStore:
    if settings.use_mysql:
        try:
            return MySQLStore(
                host=settings.cloudsql_host,
                port=settings.cloudsql_port,
                unix_socket=settings.cloudsql_unix_socket,
                user=settings.cloudsql_user,
                password=settings.cloudsql_password,
                database=settings.cloudsql_database,
                connect_timeout=settings.cloudsql_connect_timeout,
            )
        except Exception as exc:
            if settings.app_env != "local":
                raise RuntimeError("USE_MYSQL=true but MySQL connection is not available") from exc
            # Local-only fallback for development
            return LocalStore(settings.data_dir)

    if settings.use_firestore:
        if not settings.gcp_project_id:
            raise RuntimeError("USE_FIRESTORE=true but GCP_PROJECT_ID is not set")
        try:
            return FirestoreStore(settings.gcp_project_id, settings.gcp_firestore_database)
        except Exception:
            # Fallback to local store if Firestore is misconfigured
            return LocalStore(settings.data_dir)
    return LocalStore(settings.data_dir)
