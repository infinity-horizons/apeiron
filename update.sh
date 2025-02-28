#!/bin/bash

# Get Terraform outputs
project=$(tofu -chdir=infra output -raw project)
region=$(tofu -chdir=infra output -raw region)
artifact_registry=$(tofu -chdir=infra output -json artifact_registry_repositories | jq -r '.default')
cloudbuild_bucket=$(tofu -chdir=infra output -json buckets | jq -r '.cloudbuild')

# Update Skaffold configuration
yq -i -y ".build.artifacts[0].image = \"${region}-docker.pkg.dev/${project}/${artifact_registry}\"" skaffold.yaml
yq -i -y ".build.googleCloudBuild.projectId = \"${project}\"" skaffold.yaml
yq -i -y ".build.googleCloudBuild.bucket = \"${cloudbuild_bucket}\"" skaffold.yaml
yq -i -y ".deploy.cloudrun.projectid = \"${project}\"" skaffold.yaml
yq -i -y ".deploy.cloudrun.region = \"${region}\"" skaffold.yaml
