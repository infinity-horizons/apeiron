#!/usr/bin/env bash

# Get script directory
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get Terraform outputs
project=$(tofu -chdir="${script_dir}/../infra" output -raw project)

# Update namespace in all YAML files
yq -i -y ".metadata.namespace = \"${project}\"" knative-service.yaml
