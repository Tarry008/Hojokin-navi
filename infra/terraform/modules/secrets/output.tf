output "db_password_value" {
  description = "DBユーザー作成時に使用するパスワード文字列"
  value       = random_password.db_password.result
  sensitive   = true
}

output "db_password_id" {
  description = "Cloud Runの環境変数用"
  value       = google_secret_manager_secret.db_password.id
}
