variable "apeiron" {
  type = object({
    google_ai_api_key = string
    mistral_api_key   = string
    discord_token     = string
  })
  description = "Apeiron application token"
  sensitive   = true
}
