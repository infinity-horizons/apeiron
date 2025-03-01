resource "google_artifact_registry_repository" "default" {
  project       = var.project
  location      = "europe-west9"
  repository_id = var.name
  description   = "Container registry for ${var.display_name}"
  format        = "DOCKER"
}
