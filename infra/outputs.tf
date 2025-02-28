output "project" {
  description = "The project ID where resources are deployed"
  value       = var.project
}

output "region" {
  description = "The region where resources are deployed"
  value       = "europe-west9"
}

output "artifact_registry_repositories" {
  description = "The Artifact Registry repository URL"
  value = {
    default = google_artifact_registry_repository.default.repository_id
  }
}

output "buckets" {
  description = "The Cloud Build artifact bucket"
  value = {
    cloudbuild = google_storage_bucket.cloudbuild.name
  }
}