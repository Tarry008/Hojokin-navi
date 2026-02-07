variable "index_storage_name" {
  description = "Index Storageの名称"
  type        = string
}

variable "rag_endpoint_name" {
  description = "Rag Endpointの名称"
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "cloud_run_service_account_email" {
  description = "Cloud Runが使用するサービスアカウントのメールアドレス"
  type        = string
}

variable "project_id" {
  type = string
}

variable "raw_bucket_name" {
  type = string
}

variable "vector_bucket_name" {
  type = string
}
