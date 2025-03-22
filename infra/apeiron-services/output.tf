output "apeiron" {
  value = {
    google_ai_api_key = var.google_ai.api_key
    mistral_api_key   = var.mistral.api_key
    discord_token     = var.discord.token
  }
  sensitive = true
}

output "mlflow" {
  value = {
    access_key_id     = var.mlflow.access_key_id
    bucket            = aws_s3_bucket.mlflow_artifacts.bucket
    endpoint          = replace(var.endpoints.s3, "/http[s|]?:\\/\\//", "")
    region            = var.regions.aws_s3_bucket
    secret_access_key = var.mlflow.secret_access_key
  }
  sensitive = true
}
