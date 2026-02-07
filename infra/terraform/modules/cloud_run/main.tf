# Artifact Registry
resource "google_artifact_registry_repository" "app_repo" {
  location      = "asia-northeast1"
  repository_id = var.repository_id
  format        = "DOCKER"
}

# サービスアカウントの作成
resource "google_service_account" "run_sa" {
  account_id   = "cloud-run-app-sa"
  display_name = "Cloud Run Application Service Account"
}

# Cloud Run の作成
resource "google_cloud_run_v2_service" "default" {
  name     = var.service_name
  location = "asia-northeast1"
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    service_account = google_service_account.run_sa.email

    containers {
      image = "asia-northeast1-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app_repo.repository_id}/${var.image_name}:${var.image_tag}"

      env {
        name  = "VERTEX_INDEX_ENDPOINT_ID"
        value = var.vertex_index_endpoint_id
      }
    }

    vpc_access {
      network_interfaces {
        network    = var.vpc_id
        subnetwork = var.subnet_id
      }
    }
  }
}
