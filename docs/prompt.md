# CFT CLI — AI Assistant Prompt

Use this document as a reference when working with the CFT CLI project. It describes the tooling, project structure, development workflow, and conventions so you can contribute effectively.

## What Is CFT CLI

CFT CLI is a Python command-line toolkit for managing AWS CloudFormation stacks. It wraps the AWS CloudFormation, CodeBuild, CodePipeline, and Secrets Manager APIs into short, memorable commands designed for rapid iteration during stack development and testing.

Package name: `cftcli`
License: Apache 2.0
Python: 3.10+
Build system: Hatchling

## Installation

```bash
# From PyPI
pip install cftcli

# From source (editable, with test deps)
git clone https://github.com/tmb28054/cftcli.git
cd cftcli
pip install -e ".[test]"
```

Verify with `deploy-stack --help`.

## Project Layout

```
cftcli/                  # Package source
  __init__.py            # Exports __version__
  __version__.py         # Reads version from CHANGELOG.md
  utils.py               # Shared helpers: set_level, load_file, get_boto3_client,
                         #   add_common_arguments, setup_session, CACHE, CACHETIME
  common.py              # display_table() for formatted terminal output
  deploy.py              # deploy-stack / create-stack / update-stack / cfdeploy
  destroy.py             # delete-stack
  list.py                # list-stacks
  detail.py              # describe-stack / stack-detail
  attach.py              # attach-stack (real-time monitoring)
  lock.py                # lock-stack (deny-all policy + termination protection)
  unlock.py              # unlock-stack
  policy.py              # stack-policy (display current policy)
  list_pipelines.py      # list-pipelines / list-pipeline
  codebuild.py           # codebuild (run CodeBuild projects)
  secretsmanager_env.py  # secretmanager-env (export secrets as shell vars)
  buildspec.yaml         # Example buildspec for codebuild command
tests/                   # Unit tests (pytest, one file per module)
docs/                    # User-facing documentation
examples/                # Sample CloudFormation templates and parameter files
scripts/                 # CI helper scripts (build.sh, test.sh, push-github.sh)
pyproject.toml           # Build config, dependencies, CLI entry points
pytest.ini               # Test runner config with coverage
CHANGELOG.md             # Version source and release history
```

## CLI Commands at a Glance

| Command | Purpose | Key Flags |
|---|---|---|
| `deploy-stack` | Create or update a stack | `-s STACK -f TEMPLATE [-i PARAMS] [--parameter-file FILE] [--failure ACTION] [--protected] [-r ROLE]` |
| `delete-stack` | Delete a stack | `-s STACK [-r ROLE]` |
| `list-stacks` | List all stacks in a region | (none required) |
| `describe-stack` | Show stack detail, events, resources | `STACK [STACK ...]` |
| `attach-stack` | Monitor a stack operation in real-time | `-s STACK` |
| `lock-stack` | Apply deny-all policy + termination protection | `-s STACK` |
| `unlock-stack` | Remove policy + termination protection | `-s STACK` |
| `stack-policy` | Display current stack policy JSON | `-s STACK` |
| `list-pipelines` | List CodePipeline pipelines with status | (none required) |
| `codebuild` | Run a CodeBuild project | `--codebuild PROJECT -b BUILDSPEC [--bucket BUCKET] [--dst-artifact FILE]` |
| `secretmanager-env` | Print `export KEY='VALUE'` lines from a secret | `SECRET_ARN` |

All stack commands accept `--profile / -p`, `--region`, and `-v` (repeatable for verbosity).

Aliases: `create-stack`, `update-stack`, and `cfdeploy` all point to `deploy-stack`. `stack-detail` points to `describe-stack`. `list-pipeline` points to `list-pipelines`.

## Common Workflows

### Deploy a stack with inline parameters

```bash
deploy-stack -s my-app -f template.yaml -i "Env=dev,Version=1.0"
```

### Deploy with a parameter file

```bash
# params.yaml
# Environment: production
# InstanceType: t3.micro

deploy-stack -s my-app -f template.yaml --parameter-file params.yaml
```

### Monitor, inspect, then tear down

```bash
attach-stack -s my-app          # watch until complete
describe-stack my-app            # inspect detail
delete-stack -s my-app           # clean up
```

### Lock a production stack

