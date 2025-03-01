#!/usr/bin/env bash

output=$(tofu -chdir="$(dirname "$0")/infra" output -json)
project=$(echo "$output" | jq -r '.project.value')
region=$(echo "$output" | jq -r '.region.value')
artifact_registry="$(echo "$output" | jq -r '.artifact_registry_repositories.value.default')/run"
cloudbuild_bucket=$(echo "$output" | jq -r '.buckets.value.cloudbuild')

yq -i -y \
  ".build.artifacts[0].image = \"${region}-docker.pkg.dev/${project}/${artifact_registry}\"" \
  "$(dirname "$0")/skaffold.yaml"
yq -i -y \
  ".build.googleCloudBuild.bucket = \"${cloudbuild_bucket}\"" \
  "$(dirname "$0")/skaffold.yaml"
yq -i -y \
  ".deploy.cloudrun.region = \"${region}\"" \
  "$(dirname "$0")/skaffold.yaml"

# Update Kubernetes manifests
bash "$(dirname "$0")/manifests/update.sh" 2>&1 |
  sed "s/^/[manifests] /"
