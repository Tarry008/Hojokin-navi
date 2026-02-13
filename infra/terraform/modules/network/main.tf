// vpcはグローバルリソース
resource "google_compute_network" "vpc_network" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
}

// subnetはリージョンリソース
resource "google_compute_subnetwork" "network-subnet" {
  name                     = "${var.vpc_name}-subnet"
  ip_cidr_range            = "10.0.1.0/24"
  region                   = "asia-northeast1"
  network                  = google_compute_network.vpc_network.id
  private_ip_google_access = true
}

resource "google_compute_global_address" "vertex_ai-ip-range" {
  name          = "vertex-ai-ip-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

resource "google_service_networking_connection" "vertex_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.vertex_ai-ip-range.name]
}
