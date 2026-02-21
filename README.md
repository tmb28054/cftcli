# Welcome to **CFT CLI**

CLI commands to ease the interaction with CloudFormation while developing and testing CloudFormation Stacks.

## Installation

```bash
pip install cftcli
```

## Quick Start

```bash
# Deploy a stack
deploy-stack --stack my-stack --filename template.yaml

# List stacks
list-stacks

# Describe a stack
describe-stack my-stack

# Delete a stack
delete-stack --stack my-stack
```

## Commands

- **deploy-stack**: Create or update a stack
- **delete-stack**: Delete a stack
- **list-stacks**: List all stacks in a region
- **describe-stack**: Display stack details
- **attach-stack**: Monitor stack changes in real-time
- **lock-stack**: Apply stack policy and termination protection
- **unlock-stack**: Remove stack policy restrictions
- **stack-policy**: Display current stack policy
- **list-pipelines**: List all pipelines in a region
- **codebuild**: Execute a CodeBuild project

## Documentation

Complete documentation is available in the [docs/](docs/) folder:

- [Installation Guide](docs/installation.md)
- [Quick Start](docs/quickstart.md)
- [Commands Reference](docs/commands.md)
- [Configuration](docs/configuration.md)
- [Examples](docs/examples.md)
- [API Reference](docs/api.md)

## License

Apache License 2.0
