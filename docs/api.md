# API Reference

## Modules

### cftcli.utils

Shared utility functions.

#### Functions

**`set_level(verbosity: int) -> None`**

Set logging level based on verbosity.

**Parameters:**
- `verbosity`: 0-based verbosity level

**`load_file(filename: str) -> str`**

Load and return file contents.

**Parameters:**
- `filename`: Path to file

**Returns:** File contents as string

**`get_boto3_client(service: str, profile: str, region: str)`**

Create a boto3 client.

**Parameters:**
- `service`: AWS service name
- `profile`: AWS profile name
- `region`: AWS region name

**Returns:** Configured boto3 client

#### Constants

- `CACHETIME`: Cache expiration time (8 hours)
- `CACHE`: Disk cache instance

### cftcli.deploy

Stack deployment functions.

#### Functions

**`stack_exist(stackname: str) -> bool`**

Check if a stack exists.

**`find_current_stack(stacks: list) -> dict`**

Find the most recently created stack.

**`get_stack_state(stackname: str) -> str`**

Get current stack status.

**`get_inprogress_resources(stackname: str) -> list`**

Get list of resources in progress.

**`get_failed_resources(stackname: str) -> list`**

Get list of failed resources.

**`wait_for_stack(stackname: str) -> None`**

Wait for stack operation to complete.

**`load_parameters(filename: str) -> list`**

Load parameters from JSON or YAML file.

**`fill_in_current_parameters(parameters: list, stack: str) -> list`**

Fill in missing parameters with current values.

### cftcli.common

Common display functions.

#### Functions

**`display_table(records: list, title: str = 'Resources') -> None`**

Display records in a formatted table.

**Parameters:**
- `records`: List of dictionaries
- `title`: Table title

### cftcli.codebuild

CodeBuild execution functions.

#### Functions

**`s3arn_to_s3url(s3arn: str) -> str`**

Convert S3 ARN to S3 URL.

**`download_artifact(s3_arn: str, filename: str) -> str`**

Download artifact from S3.

**`watch_build(build_id: str) -> dict`**

Monitor build execution.

### cftcli.list_pipelines

Pipeline listing functions.

#### Functions

**`_get_pipeline_state(pipeline: str) -> str`**

Get pipeline execution state.

**Returns:** 'Failed', 'InProgress', or 'Succeeded'

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments

## Exceptions

All commands may raise:
- `botocore.exceptions.ClientError`: AWS API errors
- `FileNotFoundError`: Template or parameter file not found
- `ValueError`: Invalid parameter format
