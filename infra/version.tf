terraform {
  required_version = "~> 1.8"
  cloud {
    hostname     = "app.terraform.io"
    organization = "shikanime-studio"
    workspaces {
      name = "apeiron"
    }
  }
  required_providers {
    cloudflare = {
      source = "cloudflare/cloudflare"
      version = "~> 5.1"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 6.22"
    }
  }
}
