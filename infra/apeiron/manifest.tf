resource "local_file" "infinity-horizons" {
  filename = "${path.module}/.terraform/tmp/manifest/infinity-horizons.yaml"
  content = templatefile("${path.module}/templates/manifests/infinity-horizons.yaml.tftpl", {
    mistral_api_key = var.apeiron.mistral_api_key
    discord_token   = var.apeiron.discord_token
  })
  file_permission = "0600"
}

resource "terraform_data" "addons" {
  triggers_replace = {
    infinity-horizons_id = local_file.infinity-horizons.id
  }

  connection {
    type = "ssh"
    user = "root"
    host = "nishir"
  }

  provisioner "file" {
    content     = local_file.infinity-horizons.content
    destination = "/mnt/nishir/rancher/k3s/server/manifests/infinity-horizons.yaml"
  }
}
