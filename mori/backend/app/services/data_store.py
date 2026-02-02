from __future__ import annotations

from typing import Union

from ..config import Settings
from .local_store import LocalStore
from .firestore_store import FirestoreStore


ProgramStore = Union[LocalStore, FirestoreStore]


def get_store(settings: Settings) -> ProgramStore:
    if settings.use_firestore:
        if not settings.gcp_project_id:
            raise RuntimeError("USE_FIRESTORE=true but GCP_PROJECT_ID is not set")
        try:
            return FirestoreStore(settings.gcp_project_id, settings.gcp_firestore_database)
        except Exception:
            # Fallback to local store if Firestore is misconfigured
            return LocalStore(settings.data_dir)
    return LocalStore(settings.data_dir)
