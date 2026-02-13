# Cloud Run の作成
resource "google_cloud_run_v2_service" "default" {
  name     = var.service_name
  location = "asia-northeast1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  deletion_protection = false

  template {
    service_account = var.run_sa_email

    containers {
      image = "${var.repository_url}/${var.image_name}:${var.image_tag}"

      ports {
        container_port = 8080
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      env {
        name  = "VERTEX_INDEX_ENDPOINT_ID"
        value = var.vertex_index_endpoint_id
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCP_REGION"
        value = "asia-northeast1"
      }

      env {
        name  = "USE_VERTEX_AI"
        value = true
      }

      env {
        name  = "CLOUDSQL_UNIX_SOCKET"
        value = "/cloudsql/${var.db_instance_connection_name}"
      }
      env {
        name  = "CLOUDSQL_INSTANCE"
        value = var.db_instance_connection_name
      }

      env {
        name  = "CLOUDSQL_DATABASE"
        value = var.db_name
      }

      env {
        name  = "CLOUDSQL_PORT"
        value = "3306" # MySQLなら3306、Postgresなら5432
      }

      env {
        name  = "CLOUDSQL_USER"
        value = var.db_user_name
      }

      env {
        name = "CLOUDSQL_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = var.secrets_db_password_id
            version = "latest"
          }
        }
      }
    }

    vpc_access {
      network_interfaces {
        network    = var.vpc_id
        subnetwork = var.subnet_id
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [var.db_instance_connection_name]
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  location = "asia-northeast1"
  name     = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
