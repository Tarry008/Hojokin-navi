from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from ..models import Program


class LocalStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._programs_cache: Optional[List[Program]] = None

    def list_programs(self, municipality: Optional[str] = None) -> List[Program]:
        programs = self._load_programs()
        if municipality:
            return [p for p in programs if p.municipality == municipality]
        return programs

    def get_program(self, program_id: str) -> Optional[Program]:
        return next((p for p in self._load_programs() if p.program_id == program_id), None)

    def _load_programs(self) -> List[Program]:
        if self._programs_cache is not None:
            return self._programs_cache
        programs_path = self.data_dir / "seed_programs.json"
        raw = json.loads(programs_path.read_text(encoding="utf-8"))
        self._programs_cache = [Program.model_validate(item) for item in raw]
        return self._programs_cache
