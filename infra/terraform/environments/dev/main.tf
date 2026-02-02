module "database" {
  source        = "../../modules/database"
  instance_tier = "db-f1-micro"
}
