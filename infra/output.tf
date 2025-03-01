output "project" {
  description = "The project ID where resources are deployed"
  value       = var.project
}

output "region" {
  description = "The region where resources are deployed"
  value       = var.region
}

output "artifact_registry_repository" {
  description = "The Artifact Registry repository URL"
  value = google_artifact_registry_repository.default.repository_id
}

output "bucket" {
  description = "The Cloud Build artifact bucket"
  value = module.cloud_storage.name
}

output "service_account" {
  description = "The email of the service account"
  value       = module.service_accounts.email
}