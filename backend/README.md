# Backend (FastAPI)

自治体の給付金・補助金の判定AI (RAG) をローカルで動かすためのバックエンドです。Google Cloud (Firestore / Cloud Storage / Vertex AI) を前提に設計していますが、ローカルでは `data/seed_programs.json` を使って動きます。

## 前提
- uv を使用
- Python 3.12.8
- フロントエンドは React (Vite + TypeScript) + Tailwind CSS

## ローカル起動（バックエンド）

```
cd mori/backend
uv python install 3.12.8
uv venv --python 3.12.8 .venv
uv pip install -r requirements.txt --python .venv
copy .env.example .env
uv run --python .venv -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## ローカル起動（フロントエンド）

別ターミナルで以下を実行します。

```
cd mori/frontend
npm install
npm run dev
```

- フロントエンド: `http://localhost:5173`
- バックエンドAPI: `http://localhost:8000`

## バックエンドからフロントエンドを配信したい場合

```
cd mori/frontend
npm run build
```

その後、バックエンドを起動すると `http://localhost:8000` で `dist` が配信されます。
この場合は `FRONTEND_ORIGIN=http://localhost:8000` に変更してください。

## API

- 本APIの対象自治体は `港区` のみです。

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
  "municipality": "港区",
  "results": [
    {
      "program_id": "minato_single_support_004",
      "program_name": "港区 若年単身者家賃支援",
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

### Cloud Storage
- PDF原本を `gs://<bucket>/pdfs/<program_id>.pdf` に置く想定。

### Vertex AI
- `USE_VERTEX_AI=true` を設定してください。`/api/recommendations` の根拠 (`reasons/evidence`) と TODO は LLM 生成を必須にしています。
- LLMの出力フォーマットは `/api/llm/format` で確認可能。
