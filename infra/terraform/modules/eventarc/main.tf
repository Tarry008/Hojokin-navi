resource "google_eventarc_trigger" "pdf_upload_trigger" {
  name     = "pdf-upload-trigger"
  location = "asia-northeast1"

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }

  matching_criteria {
    attribute = "bucket"
    value     = var.input_pdf_bucket_name
  }

  destination {
    cloud_run_service {
      service = var.cloud_run_service_name
      region  = "asia-northeast1"
    }
  }

  service_account = var.eventarc_sa_email
}
