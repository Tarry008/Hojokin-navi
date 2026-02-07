# プロバイダ設定
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.8.0"
    }
  }
}

# Google Cloud プロバイダの設定
provider "google" {
  project = var.project_id
  region  = "asia-northeast1"
  zone    = "asia-northeast1-a"
}

module "database" {
  source        = "../../modules/database"
  instance_tier = "db-f1-micro"
}

module "network" {
  source   = "../../modules/network"
  vpc_name = "network-dev"
}

module "storage" {
  source     = "../../modules/storage"
  project_id = var.project_id
}

module "cloud_run" {
  source                   = "../../modules/cloud_run"
  repository_id            = "dev-ai-app-repoo"
  service_name             = "cloudrun-dev"
  vertex_index_endpoint_id = module.ai_service.google_vertex_ai_index_endpoint
  vpc_id                   = module.network.vpc_id
  subnet_id                = module.network.subnet_id
  project_id               = var.project_id
  image_name               = "dev-ai-app-image"
}

module "ai_service" {
  source                          = "../../modules/ai_service"
  index_storage_name              = "dev_index_storage"
  rag_endpoint_name               = "dev_rag_endpoint_name"
  project_id                      = var.project_id
  vpc_id                          = module.network.vpc_id
  cloud_run_service_account_email = module.cloud_run.cloud_run_service_account_email
  raw_bucket_name                 = module.storage.raw_data_bucket_name
  vector_bucket_name              = module.storage.vector_data_bucket_name
}
