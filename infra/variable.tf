variable "project" {
  description = "The GCP project ID"
  type        = string
}

variable "name" {
  description = "The name of the project"
  type        = string
}

variable "display_name" {
  description = "The display name of the project"
  type        = string
}

variable "region" {
  description = "The GCP region where resources will be created"
  type        = string
}

variable "domain" {
  description = "The domain name"
  type        = string
}

variable "zone" {
  description = "The Cloudflare zone ID"
  type        = string
}
