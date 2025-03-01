resource "google_secret_manager_secret" "github_webhook_secret" {
  project   = var.project
  secret_id = "${var.name}-github-webhook-secret"
  replication {
    auto {}
  }
}

resource "random_password" "github_webhook_secret" {
  length  = 32
  special = true
}

resource "google_secret_manager_secret_version" "github_webhook_secret" {
  secret      = google_secret_manager_secret.github_webhook_secret.id
  secret_data = random_password.github_webhook_secret.result
}
