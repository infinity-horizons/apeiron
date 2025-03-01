#!/usr/bin/env bash

output=$(tofu -chdir="$(dirname "$0")/../infra" output -json)
project=$(echo "$output" | jq -r '.project.value')
service_account=$(echo "$output" | jq -r '.service_account.value')
region=$(echo "$output" | jq -r '.region.value')
artifact_registry=$(echo "$output" | jq -r '.artifact_registry_repositories.value.default')

yq -i -y \
  ".metadata.namespace = \"${project}\"" \
  "$(dirname "$0")/knative-service.yaml"
yq -i -y \
  ".spec.template.spec.serviceAccountName = \"${service_account}\"" \
  "$(dirname "$0")/knative-service.yaml"
yq -i -y \
  ".metadata.labels.\"cloud.googleapis.com/location\" = \"${region}\"" \
  "$(dirname "$0")/knative-service.yaml"
yq -i -y \
  ".spec.template.spec.containers[0].image = \"${region}-docker.pkg.dev/${project}/${artifact_registry}/run\"" \
  "$(dirname "$0")/knative-service.yaml"
