# サービスアカウントの作成
resource "google_service_account" "run_sa" {
  account_id   = "cloud-run-app-sa"
  display_name = "Cloud Run Application Service Account"
}

resource "google_service_account" "eventarc_sa" {
  account_id   = "eventarc-sa"
  display_name = "Eventarc Service Account"
}
