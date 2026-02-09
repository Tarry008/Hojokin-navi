resource "google_vertex_ai_index" "rag_index" {
  region       = "asia-northeast1"
  display_name = var.index_storage_name

  metadata {
    contents_delta_uri = "gs://${var.vector_bucket_name}/embeddings"

    config {
      dimensions                  = 768
      approximate_neighbors_count = 150
      shard_size                  = "SHARD_SIZE_SMALL"
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

  network                 = "projects/${var.project_number}/global/networks/${var.vpc_name}"
  public_endpoint_enabled = false
}

resource "google_vertex_ai_index_endpoint_deployed_index" "rag_deployed_index" {
  index_endpoint    = google_vertex_ai_index_endpoint.rag_endpoint.id
  index             = google_vertex_ai_index.rag_index.id
  deployed_index_id = "rag_deployed_index_id"

  dedicated_resources {
    machine_spec {
      machine_type = var.machine_type
    }
    min_replica_count = 1
    max_replica_count = 1
  }
}
