variable "developer" {
  description = "開発チームのメンバーリスト（user:email 形式）"
  type        = list(string)
}

variable "project_id" {
  type = string
}
