#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# Create .env file from terraform outputs
if [ -f "$(dirname "$0")/infra/apeiron/terraform.tfvars.json" ]; then
  output=$(tofu -chdir="$(dirname "$0")/infra/apeiron-services" output -json)
  echo "MISTRAL_API_KEY=$(jq -r '.apeiron.value.mistral_api_key' <<<"$output")" >"$(dirname "$0")/.env"
  echo "DISCORD_TOKEN=$(jq -r '.apeiron.value.discord_token' <<<"$output")" >>"$(dirname "$0")/.env"
  chmod 600 "$(dirname "$0")/.env"
fi

for dir in "$(dirname "$0")"/infra/*; do
  if [ -f "$dir/install.sh" ]; then
    bash "$dir/install.sh" 2>&1 |
      sed "s/^/[$(basename "$dir")] /" &
  fi
done

wait
