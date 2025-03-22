variable "project" {
  type        = string
  description = "Project name"
  default     = "shikanime-studio"
}

variable "name" {
  type        = string
  description = "Name of the cluster"
  default     = "apeiron"
}

variable "regions" {
  type = object({
    aws_s3_bucket = string
  })
  description = "Resource regions"
  default = {
    aws_s3_bucket = "fsn1"
  }
}

variable "endpoints" {
  type = object({
    s3 = string
  })
  description = "Resource API endpoints"
  default = {
    s3 = "https://fsn1.your-objectstorage.com"
  }
}

variable "mistral" {
  type = object({
    api_key = string
  })
  description = "Mistral"
  sensitive   = true
}

variable "google_ai" {
  type = object({
    api_key = string
  })
  description = "Mistral"
  sensitive   = true
}

variable "discord" {
  type = object({
    token = string
  })
  description = "Discord bot"
  sensitive   = true
}

variable "mlflow" {
  type = object({
    access_key_id     = string
    secret_access_key = string
  })
  sensitive = true
}
