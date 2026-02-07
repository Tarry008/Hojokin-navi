resource "google_artifact_registry_repository_iam_member" "run_sa_repo_reader" {
  location   = google_artifact_registry_repository.app_repo.location
  repository = google_artifact_registry_repository.app_repo.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.run_sa.email}"
}
