# Changelog for the CloudFormation Template CLI

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Fixed `attach-stack` and `delete-stack` crashing because `deploy.CLOUDFORMATION` was never initialized when called from other modules
- Fixed `UnboundLocalError` in `codebuild.watch_build` when a build completes before the first poll (`phase` was never assigned)

### Added

- Smoke tests verifying `attach` and `destroy` initialize `deploy.CLOUDFORMATION` before calling `wait_for_stack`
- Tests for `deploy.wait_for_stack` — polling loop, success path, failure/rollback display, and DELETE_COMPLETE handling
- Tests for `deploy.get_stack_state` — plain status return and unknown exception re-raise
- Tests for `codebuild.watch_build` — already-complete, polling, failed, and early-exit paths
- Tests for `detail._display_events`, `_display_stack`, and `_display_resources` — event/resource rendering, status coloring, long-value wrapping, and DELETE_COMPLETE filtering
- Test suite expanded from 115 to 136 tests, coverage from 87% to 97%

## [2.11.1] - 2026-05-03

### Changed

- Added `from __future__ import annotations` to all source modules
- Added type hints to all function signatures (parameters and return types)
- Replaced `type(value) in [dict, list]` with `isinstance()` in `detail.py`
- Narrowed broad `except Exception` to `except (ClientError, OSError)` in `codebuild.py`
- Added `add_stack_argument()` helper to `utils.py` to reduce duplicate `--stack` argument code
- Fixed import ordering in `attach.py` (third-party before first-party)
- Removed unused `import logging` from `deploy.py` and `codebuild.py`
- Removed unused `set_level` import from `deploy.py`
- Fixed `open()` without encoding in `__version__.py`

### Added

- Smoke tests for all modules (`pytest -m smoke`), 12 tests
- Tests for all `_main()` entry points and `_options()` parsers
- Test suite expanded from 71 to 113 tests, coverage from 61% to 86%
- Registered `smoke` marker in `pytest.ini`
- Added "Testing" section to `README.md`

## [2.11.0] - 2026-05-02

### Changed

- Consolidated duplicated `set_level()`, `load_file()`, and constants (`TIME_DELAY`, `CACHETIME`, `CACHE`) into `cftcli/utils.py`
- Added shared `add_common_arguments()` and `setup_session()` helpers to reduce boilerplate across all CLI modules
- All module-level boto3 clients now initialize as `None` instead of calling `boto3.client()` at import time
- Replaced commented-out `set_level()` calls with `setup_session()` so verbosity flags work correctly
- Added minimum version bounds to all dependencies in `pyproject.toml`
- Expanded `.gitignore` with standard Python, IDE, and OS entries
- Added `set -e` and branch guard to `scripts/build.sh`
- Fixed shebang lines from `#!env python` to `#!/usr/bin/env python3` across all modules

### Fixed

- Fixed `LOCK_POLCIY` typo to `LOCK_POLICY` in `lock.py`
- Fixed `UNLOCK_POLCIY` typo to `UNLOCK_POLICY` in `unlock.py`
- Fixed `_disply_resources` typo to `_display_resources` in `detail.py`
- Fixed `KeyError` bug in `detail.py` `_get_resources()` (`resource[name]` → `resources[name]`)
- Synced `requirements.txt` with `pyproject.toml` (added missing `diskcache` and `pyyaml`)
- Ensured `CACHE.close()` is called in all CLI entry points

### Added

- Created missing `scripts/test.sh` referenced by `.gitlab-ci.yml`
- Added tests for `attach.py`, `destroy.py`, `detail.py`, `list.py`, `lock.py`, `unlock.py`, and `policy.py`
- Test suite expanded from 41 to 71 tests with all modules now covered
- Added `docs/prompt.md` — AI assistant prompt file documenting tooling, workflows, and conventions

## [2.10.1] - 2026-04-14

### Added

- secretsmanager-env command to export Secrets Manager secrets as shell environment variables
- Added Jenkinsfile

## [2.10.0] - 2026-03-16

### Added

- secretsmanager-env command to export Secrets Manager secrets as shell environment variables

## [2.9.1] - 2026-03-15

### Update

- fixed version bug

## [2.9.0] - 2026-02-21

### Update

- adopted pyproject.toml
- added unit tests

## [2.8.1] - 2024-09-04

### Update

- Fixed deleted stack refrence

## [2.8.0] - 2024-02-11

### Added

- policy management for stacks
- Passing roles for stack operations

## [2.7.0] - 2024-01-23

### Added

- When updating an existing stack parameters not passed use the previus values.

## [2.6.1] - 2023-10-30

### fix

- fixed region and session usage

## [2.6.0] - 2023-06-06

### Update

- added attach

## [2.6.0] - 2023-06-06

### Update

- added attach

## [2.5.1] - 2023-03-06

### Fix

- Fixed parameter file bug

## [2.5.0] - 2023-02-22

### Added

- parameter-file support

## [2.4.2] - 2022-10-30

### Fix

- Fixed parameters bug

## [2.4.1] - 2022-10-24

### Fix

- fixed github push

## [2.4.0] - 2022-10-23

### Added

- codebuild cli

## [2.3.0] - 2022-10-04

### Added

- pipeline

## [2.2.0] - 2022-10-02

### Added

- parameters

## [2.1.0] - 2022-09-11

### Added

- list-pipelines
- attach-stack

## [2.0.1] - 2022-06-11

### fix

- Fixed deploy bug,

## [2.0.0] - 2022-06-09

### Update

- Updated the licends

## [1.1.1] - 2022-06-07

### Fix

- Updated stack detail to infer the stack

## [1.1.0] - 2022-06-07

### Added

- Display of the Resources for the stack

## [1.0.0] - 2022-06-07

### Removed

- AssumeRole was moved out as it presume an assume role design.

## [0.1.0] - 2022-06-06

- Initial Push
