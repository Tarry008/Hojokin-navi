from __future__ import annotations

import json
from typing import Optional

from ..models import UserInput, Program, LLMProgramFormat
from ..config import Settings


LLM_SCHEMA_DESCRIPTION = """
次のJSON形式を厳守して出力してください。余計な文字は出力しないこと。
{
  "program_id": "xxx_001",
  "level": "high | medium | low | unknown",
  "confidence": 0.0,
  "reasons": [
    {
      "text": "理由の説明文",
      "evidence_ref": 0
    }
  ],
  "deadline": {
    "date": "YYYY-MM-DD | null",
    "evidence_ref": 1
  },
  "todo": [
    {
      "text": "ユーザーが最初にやるべき行動",
      "evidence_ref": 2
    }
  ],
  "evidence": [
    {
      "page": 0,
      "source_url": "",
      "snippet": ""
    }
  ]
}
""".strip()


def build_prompt(user: UserInput, program: Program) -> str:
    return (
        "あなたは自治体の給付金・補助金の判定アシスタントです。"
        "対象/対象外の断定ではなく、対象になるための条件も含めて説明してください。\n\n"
        f"ユーザー情報: {user.model_dump()}\n"
        f"制度情報: {program.model_dump()}\n\n"
        f"出力フォーマット:\n{LLM_SCHEMA_DESCRIPTION}"
    )


def call_vertex_ai(user: UserInput, program: Program, settings: Settings) -> Optional[LLMProgramFormat]:
    if not settings.use_vertex_ai:
        return None
    try:
        from vertexai import init  # type: ignore
        from vertexai.generative_models import GenerativeModel  # type: ignore
    except Exception:
        return None

    if not settings.gcp_project_id:
        return None

    init(project=settings.gcp_project_id, location=settings.gcp_region)
    model = GenerativeModel(settings.vertex_model)
    response = model.generate_content(
        build_prompt(user, program),
        generation_config={"temperature": settings.vertex_temperature},
    )
    if not response.text:
        return None

    try:
        payload = json.loads(response.text)
        return LLMProgramFormat.model_validate(payload)
    except Exception:
        return None
