resource "google_sql_database_instance" "main" {
  name             = "main-instance"
  database_version = "POSTGRES_15"
  region           = "asia-northeast1"

  settings {
    tier = var.instance_tier
  }
}
