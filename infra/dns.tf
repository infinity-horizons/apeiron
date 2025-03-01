resource "cloudflare_dns_record" "default" {
  zone_id  = var.zone
  comment  = "Managed by Terraform"
  content  = "ghs.googlehosted.com."
  name     = var.name
  proxied  = true
  ttl      = 1
  type     = "CNAME"
}