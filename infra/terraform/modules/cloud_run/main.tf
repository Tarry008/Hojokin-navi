# Cloud Run の作成
resource "google_cloud_run_v2_service" "default" {
  name     = var.service_name
  location = "asia-northeast1"
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  deletion_protection = false

  template {
    service_account = var.run_sa_email

    containers {
      image = "${var.repository_url}/${var.image_name}:${var.image_tag}"

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
