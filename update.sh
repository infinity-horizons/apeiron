#!/bin/bash

# Get Terraform outputs
project=$(tofu -chdir=infra output -raw project)
region=$(tofu -chdir=infra output -raw region)
artifact_registry=$(tofu -chdir=infra output -json artifact_registry_repositories | jq -r '.default')
cloudbuild_bucket=$(tofu -chdir=infra output -json buckets | jq -r '.cloudbuild')

# Update Skaffold configuration
yq -i -y \
  ".build.artifacts[0].image = \"${region}-docker.pkg.dev/${project}/${artifact_registry}/run\"" \
  "$(dirname "$0")/skaffold.yaml"
yq -i -y \
  ".build.googleCloudBuild.bucket = \"${cloudbuild_bucket}\"" \
  "$(dirname "$0")/skaffold.yaml"
yq -i -y \
  ".deploy.cloudrun.region = \"${region}\"" \
  "$(dirname "$0")/skaffold.yaml"
