#!/usr/bin/env bash

# Get Terraform outputs
project=$(tofu -chdir="$(dirname "$0")/infra" output -raw project)
artifact_registry="$(tofu -chdir="$(dirname "$0")/infra" output -json artifact_registry_repositories | jq -r '.default')/run"
cloudbuild_bucket=$(tofu -chdir="$(dirname "$0")/infra" output -json buckets | jq -r '.cloudbuild')

# Update Skaffold configuration
yq -i -y ".build.artifacts[0].image = \"${region}-docker.pkg.dev/${project}/${artifact_registry}\"" "$(dirname "$0")/skaffold.yaml"
yq -i -y ".build.googleCloudBuild.bucket = \"${cloudbuild_bucket}\"" "$(dirname "$0")/skaffold.yaml"

# Update Kubernetes manifests
bash "$(dirname "$0")/manifests/update.sh" 2>&1 |
    sed "s/^/[manifests] /"
