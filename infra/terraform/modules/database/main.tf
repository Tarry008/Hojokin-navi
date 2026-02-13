resource "google_sql_database_instance" "main" {
  name                = "main-instance"
  database_version    = "MYSQL_8_0"
  region              = "asia-northeast1"
  deletion_protection = false

  settings {
    tier = var.instance_tier

    database_flags {
      name  = "cloudsql_iam_authentication"
      value = "on"
    }
  }
}

resource "google_sql_database" "main_db" {
  name     = "hojokin_db"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "users" {
  name     = "backend_user"
  instance = google_sql_database_instance.main.name
  password = var.secrets_db_password
  host     = "%"
}

resource "google_sql_user" "iam_user" {
  for_each = toset(var.developer)
  name     = replace(each.value, "user:", "")
  instance = google_sql_database_instance.main.name
  type     = "CLOUD_IAM_USER"
}
