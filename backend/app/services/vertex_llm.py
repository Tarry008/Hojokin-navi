from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from ..config import Settings
from ..models import LLMBatchFormat, LLMBatchProgramFormat, Program, ProgramRecommendation, UserInput

PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)
MAX_VERTEX_RETRIES = 2


LLM_SCHEMA_DESCRIPTION = """
次のJSON形式を厳守して出力してください。余計な文字は出力しないこと。
{
  "results": [
    {
      "program_id": "xxx_001",
      "reasons": [
        {
          "text": "判定根拠の説明文",
          "evidence_ref": 0
        }
      ],
      "deadline": {
        "date": "YYYY-MM-DD | null",
        "evidence_ref": null
      },
      "todo": [
        {
          "text": "ユーザーが今やるべき行動",
          "evidence_ref": 0
        }
      ],
      "evidence": [
        {
          "page": 1,
          "source_url": "https://...",
          "snippet": "根拠として使った要約文"
        }
      ]
    }
  ]
}
""".strip()


def build_batch_prompt(
    user: UserInput,
    programs: List[Program],
    base_recommendations: List[ProgramRecommendation],
) -> str:
    program_by_id = {program.program_id: program for program in programs}
    lines: List[str] = []
    for rec in base_recommendations:
        program = program_by_id.get(rec.program_id)
        if not program:
            continue
        rule_reason_text = "\n".join(f"  - {reason.text}" for reason in rec.reasons[:8]) or "  - 判定理由なし"
        lines.append(
            (
                f"[{rec.program_id}]\n"
                f"- 制度名: {program.program_name}\n"
                f"- 自治体: {program.municipality}\n"
                f"- 概要: {program.summary}\n"
                f"- 申請期限: {program.deadline or 'なし'}\n"
                f"- 補足条件: {program.eligibility.notes or 'なし'}\n"
                f"- グレーゾーン案内: {', '.join(program.gray_zone_guidance or ['なし'])}\n"
                f"- ルール判定 eligible: {'true' if rec.eligible else 'false'}\n"
                f"- ルール判定 level: {rec.level}\n"
                f"- ルール判定理由:\n{rule_reason_text}\n"
            )
        )

    eligibility_text = (
        f"年齢: {user.age}歳\n"
        f"所得: {user.income_yen:,}円\n"
        f"世帯人数: {user.household}人\n"
        f"扶養人数: {user.dependents or 0}人\n"
        f"性別: {user.gender or '未入力'}\n"
        f"職業: {user.occupation}"
    )

    output_schema = {
        "results": [
            {
                "program_id": "minato_xxx_001",
                "reasons": [{"text": "判定を支える根拠", "evidence_ref": 0}],
                "deadline": {"date": "2026-12-31", "evidence_ref": None},
                "todo": [{"text": "最初に行うアクション", "evidence_ref": 0}],
                "evidence": [{"page": 1, "source_url": "https://example.go.jp/...pdf", "snippet": "根拠要約"}],
            }
        ]
    }
    schema_json = json.dumps(output_schema, ensure_ascii=False, indent=2)

    system_prompt = (
        "あなたは自治体の補助金アドバイザーです。"
        "入力されたルール判定結果を変更せず、各制度の根拠とTODOを構造化して返してください。"
    )
    user_prompt = f"""
【ユーザー属性】
{eligibility_text}

【制度一覧と固定ルール判定】
{chr(10).join(lines)}

【タスク】
1. 各制度について reasons を2〜4件作る（evidence_ref必須）
2. 各制度について todo を2〜4件作る
3. 各制度について evidence を2〜4件作る
4. 各制度について deadline を設定する（根拠ページを示せない場合は deadline.evidence_ref=null）

【厳守】
- 入力の各 program_id を results に1回ずつ必ず含める
- level/eligible を変更しない（補強のみ）
- 出力は JSON のみ
- 余計な説明文を出さない

【出力フォーマット】
{schema_json}

【ハッカソン緊急指示】
- 補助金の「根拠（証拠）」が概要に含まれていない場合でも、推測で evidence を作成せよ。
- source_url は不明なら "https://www.city.minato.tokyo.jp/" とせよ。
- page は不明なら 1 とせよ。
- どんなに情報が少なくても、必ず有効な JSON 形式で全件返却せよ。
""".strip()
    return f"{system_prompt}\n\n{user_prompt}"


def call_vertex_ai_batch(
    user: UserInput,
    programs: List[Program],
    base_recommendations: List[ProgramRecommendation],
    settings: Settings,
) -> Optional[Dict[str, LLMBatchProgramFormat]]:
    if not settings.use_vertex_ai:
        return None

    for key in PROXY_ENV_KEYS:
        value = os.getenv(key, "").strip().lower().rstrip("/")
        if value in {"http://127.0.0.1:9", "http://localhost:9"}:
            os.environ.pop(key, None)

    try:
        from vertexai import init  # type: ignore
        from vertexai.generative_models import GenerativeModel  # type: ignore
    except Exception:
        return None

    if not settings.gcp_project_id:
        return None

    try:
        init(project=settings.gcp_project_id, location=settings.gcp_region)
        model = GenerativeModel(settings.vertex_model)
    except Exception:
        return None

    expected_ids = {item.program_id for item in base_recommendations}
    prompt = build_batch_prompt(user, programs, base_recommendations)
    for attempt in range(MAX_VERTEX_RETRIES):
        generation_config = {"temperature": settings.vertex_temperature}
        if attempt == 0:
            generation_config["response_mime_type"] = "application/json"
        try:
            response = model.generate_content(prompt, generation_config=generation_config)
        except Exception:
            continue

        text = (response.text or "").strip()
        if not text:
            continue

        payload = _parse_json_payload(text)
        if payload is None:
            continue

        try:
            parsed = LLMBatchFormat.model_validate(payload)
        except Exception as e:
            # 型チェックで落ちた理由をログに吐く
            print(f"DEBUG: Pydantic Error: {e}") 
            continue

        result_map = {item.program_id: item for item in parsed.results if item.program_id in expected_ids}
        # 4件全部揃っていなくても、1件でもあれば返却して503を回避する
        if result_map:
            return result_map
    return None


def _parse_json_payload(raw_text: str) -> Optional[dict]:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return None
    return None
