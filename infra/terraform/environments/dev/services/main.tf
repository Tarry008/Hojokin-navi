terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.8.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "asia-northeast1"
  zone    = "asia-northeast1-a"
}

data "terraform_remote_state" "base" {
  backend = "gcs"

  config = {
    bucket = "${var.project_id}-tfstate"
    prefix = "terraform/dev/base"
  }
}

module "sa_iam" {
  source                 = "../../../modules/sa_iam"
  project_id             = var.project_id
  run_sa_email           = data.terraform_remote_state.base.outputs.run_sa_email
  eventarc_sa_email      = data.terraform_remote_state.base.outputs.eventarc_sa_email
  repository_location    = data.terraform_remote_state.base.outputs.repository_location
  repository_id          = data.terraform_remote_state.base.outputs.repository_id
  raw_bucket_name        = data.terraform_remote_state.base.outputs.raw_bucket_name
  vector_bucket_name     = data.terraform_remote_state.base.outputs.vector_bucket_name
  cloud_run_service_name = module.cloud_run.cloud_run_service_name
}

module "cloud_run" {
  source                   = "../../../modules/cloud_run"
  service_name             = "cloudrun-dev"
  repository_id            = data.terraform_remote_state.base.outputs.repository_id
  vpc_id                   = data.terraform_remote_state.base.outputs.vpc_id
  subnet_id                = data.terraform_remote_state.base.outputs.subnet_id
  run_sa_email             = data.terraform_remote_state.base.outputs.run_sa_email
  project_id               = var.project_id
  vertex_index_endpoint_id = module.ai_service.google_vertex_ai_index_endpoint
  image_name               = "dev-ai-app-image"
  repository_url           = data.terraform_remote_state.base.outputs.repository_url
}

module "ai_service" {
  source             = "../../../modules/ai_service"
  index_storage_name = "dev_index_storage"
  rag_endpoint_name  = "dev_rag_endpoint_name"
  project_id         = var.project_id
  project_number     = data.terraform_remote_state.base.outputs.project_number
  vpc_id             = data.terraform_remote_state.base.outputs.vpc_id
  vector_bucket_name = data.terraform_remote_state.base.outputs.vector_bucket_name
  machine_type       = "n1-standard-2"
}

module "eventarc" {
  source                 = "../../../modules/eventarc"
  input_pdf_bucket_name  = module.storage.raw_data_bucket_name
  cloud_run_service_name = module.cloud_run.service_name
  eventarc_sa_email      = module.service_account.eventarc_sa_email
}
