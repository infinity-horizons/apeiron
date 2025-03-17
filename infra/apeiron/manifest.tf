resource "kubernetes_namespace" "infinity_horizons" {
  metadata {
    name = "infinity-horizons"
  }
}

resource "kubernetes_secret" "apeiron" {
  metadata {
    name      = "apeiron"
    namespace = kubernetes_namespace.infinity_horizons.metadata[0].name
  }
  data = {
    mistral_api_key = var.apeiron.mistral_api_key
    discord_token   = var.apeiron.discord_token
  }
  type = "Opaque"
}

resource "kubernetes_secret" "mlflow" {
  metadata {
    name      = "mlflow"
    namespace = kubernetes_namespace.infinity_horizons.metadata[0].name
  }
  data = {
    access_key_id     = var.mlflow_server.access_key_id
    region            = var.mlflow_server.region
    secret_access_key = var.mlflow_server.secret_access_key
  }
  type = "Opaque"
}

resource "kubernetes_config_map" "mlflow" {
  metadata {
    name      = "mlflow"
    namespace = kubernetes_namespace.infinity_horizons.metadata[0].name
  }
  data = {
    artifacts_destination = "s3://${var.mlflow_server.bucket}/"
    s3_endpoint_url       = "https://${var.mlflow_server.endpoint}"
  }
}
