# Backend (FastAPI)

自治体の給付金・補助金の判定AI (RAG) をローカルで動かすためのバックエンドです。Google Cloud (Firestore / Cloud Storage / Vertex AI) を前提に設計していますが、ローカルでは `data/seed_programs.json` を使って動きます。

## 前提
- uv を使用
- Python 3.12.8

## ローカル起動（uv）

```
cd mori/backend
uv python install 3.12.8
uv venv --python 3.12.8 .venv
uv pip install -r requirements.txt --python .venv
copy .env.example .env
uv run --python .venv -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

ブラウザで `http://localhost:8000` を開くとフロントエンドが表示されます。

## API

### POST /api/recommendations
入力:
```
{
  "age": 25,
  "income_yen": 3200000,
  "household": 2,
  "occupation": "会社員",
  "dependents": 0
}
```

出力:
```
{
  "municipality": "○○市",
  "results": [
    {
      "program_id": "city_young_single_001",
      "program_name": "○○市 若年単身者支援金",
      "level": "high",
      "confidence": 0.82,
      "reasons": [
        {"text": "対象年齢に該当する", "evidence_ref": 0}
      ],
      "deadline": {"date": "2026-02-28", "evidence_ref": 1},
      "todo": [
        {"text": "学生証または本人確認書類を準備する", "evidence_ref": 2}
      ],
      "evidence": [
        {"page": 2, "source_url": "...", "snippet": "..."}
      ]
    }
  ],
  "meta": {"model": "gcp-vertex-optional", "version": "mvp-0.1"}
}
```

## GCP連携

### Firestore
- `USE_FIRESTORE=true` + `GCP_PROJECT_ID` を設定すると Firestore を読み書きします。
- ローカルで試す場合は `scripts/seed_firestore.py` を実行してください。

### Cloud Storage
- PDF原本を `gs://<bucket>/pdfs/<program_id>.pdf` に置く想定。

### Vertex AI
- `USE_VERTEX_AI=true` を設定すると `/api/recommendations` が Vertex AI の結果を優先します（失敗時はルールベースにフォールバック）。
- LLMの出力フォーマットは `/api/llm/format` で確認可能。
