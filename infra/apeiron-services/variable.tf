variable "mistral" {
  type = object({
    api_key = string
  })
  description = "Mistral"
  sensitive   = true
}

variable "discord" {
  type        = object({
    token = string
  })
  description = "Discord bot"
  sensitive   = true
}
