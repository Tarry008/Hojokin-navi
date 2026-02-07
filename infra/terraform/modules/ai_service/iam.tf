resource "google_storage_bucket_iam_member" "raw_bucket_admin" {
  bucket = var.raw_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.cloud_run_service_account_email}"
}

resource "google_storage_bucket_iam_member" "vector_bucket_admin" {
  bucket = var.vector_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.cloud_run_service_account_email}"
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${var.cloud_run_service_account_email}"
}
