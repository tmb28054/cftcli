# Configuration

## Environment Variables

CFT CLI respects the following environment variables:

### AWS Configuration

- `AWS_PROFILE`: Default AWS profile to use
- `AWS_DEFAULT_REGION`: Default AWS region
- `STACKNAME`: Default stack name
- `FILENAME`: Default template filename

### CodeBuild Configuration

- `CODEBUILD`: Default CodeBuild project name
- `BUILDSPEC`: Default buildspec file path
- `ROLEARN`: Default IAM role ARN
- `BUCKET`: Default S3 bucket for artifacts
- `BUCKETPATH`: Default S3 path prefix

## Cache

CFT CLI caches frequently used values in `~/.cftcli/` to reduce repetitive typing.

Cached values include:
- AWS profile
- AWS region
- Stack name
- CodeBuild project
- Buildspec path
- Role ARN
- S3 bucket settings

Cache entries expire after 8 hours.

## AWS Credentials

CFT CLI uses standard AWS credential resolution:

1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. AWS config file (`~/.aws/config`)
4. IAM role (when running on EC2)

## Parameter Files

Parameter files can be in JSON or YAML format:

### JSON Format

```json
{
  "Environment": "production",
  "InstanceType": "t3.micro",
  "KeyName": "my-key"
}
```

### YAML Format

```yaml
Environment: production
InstanceType: t3.micro
KeyName: my-key
```

## Verbosity Levels

Use `-v` flags to increase logging verbosity:

- No flag: INFO level, boto3 at ERROR
- `-v`: INFO level, boto3 at INFO
- `-vv`: DEBUG level, boto3 at DEBUG
- `-vvv`: DEBUG level, boto3 at DEBUG

## Profiles

Use different AWS profiles for different environments:

```bash
# Development
deploy-stack -s dev-stack -f template.yaml -p dev

# Production
deploy-stack -s prod-stack -f template.yaml -p prod
```
