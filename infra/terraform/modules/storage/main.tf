resource "google_storage_bucket" "raw_data" {
  name                        = "ai-hackathon-raw-data-${var.project_id}"
  location                    = "ASIA-NORTHEAST1"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "vector_data" {
  name                        = "ai-hackathon-vector-data-${var.project_id}"
  location                    = "ASIA-NORTHEAST1"
  uniform_bucket_level_access = true
}
