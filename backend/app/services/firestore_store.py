from __future__ import annotations

from typing import List, Optional

from ..models import Program, Eligibility


class FirestoreStore:
    def __init__(self, project_id: str, database: str = "(default)"):
        try:
            from google.cloud import firestore  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("google-cloud-firestore is not available") from exc

        self.client = firestore.Client(project=project_id, database=database)

    def list_programs(self, municipality: Optional[str] = None) -> List[Program]:
        query = self.client.collection("programs")
        if municipality:
            query = query.where("municipality", "==", municipality)
        docs = query.stream()
        return [self._doc_to_program(doc) for doc in docs]

    def get_program(self, program_id: str) -> Optional[Program]:
        doc = self.client.collection("programs").document(program_id).get()
        if not doc.exists:
            return None
        return self._doc_to_program(doc)

    def _doc_to_program(self, doc) -> Program:
        data = doc.to_dict() or {}
        eligibility = Eligibility.model_validate(data.get("eligibility", {}))
        return Program(
            program_id=data.get("program_id", doc.id),
            program_name=data.get("program_name", ""),
            municipality=data.get("municipality", ""),
            summary=data.get("summary", ""),
            eligibility=eligibility,
            deadline=data.get("deadline"),
            gray_zone_guidance=data.get("gray_zone_guidance", []),
        )
