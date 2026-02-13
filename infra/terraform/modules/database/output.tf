output "db_instance_connection_name" {
  value = google_sql_database_instance.main.connection_name
}

output "db_name" {
  value = google_sql_database.main_db.name
}

output "db_user_name" {
  value = google_sql_user.users.name
}
