terraform {
  backend "gcs" {
    bucket = "ai-hackathon-486003-tfstate"
    prefix = "terraform/state"
  }
}
