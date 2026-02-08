output "repository_id" {
  value = google_artifact_registry_repository.app_repo.repository_id
}

output "repository_location" {
  value = google_artifact_registry_repository.app_repo.location
}
