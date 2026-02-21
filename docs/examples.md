# Examples

## Basic Stack Deployment

Deploy a simple stack:

```bash
deploy-stack --stack my-app-stack --filename app-template.yaml
```

## Stack with Parameters

### Using Command Line Parameters

```bash
deploy-stack \
  --stack web-app \
  --filename web-template.yaml \
  --parameters "Environment=prod,InstanceType=t3.large,KeyName=prod-key"
```

### Using Parameter File

Create `params.json`:
```json
{
  "Environment": "production",
  "InstanceType": "t3.large",
  "KeyName": "prod-key",
  "VpcId": "vpc-12345678"
}
```

Deploy:
```bash
deploy-stack -s web-app -f web-template.yaml --parameter-file params.json
```

## Stack with IAM Role

```bash
deploy-stack \
  --stack secure-stack \
  --filename template.yaml \
  --role arn:aws:iam::123456789012:role/CloudFormationRole
```

## Protected Stack

Create a stack with termination protection:

```bash
deploy-stack \
  --stack critical-stack \
  --filename template.yaml \
  --protected
```

## Stack with Rollback on Failure

```bash
deploy-stack \
  --stack test-stack \
  --filename template.yaml \
  --failure ROLLBACK
```

## Multi-Region Deployment

Deploy to different regions:

```bash
# US East
deploy-stack -s app-east -f template.yaml --region us-east-1

# US West
deploy-stack -s app-west -f template.yaml --region us-west-2

# EU
deploy-stack -s app-eu -f template.yaml --region eu-west-1
```

## Stack Management Workflow

### Development Workflow

```bash
# Create dev stack
deploy-stack -s dev-app -f template.yaml -i "Env=dev" -p dev

# Monitor changes
attach-stack -s dev-app -p dev

# Check status
describe-stack dev-app -p dev

# Delete when done
delete-stack -s dev-app -p dev
```

### Production Workflow

```bash
# Lock production stack
lock-stack -s prod-app -p prod

# Update with protection
deploy-stack -s prod-app -f template.yaml --protected -p prod

# Verify deployment
describe-stack prod-app -p prod

# Unlock if needed
unlock-stack -s prod-app -p prod
```

## Pipeline Monitoring

List all pipelines and their status:

```bash
list-pipelines --region us-east-1
```

## CodeBuild Execution

### Simple Build

```bash
codebuild \
  --codebuild my-build-project \
  --buildspec buildspec.yml
```

### Build with Artifacts

```bash
codebuild \
  --codebuild my-build \
  --buildspec buildspec.yml \
  --bucket my-artifacts-bucket \
  --dst-artifact build-output.zip
```

### Build with Source Artifact

```bash
codebuild \
  --codebuild my-build \
  --buildspec buildspec.yml \
  --src-artifact s3://my-bucket/source.zip \
  --dst-artifact output.zip \
  --bucket my-artifacts-bucket
```

## Stack Policy Management

### View Current Policy

```bash
stack-policy --stack my-stack
```

### Lock Stack

```bash
lock-stack --stack production-stack
```

### Unlock Stack

```bash
unlock-stack --stack production-stack
```

## Listing and Describing

### List All Stacks

```bash
list-stacks
```

### Describe Multiple Stacks

```bash
describe-stack stack1 stack2 stack3
```

### Describe with Verbose Output

```bash
describe-stack my-stack -vv
```

## Error Handling

### Stack Creation with Delete on Failure

```bash
deploy-stack \
  --stack test-stack \
  --filename template.yaml \
  --failure DELETE
```

### Verbose Debugging

```bash
deploy-stack \
  --stack debug-stack \
  --filename template.yaml \
  -vvv
```
