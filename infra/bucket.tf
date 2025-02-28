resource "google_storage_bucket" "cloudbuild" {
  project                     = var.project
  name                        = "${var.project}-europe-west9-cloudbuild"
  location                    = "europe-west9"
  uniform_bucket_level_access = true
}