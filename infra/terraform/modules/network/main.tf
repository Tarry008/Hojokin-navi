// vpcはグローバルリソース
resource "google_compute_network" "vpc_network" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
}

// subnetはリージョンリソース
resource "google_compute_subnetwork" "network-subnet" {
  name          = "${var.vpc_name}-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = "asia-northeast1"
  network       = google_compute_network.vpc_network.id
}

resource "google_vpc_access_connector" "connector" {
  name          = "${var.vpc_name}-connector"
  region        = "asia-northeast1"
  network       = google_compute_network.vpc_network.name
  ip_cidr_range = "10.8.0.0/28"

  min_instances = 2
  max_instances = 3
}
