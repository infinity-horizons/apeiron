#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

output=$(tofu -chdir=infra output -json)
project=$(echo "$output" | jq -r '.project.value')
region=$(echo "$output" | jq -r '.region.value')
artifact_registry=$(echo "$output" | jq -r '.artifact_registry_repository.value')
cloudbuild_bucket=$(echo "$output" | jq -r '.bucket.value')

yq -i -y \
  ".build.artifacts[0].image = \"${region}-docker.pkg.dev/${project}/${artifact_registry}/run\"" \
  "$(dirname "$0")/skaffold.yaml"
yq -i -y \
  ".build.googleCloudBuild.bucket = \"${cloudbuild_bucket}\"" \
  "$(dirname "$0")/skaffold.yaml"
yq -i -y \
  ".deploy.cloudrun.region = \"${region}\"" \
  "$(dirname "$0")/skaffold.yaml"
