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
    google_ai_api_key = var.apeiron.google_ai_api_key
    mistral_api_key   = var.apeiron.mistral_api_key
    discord_token     = var.apeiron.discord_token
  }
  type = "Opaque"
}

resource "kubernetes_secret" "mlflow" {
  metadata {
    name      = "mlflow"
    namespace = kubernetes_namespace.infinity_horizons.metadata[0].name
  }
  data = {
    access_key_id     = var.mlflow.access_key_id
    region            = var.mlflow.region
    secret_access_key = var.mlflow.secret_access_key
  }
  type = "Opaque"
}

resource "kubernetes_config_map" "mlflow" {
  metadata {
    name      = "mlflow"
    namespace = kubernetes_namespace.infinity_horizons.metadata[0].name
  }
  data = {
    artifacts_destination = "s3://${var.mlflow.bucket}/"
    s3_endpoint_url       = "https://${var.mlflow.endpoint}"
  }
}
