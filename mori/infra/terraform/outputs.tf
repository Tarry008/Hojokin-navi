output "cloud_run_service_name" {
  value = google_cloud_run_v2_service.api.name
}

output "storage_bucket" {
  value = google_storage_bucket.pdfs.name
}