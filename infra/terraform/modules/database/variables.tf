variable "instance_tier" {
  description = "DBのスペック"
  type        = string
}

variable "secrets_db_password" {
  type = string
}

variable "developer" {
  type = list(string)
}
