terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.8.0"
    }
  }
}

provider "google" {
  project = "ai-hackathon-dev"
  region  = "asia-northeast1"
  zone    = "asia-northeast1-a"
}

module "database" {
  source        = "../../modules/database"
  instance_tier = ""
}

module "network" {
  source   = "../../modules/network"
  vpc_name = ""
}
