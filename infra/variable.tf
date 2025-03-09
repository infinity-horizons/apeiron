variable "discord" {
  type = object({
    token = string
  })
  description = "Discord application token"
  sensitive   = true
}
