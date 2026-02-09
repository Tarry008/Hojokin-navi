variable "instance_tier" {
  description = "DBのスペック"
  type        = string
}

variable "db_iam_user" {
  type = list(string)
}
