output "apeiron" {
  value = {
    google_ai_api_key = var.google_ai.api_key
    mistral_api_key   = var.mistral.api_key
    discord_token     = var.discord.token
  }
  sensitive = true
}
