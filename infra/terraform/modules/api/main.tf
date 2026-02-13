resource "google_project_service" "vertex_ai" {
  project = var.project_id
  service = "aiplatform.googleapis.com"

  # APIを無効化した時に、依存しているリソースまで消さないための設定
  disable_on_destroy = false
}
