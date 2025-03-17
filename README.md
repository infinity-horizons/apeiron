# Apeiron Discord Bot

Apeiron is a Discord bot designed to enhance community engagement through
generative AI capabilities. It creates interactive and dynamic conversations by
leveraging advanced AI models to facilitate meaningful interactions within
Discord communities.

## Project Overview

The project consists of several key components:

- A Discord bot written in Python
- Infrastructure as Code using Terraform
- Cloud Run deployment configurations

## Project Structure

- `/apeiron` - Core application code for Discord bot and API
- `/infra` - Terraform infrastructure configurations
- `/manifests` - Kubernetes deployment files
- `/nix` - Development environment setup

## Setup

### Prerequisites

- Python 3.x
- Nix (for development environment)
- Kubernetes cluster
- Discord application credentials
- Mistral API key

### Environment Variables

Required environment variables:

- `DISCORD_TOKEN` - Discord application token
- `MISTRAL_API_KEY` - Mistral API key

### Local Development

1. Set up the development environment:

```bash
nix develop
```

2. Install dependencies:

```bash
uv sync
```

3. Run the application:

```bash
uvicorn --factory apeiron.app:create_app
```

## Deployment

### Nishir Cluster

1. Configure Terraform variables
2. Apply infrastructure:

```bash
terraform -chdir=infra init
terraform -chdir=infra apply
```

3. Deploy to Kubernetes:

```bash
skaffold run
```

## License

This project is licensed under the GNU Affero General Public License v3.0
(AGPL-3.0) - see the LICENSE file for details.
