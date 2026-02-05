output "vpc_connector_id" {
  description = "Cloud RunがVPCに接続するためのコネクタID"
  value       = google_vpc_access_connector.connector.id
}