```bash
lock-stack -s prod-app           # deny-all policy + termination protection
stack-policy -s prod-app         # verify the policy
unlock-stack -s prod-app         # remove when maintenance is needed
```

### Inject secrets into the shell

```bash
source <(secretmanager-env arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret)
```

### Run a CodeBuild project

```bash
codebuild --codebuild my-project -b buildspec.yml --bucket artifacts-bucket --dst-artifact output.zip
```

## Configuration

### Environment Variables

| Variable | Used By | Purpose |
|---|---|---|
| `AWS_PROFILE` | All commands | Default AWS profile |
| `AWS_DEFAULT_REGION` | All commands | Default AWS region |
| `STACKNAME` | deploy-stack, attach-stack | Default stack name |
| `FILENAME` | deploy-stack | Default template file |
| `CODEBUILD` | codebuild | Default CodeBuild project |
| `BUILDSPEC` | codebuild | Default buildspec path |
| `ROLEARN` | codebuild | Default IAM role ARN |
| `BUCKET` | codebuild | Default S3 artifact bucket |
| `BUCKETPATH` | codebuild | Default S3 path prefix |

### Disk Cache

Frequently used values (profile, region, stack name, codebuild settings) are cached in `~/.cftcli/` for 8 hours via `diskcache`. This means you can omit `--profile` and `--region` on subsequent calls if they haven't changed.

### Verbosity

`-v` = INFO for boto3, `-vv` = DEBUG for everything, `-vvv` = maximum debug output.

## Development Workflow

### Running Tests

```bash
pip install -e ".[test]"
python3 -m pytest tests/ -v
```

Coverage report:

```bash
python3 -m pytest tests/ --cov=cftcli --cov-report=term-missing
```

### Project Conventions

- Each CLI command lives in its own module under `cftcli/`.
- Shared logic goes in `utils.py` (session setup, logging, file I/O, cache) or `common.py` (display).
- Every module exposes a `_main()` function registered as a console script in `pyproject.toml`.
- boto3 clients are initialized as `None` at module level and created inside `_main()` after session setup.
- Tests live in `tests/test_<module>.py` and use `unittest.mock.patch` to mock AWS calls.
- Version is extracted from the first `## [X.Y.Z]` entry in `CHANGELOG.md` at build time.

### Adding a New Command

1. Create `cftcli/newcommand.py` with a `_main()` entry point.
2. Import shared helpers from `utils.py`:
   ```python
   from cftcli.utils import LOG, CACHE, setup_session, add_common_arguments
   ```
3. Use `add_common_arguments(parser)` for the standard `--profile`, `--region`, `-v` flags.
4. Call `setup_session(args)` at the start of `_main()`.
5. Initialize your boto3 client after `setup_session()`, not at module level.
6. Register the entry point in `pyproject.toml` under `[project.scripts]`.
7. Add a test file `tests/test_newcommand.py`.
8. Document the command in `docs/commands.md`.
9. Add a changelog entry under `[Unreleased]` in `CHANGELOG.md`.

### Building and Publishing

```bash
python3 -m build --wheel
twine upload dist/*.whl
```

The CI pipeline (`scripts/build.sh`) handles this automatically on the `main` branch.

## Key Files Reference

| File | Purpose |
|---|---|
| `pyproject.toml` | Build config, dependencies, all 16 CLI entry points |
| `CHANGELOG.md` | Release history and version source |
| `cftcli/utils.py` | Shared utilities — start here when reading the code |
| `cftcli/deploy.py` | Largest module — stack create/update, wait logic, parameter loading |
| `pytest.ini` | Test config with coverage settings |
| `hatch_build.py` | Custom build hook to inject CHANGELOG.md and extract version |
| `examples/noop.yaml` | Minimal CloudFormation template for testing |
| `examples/noop-param.yaml` | Parameter file for the noop template |

## Troubleshooting

| Problem | Solution |
|---|---|
| `No module named 'boto3'` | Run `pip install cftcli` or `pip install boto3` |
| `Stack does not exist` | Check the stack name and region — use `list-stacks` to verify |
| `Access Denied` | Verify your AWS credentials and IAM permissions |
| Commands ignore `-v` flag | Ensure you're on the latest version — older versions had this bug |
| Cache returns stale values | Delete `~/.cftcli/` to clear the disk cache |
| `No module named 'yaml'` | Run `pip install pyyaml` |
