variable "repository_id" {
  type = string
}

variable "service_name" {
  description = "Cloud Runのサービス名"
  type        = string
}

variable "vertex_index_endpoint_id" {
  type = string
}

variable "run_sa_email" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "project_id" {
  type = string
}

variable "repository_url" {
  type = string
}

variable "image_name" {
  description = "コンテナイメージの名前"
  type        = string
}

variable "image_tag" {
  description = "デプロイするイメージのタグ"
  type        = string
  default     = "latest"
}

variable "secrets_db_password_id" {
  description = "シークレット内のDBパスワード"
  type        = string
}

variable "db_instance_connection_name" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_user_name" {
  type = string
}
