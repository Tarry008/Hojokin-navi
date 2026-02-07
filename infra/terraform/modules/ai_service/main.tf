resource "google_vertex_ai_index" "rag_index" {
  region       = "asia-northeast1"
  display_name = var.index_storage_name

  metadata {
    contents_delta_uri = "gs://${var.vector_bucket_name}/embeddings"
    config {
      dimensions                  = 768
      approximate_neighbors_count = 150
      algorithm_config {
        tree_ah_config {
          leaf_node_embedding_count    = 500
          leaf_nodes_to_search_percent = 7
        }
      }
    }
  }
  index_update_method = "STREAM_UPDATE"
}

resource "google_vertex_ai_index_endpoint" "rag_endpoint" {
  display_name = var.rag_endpoint_name
  region       = "asia-northeast1"

  network                 = var.vpc_id
  public_endpoint_enabled = false
}
