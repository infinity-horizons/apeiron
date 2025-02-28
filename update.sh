#!/usr/bin/env bash

# Get script directory
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get Terraform outputs
project=$(tofu -chdir="${script_dir}/infra" output -raw project)
region=$(tofu -chdir="${script_dir}/infra" output -raw region)
artifact_registry=$(tofu -chdir="${script_dir}/infra" output -json artifact_registry_repositories | jq -r '.default')
cloudbuild_bucket=$(tofu -chdir="${script_dir}/infra" output -json buckets | jq -r '.cloudbuild')

# Update Skaffold configuration
yq -i -y ".build.artifacts[0].image = \"${region}-docker.pkg.dev/${project}/${artifact_registry}\"" skaffold.yaml
yq -i -y ".build.googleCloudBuild.bucket = \"${cloudbuild_bucket}\"" skaffold.yaml
yq -i -y ".deploy.cloudrun.region = \"${region}\"" skaffold.yaml

# Update Kubernetes manifests
bash "manifests/update.sh" 2>&1 |
    sed "s/^/[manifests] /"
