#!/usr/bin/env bash

# Get Terraform outputs
project=$(tofu -chdir="$(dirname "$0")/../infra" output -raw project)
service_account=$(tofu -chdir="$(dirname "$0")/../infra" output -raw service_account)
region=$(tofu -chdir="$(dirname "$0")/../infra" output -raw region)
artifact_registry=$(tofu -chdir="$(dirname "$0")/../infra" output -json artifact_registry_repositories | jq -r '.default')

# Update namespace in all YAML files
yq -i -y ".metadata.namespace = \"${project}\"" "$(dirname "$0")/knative-service.yaml"
yq -i -y ".spec.template.spec.serviceAccountName = \"${service_account}\"" "$(dirname "$0")/knative-service.yaml"
yq -i -y ".metadata.labels.\"cloud.googleapis.com/location\" = \"${region}\"" "$(dirname "$0")/knative-service.yaml"
yq -i -y ".spec.template.spec.containers[0].image = \"${region}-docker.pkg.dev/${project}/${artifact_registry}\"" "$(dirname "$0")/knative-service.yaml"
