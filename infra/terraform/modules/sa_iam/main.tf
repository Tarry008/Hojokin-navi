resource "google_artifact_registry_repository_iam_member" "run_sa_repo_reader" {
  location   = var.repository_location
  repository = var.repository_id
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${var.run_sa_email}"
}

resource "google_storage_bucket_iam_member" "raw_bucket_admin" {
  bucket = var.raw_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.run_sa_email}"
}

resource "google_storage_bucket_iam_member" "vector_bucket_admin" {
  bucket = var.vector_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.run_sa_email}"
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${var.run_sa_email}"
}

resource "google_cloud_run_service_iam_member" "eventarc_run_invoker" {
  location = "asia-northeast1"
  service  = var.cloud_run_service_name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.eventarc_sa_email}"
}

resource "google_project_iam_member" "pubsub_service_account_token_creator" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "eventarc_sa_receiver" {
  project = var.project_id
  role    = "roles/eventarc.eventReceiver"
  member  = "serviceAccount:${var.eventarc_sa_email}"
}

resource "google_project_iam_member" "gcs_pubsub_publishing" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:service-${var.project_number}@gs-project-accounts.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${var.run_sa_email}"
}

resource "google_project_iam_member" "cloudsql_instance_user" {
  project = var.project_id
  role    = "roles/cloudsql.instanceUser"
  member  = "serviceAccount:${var.run_sa_email}" # 実行用サービスアカウントのメールアドレス
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.run_sa_email}"
}
