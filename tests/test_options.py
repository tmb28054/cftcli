"""Tests for _options() argument parsers across modules to boost coverage."""

from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest


class TestDeployOptions:
    """Tests for deploy._options()."""

    @patch('sys.argv', ['deploy-stack', '--stack', 'my-stack', '--filename', 'tpl.yaml'])
    def test_options_required_args(self):
        """Test _options parses required arguments."""
        from cftcli.deploy import _options

        args = _options()
        assert args.stackname == 'my-stack'
        assert args.filename == 'tpl.yaml'
        assert args.failure == 'DO_NOTHING'
        assert args.protected is False

    @patch('sys.argv', ['deploy-stack', '--stack', 's', '--filename', 'f',
                        '--parameters', 'A=1,B=2', '--failure', 'ROLLBACK',
                        '--protected', '-v', '--role', 'arn:role'])
    def test_options_all_args(self):
        """Test _options parses all optional arguments."""
        from cftcli.deploy import _options

        args = _options()
        assert args.parameters == 'A=1,B=2'
        assert args.failure == 'ROLLBACK'
        assert args.protected is True
        assert args.verbosity == 1
        assert args.role == 'arn:role'


class TestDestroyOptions:
    """Tests for destroy._options()."""

    @patch('sys.argv', ['delete-stack', '--stack', 'del-stack', '--role', 'arn:r'])
    def test_options_with_role(self):
        """Test _options parses --role."""
        from cftcli.destroy import _options

        args = _options()
        assert args.stackname == 'del-stack'
        assert args.role == 'arn:r'


class TestListOptions:
    """Tests for list._options()."""

    @patch('sys.argv', ['list-stacks'])
    def test_options_defaults(self):
        """Test _options uses defaults."""
        from cftcli.list import _options

        args = _options()
        assert args.verbosity == 0


class TestDetailOptions:
    """Tests for detail._options()."""

    @patch('sys.argv', ['describe-stack', 'stack1', 'stack2'])
    def test_options_positional_stacks(self):
        """Test _options parses positional stack names."""
        from cftcli.detail import _options

        args = _options()
        assert args.stacks == ['stack1', 'stack2']


class TestLockOptions:
    """Tests for lock._options()."""

    @patch('sys.argv', ['lock-stack', '--stack', 'prod'])
    def test_options_stack(self):
        """Test _options parses --stack."""
        from cftcli.lock import _options

        args = _options()
        assert args.stackname == 'prod'


class TestUnlockOptions:
    """Tests for unlock._options()."""

    @patch('sys.argv', ['unlock-stack', '--stack', 'prod'])
    def test_options_stack(self):
        """Test _options parses --stack."""
        from cftcli.unlock import _options

        args = _options()
        assert args.stackname == 'prod'


class TestPolicyOptions:
    """Tests for policy._options()."""

    @patch('sys.argv', ['stack-policy', '--stack', 'my-stack'])
    def test_options_stack(self):
        """Test _options parses --stack."""
        from cftcli.policy import _options

        args = _options()
        assert args.stackname == 'my-stack'


class TestListPipelinesOptions:
    """Tests for list_pipelines._options()."""

    @patch('sys.argv', ['list-pipelines', '-v', '-v'])
    def test_options_verbosity(self):
        """Test _options parses verbosity."""
        from cftcli.list_pipelines import _options

        args = _options()
        assert args.verbosity == 2


class TestAttachOptions:
    """Tests for attach._options()."""

    @patch('sys.argv', ['attach-stack', '--stack', 'watch-me'])
    def test_options_stack(self):
        """Test _options parses --stack."""
        from cftcli.attach import _options

        args = _options()
        assert args.stackname == 'watch-me'


class TestCodebuildOptions:
    """Tests for codebuild._options()."""

    @patch('sys.argv', ['codebuild', '--codebuild', 'proj', '--buildspec', 'bs.yml'])
    def test_options_required(self):
        """Test _options parses codebuild arguments."""
        from cftcli.codebuild import _options

        args = _options()
        assert args.codebuild == 'proj'
        assert args.buildspec == 'bs.yml'


class TestSecretsManagerOptions:
    """Tests for secretsmanager_env._options()."""

    @patch('sys.argv', ['secretmanager-env', 'arn:aws:secretsmanager:us-east-1:123:secret:s',
                        '--profile', 'prod', '--region', 'eu-west-1'])
    def test_options_all_args(self):
        """Test _options parses all arguments."""
        from cftcli.secretsmanager_env import _options

        args = _options()
        assert 'secretsmanager' in args.secret_arn
        assert args.profile == 'prod'
        assert args.region == 'eu-west-1'
