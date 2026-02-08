output "run_sa_email" {
  value = google_service_account.run_sa.email
}

output "eventarc_sa_email" {
  value = google_service_account.eventarc_sa.email
}
