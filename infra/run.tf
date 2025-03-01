resource "google_cloud_run_service" "default" {
  project  = var.project
  name     = var.name
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/cloudrun/hello"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].spec[0].containers[0].image,
      template[0].spec[0].containers[0].env
    ]
  }
}

resource "google_cloud_run_service_iam_member" "default" {
  location = google_cloud_run_service.default.location
  project  = google_cloud_run_service.default.project
  service  = google_cloud_run_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_domain_mapping" "default" {
  location = google_cloud_run_service.default.location
  project  = google_cloud_run_service.default.project
  name     = var.domain

  metadata {
    namespace = google_cloud_run_service.default.project
  }

  spec {
    route_name = google_cloud_run_service.default.name
  }
}