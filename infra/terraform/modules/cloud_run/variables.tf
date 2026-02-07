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

variable "vpc_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "project_id" {
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
