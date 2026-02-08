resource "google_project_iam_member" "developer_view" {
  for_each = toset(var.developer)
  project  = var.project_id
  role     = "roles/viewer"
  member   = each.value
}

# メンバー全員「Cloud Runのデプロイ」を許可
resource "google_project_iam_member" "developer_run" {
  for_each = toset(var.developer)
  project  = var.project_id
  role     = "roles/run.developer"
  member   = each.value
}

# メンバー全員に「GCSの中身の操作」を許可
resource "google_project_iam_member" "developer_storage" {
  for_each = toset(var.developer)
  project  = var.project_id
  role     = "roles/storage.objectAdmin"
  member   = each.value
}

# メンバー全員に「Cloud SQLの中身の操作」を許可
resource "google_project_iam_member" "developer_sql" {
  for_each = toset(var.developer)
  project  = var.project_id
  role     = "roles/cloudsql.editor"
  member   = each.value
}

resource "google_project_iam_member" "developer_vertex_ai" {
  for_each = toset(var.developer)
  project  = var.project_id
  role     = "roles/aiplatform.user"
  member   = each.value
}

resource "google_project_iam_member" "developer_logging" {
  for_each = toset(var.developer)
  project  = var.project_id
  role     = "roles/logging.viewer"
  member   = each.value
}
