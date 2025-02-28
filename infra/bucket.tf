module "cloud_storage" {
  source  = "terraform-google-modules/cloud-storage/google"
  version = "~> 9.1"

  project_id = var.project
  names      = ["cloudbuild"]
  prefix     = "${var.project}-europe-west9"
  location   = "europe-west9"
}