variable "apeiron" {
  type = object({
    discord_token = string
  })
  description = "Apeiron application token"
  sensitive   = true
}
