"""Smoke tests for all cftcli modules.

Each test exercises the primary happy path for a module and runs in under
2 seconds with no external dependencies.
"""

from __future__ import annotations

import json
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest


@pytest.mark.smoke
@patch('cftcli.deploy.CLOUDFORMATION')
def test_deploy_stack_exist_happy_path(mock_cf):
    """Smoke: stack_exist returns True for an existing stack."""
    from cftcli.deploy import stack_exist

    mock_cf.describe_stacks.return_value = {
        'Stacks': [{'StackName': 'my-stack'}],
    }
    assert stack_exist('my-stack') is True


@pytest.mark.smoke
def test_deploy_load_parameters_happy_path():
    """Smoke: load_parameters reads a JSON file correctly."""
    from cftcli.deploy import load_parameters

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False, encoding='utf8',
    ) as f:
        json.dump({'Env': 'prod', 'Size': 'large'}, f)
        path = f.name
    try:
        params = load_parameters(path)
        assert len(params) == 2
        assert params[0]['ParameterKey'] == 'Env'
    finally:
        os.unlink(path)


@pytest.mark.smoke
@patch('builtins.print')
def test_common_display_table_happy_path(mock_print):
    """Smoke: display_table prints a formatted table."""
    from cftcli.common import display_table

    display_table([{'name': 'stack-1', 'status': 'OK'}], 'Stacks')
    assert mock_print.call_count >= 2


@pytest.mark.smoke
def test_utils_set_level_happy_path():
    """Smoke: set_level runs without error at default verbosity."""
    from cftcli.utils import set_level

    set_level(0)


@pytest.mark.smoke
def test_utils_load_file_happy_path():
    """Smoke: load_file reads a file."""
    from cftcli.utils import load_file

    with tempfile.NamedTemporaryFile(
        mode='w', delete=False, encoding='utf8',
    ) as f:
        f.write('hello')
        path = f.name
    try:
        assert load_file(path) == 'hello'
    finally:
        os.unlink(path)


@pytest.mark.smoke
@patch('cftcli.list_pipelines.INTERFACE')
def test_list_pipelines_state_happy_path(mock_iface):
    """Smoke: _get_pipeline_state returns Succeeded."""
    from cftcli.list_pipelines import _get_pipeline_state

    mock_iface.get_pipeline_state.return_value = {
        'stageStates': [{'latestExecution': {'status': 'Succeeded'}}],
    }
    assert _get_pipeline_state('my-pipe') == 'Succeeded'


@pytest.mark.smoke
def test_codebuild_s3arn_to_s3url_happy_path():
    """Smoke: s3arn_to_s3url converts correctly."""
    from cftcli.codebuild import s3arn_to_s3url

    assert s3arn_to_s3url('arn:aws:s3:::bucket/key') == 's3://bucket/key'


@pytest.mark.smoke
@patch('boto3.Session')
def test_secretsmanager_get_secret_happy_path(mock_session):
    """Smoke: get_secret parses a JSON secret."""
    from cftcli.secretsmanager_env import get_secret

    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client
    mock_client.get_secret_value.return_value = {
        'SecretString': json.dumps({'KEY': 'VALUE'}),
    }
    result = get_secret('arn:aws:secretsmanager:us-east-1:123:secret:s', None, None)
    assert result == {'KEY': 'VALUE'}


@pytest.mark.smoke
def test_version_exists():
    """Smoke: package version is defined."""
    from cftcli import __version__

    assert __version__ is not None
    assert __version__ != 'unknown'


@pytest.mark.smoke
def test_lock_policy_structure():
    """Smoke: LOCK_POLICY has expected structure."""
    from cftcli.lock import LOCK_POLICY

    assert 'Statement' in LOCK_POLICY
    effects = [s['Effect'] for s in LOCK_POLICY['Statement']]
    assert 'Deny' in effects


@pytest.mark.smoke
def test_unlock_policy_structure():
    """Smoke: UNLOCK_POLICY has only Allow statements."""
    from cftcli.unlock import UNLOCK_POLICY

    for stmt in UNLOCK_POLICY['Statement']:
        assert stmt['Effect'] == 'Allow'


@pytest.mark.smoke
@patch('cftcli.detail.CLOUDFORMATION')
def test_detail_get_resources_happy_path(mock_cf):
    """Smoke: _get_resources returns a dict keyed by LogicalResourceId."""
    from cftcli.detail import _get_resources

    mock_cf.describe_stack_resources.return_value = {
        'StackResources': [
            {
                'LogicalResourceId': 'Bucket',
                'Timestamp': datetime(2024, 1, 1),
                'ResourceStatus': 'CREATE_COMPLETE',
            },
        ],
    }
    result = _get_resources('test')
    assert 'Bucket' in result
