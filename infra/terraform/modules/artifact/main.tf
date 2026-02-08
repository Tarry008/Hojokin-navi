# Artifact Registry
resource "google_artifact_registry_repository" "app_repo" {
  location      = "asia-northeast1"
  repository_id = var.repository_id
  format        = "DOCKER"
}
