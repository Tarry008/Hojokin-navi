# GCP Infrastructure (MVP)

## 構成
- Cloud Storage: PDF原本を保存（差し替え容易）
- Firestore: 制度メタデータ + evidenceチャンク（必要ならembeddingも追加）
- Cloud Run: FastAPIバックエンドをデプロイ
- Vertex AI: LLM判定（任意）

## Terraformの使い方
1. `terraform/variables.tf` の値を設定
2. `terraform` フォルダで初期化

```
terraform init
terraform plan
```

`google_cloud_run_v2_service` の `image` にビルドしたコンテナを指定してください。

## Firestore データモデル
- `programs/{program_id}`
  - program_name, municipality, summary, eligibility, deadline, todo_steps, gray_zone_guidance
- `programs/{program_id}/evidence/{evidence_id}`
  - page, source_url, snippet

## Cloud Storage
- `gs://<bucket>/pdfs/<program_id>.pdf`

## Vertex AI
- `USE_VERTEX_AI=true` を設定し、`VERTEX_MODEL` を指定
- Cloud Run サービスアカウントに Vertex AI 使用権限を付与
