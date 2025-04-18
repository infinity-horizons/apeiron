variable "discord" {
  type = object({
    token = string
  })
  description = "Discord bot"
  sensitive   = true
}

variable "google_ai" {
  type = object({
    api_key = string
  })
  description = "Mistral"
  sensitive   = true
}

variable "huggingface" {
  type = object({
    token = string
  })
  description = "Hugging Face"
  sensitive   = true
}

variable "mistral" {
  type = object({
    api_key = string
  })
  description = "Mistral"
  sensitive   = true
}
