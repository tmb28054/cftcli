# Installation

## Requirements

- Python 3.8 or higher
- AWS credentials configured
- pip package manager

## Install from PyPI

```bash
pip install cftcli
```

## Install from Source

```bash
git clone https://github.com/tmb28054/cftcli.git
cd cftcli
pip install -e .
```

## Install with Test Dependencies

```bash
pip install -e ".[test]"
```

## Verify Installation

```bash
deploy-stack --help
```

## AWS Configuration

Ensure your AWS credentials are configured:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_PROFILE=your-profile
export AWS_DEFAULT_REGION=us-east-1
```
