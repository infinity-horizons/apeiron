variable "apeiron" {
  type = object({
    mistral_api_key = string
    discord_token   = string
  })
  description = "Apeiron application token"
  sensitive   = true
}
