variable "apeiron" {
  type = object({
    mistral_api_key = string
    discord_token   = string
  })
  description = "Apeiron application token"
  sensitive   = true
}

variable "mlflow" {
  type = object({
    access_key_id     = string
    bucket            = string
    endpoint          = string
    region            = string
    secret_access_key = string
  })
  description = "MLflow server artifacts storage"
  sensitive   = true
}
