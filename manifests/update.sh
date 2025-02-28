#!/usr/bin/env bash

# Get Terraform outputs
project=$(tofu -chdir="$(dirname "$0")/../infra" output -raw project)
service_account=$(tofu -chdir="$(dirname "$0")/../infra" output -raw service_account)

# Update namespace in all YAML files
yq -i -y ".metadata.namespace = \"${project}\"" "$(dirname "$0")/knative-service.yaml"
yq -i -y ".spec.template.spec.serviceAccountName = \"${service_account}\"" "$(dirname "$0")/knative-service.yaml"
