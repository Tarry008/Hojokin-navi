output "raw_data_bucket_name" {
  value = google_storage_bucket.raw_data.name
}

output "vector_data_bucket_name" {
  value = google_storage_bucket.vector_data.name
}
