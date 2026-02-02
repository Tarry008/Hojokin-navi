variable "project_id" {
  type        = string
  description = "GCP project id"
}

variable "region" {
  type        = string
  description = "GCP region"
  default     = "asia-northeast1"
}

variable "firestore_location" {
  type        = string
  description = "Firestore location"
  default     = "asia-northeast1"
}

variable "storage_bucket" {
  type        = string
  description = "Cloud Storage bucket name"
}

variable "cloud_run_service" {
  type        = string
  description = "Cloud Run service name"
  default     = "grant-rag-api"
}

variable "container_image" {
  type        = string
  description = "Container image URL (gcr.io/... or artifact registry)"
}