variable "project" {
  description = "The GCP project ID"
  type        = string
  default     = "shikanime-studio-labs"
}

variable "name" {
  description = "The name of the project"
  type        = string
  default     = "apeiron"
}

variable "display_name" {
  description = "The display name of the project"
  type        = string
  default     = "Apeiron"
}

variable "region" {
  description = "The GCP region where resources will be created"
  type        = string
  default     = "europe-west9"
}
