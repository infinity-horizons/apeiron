output "apeiron" {
  value = {
    mistral_api_key = var.mistral.api_key
    discord_token   = var.discord.token
  }
  sensitive   = true
}
