# Commands Reference

## Stack Management

### deploy-stack / create-stack / update-stack

Create or update a CloudFormation stack.

```bash
deploy-stack --stack STACK_NAME --filename TEMPLATE_FILE [OPTIONS]
```

**Options:**
- `--stack, -s`: Stack name (required)
- `--filename, -f`: CloudFormation template file (required)
- `--parameters, -i`: Comma-delimited parameters (e.g., `Key1=Value1,Key2=Value2`)
- `--parameter-file`: JSON or YAML file with parameters
- `--profile, -p`: AWS profile (default: default)
- `--region`: AWS region (default: us-east-1)
- `--role, -r`: IAM role ARN for stack operations
- `--failure`: On failure action: DO_NOTHING, ROLLBACK, DELETE (default: DO_NOTHING)
- `--protected`: Enable termination protection
- `--verbose, -v`: Increase verbosity

**Aliases:** `create-stack`, `update-stack`, `cfdeploy`

### delete-stack

Delete a CloudFormation stack.

```bash
delete-stack --stack STACK_NAME [OPTIONS]
```

**Options:**
- `--stack, -s`: Stack name (required)
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--role, -r`: IAM role ARN
- `--verbose, -v`: Increase verbosity

### list-stacks

List all CloudFormation stacks in a region.

```bash
list-stacks [OPTIONS]
```

**Options:**
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--verbose, -v`: Increase verbosity

### describe-stack / stack-detail

Display detailed information about a stack.

```bash
describe-stack STACK_NAME [OPTIONS]
```

**Options:**
- `STACK_NAME`: One or more stack names (positional)
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--verbose, -v`: Increase verbosity

**Alias:** `stack-detail`

### attach-stack

Attach to a stack and monitor its changes in real-time.

```bash
attach-stack --stack STACK_NAME [OPTIONS]
```

**Options:**
- `--stack, -s`: Stack name (required)
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--verbose, -v`: Increase verbosity

## Stack Policy Management

### lock-stack

Apply a deny-all policy and enable termination protection.

```bash
lock-stack --stack STACK_NAME [OPTIONS]
```

**Options:**
- `--stack, -s`: Stack name (required)
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--verbose, -v`: Increase verbosity

### unlock-stack

Remove stack policy restrictions and disable termination protection.

```bash
unlock-stack --stack STACK_NAME [OPTIONS]
```

**Options:**
- `--stack, -s`: Stack name (required)
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--verbose, -v`: Increase verbosity

### stack-policy

Display the current stack policy.

```bash
stack-policy --stack STACK_NAME [OPTIONS]
```

**Options:**
- `--stack, -s`: Stack name (required)
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--verbose, -v`: Increase verbosity

## Pipeline Management

### list-pipelines / list-pipeline

List all CodePipeline pipelines with their current status.

```bash
list-pipelines [OPTIONS]
```

**Options:**
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--verbose, -v`: Increase verbosity

**Alias:** `list-pipeline`

## CodeBuild

### codebuild

Execute a CodeBuild project.

```bash
codebuild --codebuild PROJECT_NAME --buildspec BUILDSPEC_FILE [OPTIONS]
```

**Options:**
- `--codebuild, --project`: CodeBuild project name (required)
- `--buildspec, -b`: Buildspec file path (required)
- `--src-artifact, -s`: Source artifact S3 location
- `--dst-artifact, -d`: Destination artifact filename
- `--bucket`: S3 bucket for artifacts
- `--bucket-path`: S3 path prefix (default: cftcli)
- `--rolearn, -r`: IAM role ARN
- `--profile, -p`: AWS profile
- `--region`: AWS region
- `--verbose, -v`: Increase verbosity

## Secrets Manager

### secretsmanager-env

Read an AWS Secrets Manager secret and output shell export statements.

```bash
secretmanager-env SECRET_ARN [OPTIONS]
```

**Options:**
- `SECRET_ARN`: The ARN of the secret to retrieve (required)
- `--profile, -p`: AWS profile
- `--region`: AWS region

**Usage:**

```bash
# Print export statements
secretmanager-env arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret

# Source directly into current shell
source <(secretmanager-env arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret)

# With profile and region
source <(secretmanager-env $SECRET_ARN --profile prod --region us-east-1)
```

Given a secret `{"DB_HOST": "localhost", "DB_PASS": "s3cr3t"}`, the output will be:

```bash
export DB_HOST='localhost'
export DB_PASS='s3cr3t'
```
