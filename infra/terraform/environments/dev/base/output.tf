output "repository_url" {
  description = "Artifact RegistryのベースURL"
  value       = "${module.artifact_registry.repository_location}-docker.pkg.dev/${var.project_id}/${module.artifact_registry.repository_id}"
}

output "repository_id" {
  value = module.artifact_registry.repository_id
}

output "repository_location" {
  value = module.artifact_registry.repository_location
}

output "run_sa_email" {
  description = "Cloud Runに割りあてるサービスアカウントのメールアドレス"
  value       = module.sa_creation.run_sa_email
}

output "eventarc_sa_email" {
  value = module.sa_creation.eventarc_sa_email
}

output "vpc_name" {
  value = module.network.vpc_name
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "subnet_id" {
  value = module.network.subnet_id
}

output "project_number" {
  value = data.google_project.project.number
}

output "raw_bucket_name" {
  value = module.storage.raw_data_bucket_name
}

output "vector_bucket_name" {
  value = module.storage.vector_data_bucket_name
}

output "secret_db_password_id" {
  value = module.secrets.db_password_id
}

output "db_instance_connection_name" {
  value = module.database.db_instance_connection_name
}

output "db_name" {
  value = module.database.db_name
}

output "db_user_name" {
  value = module.database.db_user_name
}
