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
