resource "google_sql_user" "iam_user" {
  for_each = toset(var.db_iam_user)
  name     = replace(each.value, "user:", "")
  instance = google_sql_database_instance.main.name
  type     = "CLOUD_IAM_USER"
}
