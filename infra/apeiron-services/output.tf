output "apeiron" {
  value = {
    discord_token     = var.discord.token
    google_ai_api_key = var.google_ai.api_key
    huggingface_token = var.huggingface.token
    mistral_api_key   = var.mistral.api_key
  }
  sensitive = true
}
