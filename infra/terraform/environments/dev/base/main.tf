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

data "google_project" "project" {}

module "database" {
  source        = "../../../modules/database"
  instance_tier = "db-f1-micro"
}

module "network" {
  source   = "../../../modules/network"
  vpc_name = "network-dev"
}

module "storage" {
  source     = "../../../modules/storage"
  project_id = var.project_id
}

module "artifact_registry" {
  source        = "../../../modules/artifact"
  repository_id = "dev-app-repo"
  project_id    = var.project_id
}

module "sa_creation" {
  source = "../../../modules/sa_creation"
}
