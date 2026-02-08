resource "google_sql_database_instance" "main" {
  name                = "main-instance"
  database_version    = "MYSQL_8_0"
  region              = "asia-northeast1"
  deletion_protection = false

  settings {
    tier = var.instance_tier
  }
}
