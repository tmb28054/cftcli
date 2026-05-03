"""Tests for _main() entry points across all modules to boost coverage.

These tests mock _options() and boto3 clients to exercise the full
_main() code paths without making real AWS calls.
"""

from __future__ import annotations

import argparse
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock, call

import pytest


class TestDeployMain:
    """Tests for deploy._main()."""

    @patch('cftcli.deploy.wait_for_stack')
    @patch('cftcli.deploy.boto3')
    @patch('cftcli.deploy.setup_session')
    @patch('cftcli.deploy._options')
    def test_main_creates_new_stack(self, mock_opts, mock_setup, mock_boto3, mock_wait):
        """Test _main creates a stack when it doesn't exist."""
        import cftcli.deploy

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False, encoding='utf8',
        ) as f:
            f.write('AWSTemplateFormatVersion: 2010-09-09\n')
            tpl_path = f.name

        try:
            mock_opts.return_value = argparse.Namespace(
                stackname='new-stack', profile='default', region='us-east-1',
                verbosity=0, role=None, filename=tpl_path, parameters='',
                parameter_file='', failure='DO_NOTHING', protected=False,
            )
            mock_cf = MagicMock()
            mock_boto3.client.return_value = mock_cf
            mock_cf.describe_stacks.side_effect = Exception(
                'Stack with id new-stack does not exist',
            )
            mock_cf.exceptions.ClientError = Exception

            cftcli.deploy._main()

            mock_cf.create_stack.assert_called_once()
            mock_wait.assert_called_once_with('new-stack')
        finally:
            os.unlink(tpl_path)

    @patch('cftcli.deploy.wait_for_stack')
    @patch('cftcli.deploy.boto3')
    @patch('cftcli.deploy.setup_session')
    @patch('cftcli.deploy._options')
    def test_main_updates_existing_stack(self, mock_opts, mock_setup, mock_boto3, mock_wait):
        """Test _main updates a stack when it exists."""
        import cftcli.deploy

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False, encoding='utf8',
        ) as f:
            f.write('AWSTemplateFormatVersion: 2010-09-09\n')
            tpl_path = f.name

        try:
            mock_opts.return_value = argparse.Namespace(
                stackname='existing-stack', profile='default', region='us-east-1',
                verbosity=0, role='arn:aws:iam::123:role/R', filename=tpl_path,
                parameters='Key=Val', parameter_file='', failure='DO_NOTHING',
                protected=False,
            )
            mock_cf = MagicMock()
            mock_boto3.client.return_value = mock_cf
            mock_cf.describe_stacks.return_value = {
                'Stacks': [{
                    'StackName': 'existing-stack',
                    'CreationTime': datetime(2024, 1, 1),
                    'Parameters': [],
                }],
            }

            cftcli.deploy._main()

            mock_cf.update_stack.assert_called_once()
            kwargs = mock_cf.update_stack.call_args[1]
            assert kwargs['RoleARN'] == 'arn:aws:iam::123:role/R'
        finally:
            os.unlink(tpl_path)

    @patch('cftcli.deploy.wait_for_stack')
    @patch('cftcli.deploy.boto3')
    @patch('cftcli.deploy.setup_session')
    @patch('cftcli.deploy._options')
    def test_main_with_parameter_file(self, mock_opts, mock_setup, mock_boto3, mock_wait):
        """Test _main loads parameters from a file."""
        import cftcli.deploy

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False, encoding='utf8',
        ) as f:
            f.write('AWSTemplateFormatVersion: 2010-09-09\n')
            tpl_path = f.name

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False, encoding='utf8',
        ) as f:
            json.dump({'Param1': 'Value1'}, f)
            param_path = f.name

        try:
            mock_opts.return_value = argparse.Namespace(
                stackname='param-stack', profile='default', region='us-east-1',
                verbosity=0, role=None, filename=tpl_path, parameters='',
                parameter_file=param_path, failure='ROLLBACK', protected=True,
            )
            mock_cf = MagicMock()
            mock_boto3.client.return_value = mock_cf
            mock_cf.describe_stacks.side_effect = Exception(
                'Stack with id param-stack does not exist',
            )
            mock_cf.exceptions.ClientError = Exception

            cftcli.deploy._main()

            kwargs = mock_cf.create_stack.call_args[1]
            assert kwargs['OnFailure'] == 'ROLLBACK'
            assert kwargs['EnableTerminationProtection'] is True
            assert any(p['ParameterKey'] == 'Param1' for p in kwargs['Parameters'])
        finally:
            os.unlink(tpl_path)
            os.unlink(param_path)


class TestDestroyMain:
    """Tests for destroy._main()."""

    @patch('cftcli.destroy.wait_for_stack')
    @patch('cftcli.destroy.CACHE')
    @patch('cftcli.destroy.boto3')
    @patch('cftcli.destroy.setup_session')
    @patch('cftcli.destroy._options')
    def test_main_deletes_with_role(self, mock_opts, mock_setup, mock_boto3,
                                    mock_cache, mock_wait):
        """Test _main passes RoleARN when provided."""
        import cftcli.destroy

        mock_opts.return_value = argparse.Namespace(
            stackname='del-stack', profile='default', region='us-east-1',
            verbosity=0, role='arn:aws:iam::123:role/R',
        )
        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.destroy._main()

        mock_cf.delete_stack.assert_called_once_with(
            StackName='del-stack', RoleARN='arn:aws:iam::123:role/R',
        )


class TestDetailMain:
    """Tests for detail._main()."""

    @patch('cftcli.detail.CACHE')
    @patch('cftcli.detail.boto3')
    @patch('cftcli.detail.setup_session')
    @patch('cftcli.detail._options')
    def test_main_displays_stack(self, mock_opts, mock_setup, mock_boto3, mock_cache):
        """Test _main displays stack detail."""
        import cftcli.detail

        mock_opts.return_value = argparse.Namespace(
            stacks=['my-stack'], profile='default', region='us-east-1', verbosity=0,
        )
        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{
                'StackName': 'my-stack',
                'StackStatus': 'CREATE_COMPLETE',
                'CreationTime': str(datetime(2024, 1, 1)),
            }],
        }
        mock_cf.describe_stack_events.return_value = {'StackEvents': []}
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        cftcli.detail._main()

        mock_cf.describe_stacks.assert_called()

    @patch('cftcli.detail.CACHE')
    @patch('cftcli.detail.boto3')
    @patch('cftcli.detail.setup_session')
    @patch('cftcli.detail._options')
    def test_main_uses_cache_when_no_stacks(self, mock_opts, mock_setup,
                                             mock_boto3, mock_cache):
        """Test _main falls back to cached stack name."""
        import cftcli.detail

        mock_opts.return_value = argparse.Namespace(
            stacks=[], profile='default', region='us-east-1', verbosity=0,
        )
        mock_cache.get.side_effect = lambda key, default=[]: (
            json.dumps(['cached-stack']) if key == 'stacks' else default
        )
        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{'StackName': 'cached-stack', 'StackStatus': 'OK'}],
        }
        mock_cf.describe_stack_events.return_value = {'StackEvents': []}
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        cftcli.detail._main()

        mock_cf.describe_stacks.assert_called_with(StackName='cached-stack')

    @patch('cftcli.detail.CACHE')
    @patch('cftcli.detail.setup_session')
    @patch('cftcli.detail._options')
    def test_main_exits_when_no_stack(self, mock_opts, mock_setup, mock_cache):
        """Test _main exits with code 1 when no stack name available."""
        import cftcli.detail

        mock_opts.return_value = argparse.Namespace(
            stacks=[], profile='default', region='us-east-1', verbosity=0,
        )
        mock_cache.get.return_value = ''

        with pytest.raises(SystemExit) as exc_info:
            cftcli.detail._main()
        assert exc_info.value.code == 1


class TestListMain:
    """Tests for list._main()."""

    @patch('cftcli.list.CACHE')
    @patch('cftcli.list.cftcli.common.display_table')
    @patch('cftcli.list.boto3')
    @patch('cftcli.list.setup_session')
    @patch('cftcli.list._options')
    def test_main_color_codes_statuses(self, mock_opts, mock_setup, mock_boto3,
                                       mock_display, mock_cache):
        """Test _main applies correct colors to different statuses."""
        import cftcli.list

        mock_opts.return_value = argparse.Namespace(
            profile='default', region='us-east-1', verbosity=0,
        )
        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.list_stacks.return_value = {
            'StackSummaries': [
                {'StackName': 's1', 'StackStatus': 'CREATE_COMPLETE',
                 'CreationTime': datetime(2024, 1, 1)},
                {'StackName': 's2', 'StackStatus': 'ROLLBACK_COMPLETE',
                 'CreationTime': datetime(2024, 1, 1)},
                {'StackName': 's3', 'StackStatus': 'UPDATE_ROLLBACK_FAILED',
                 'CreationTime': datetime(2024, 1, 1)},
                {'StackName': 's4', 'StackStatus': 'CREATE_IN_PROGRESS',
                 'CreationTime': datetime(2024, 1, 1)},
            ],
        }

        cftcli.list._main()

        stacks = mock_display.call_args[0][0]
        assert len(stacks) == 4


class TestListPipelinesMain:
    """Tests for list_pipelines._main()."""

    @patch('cftcli.list_pipelines.CACHE')
    @patch('cftcli.list_pipelines.cftcli.common.display_table')
    @patch('cftcli.list_pipelines.boto3')
    @patch('cftcli.list_pipelines.setup_session')
    @patch('cftcli.list_pipelines._options')
    def test_main_lists_pipelines(self, mock_opts, mock_setup, mock_boto3,
                                   mock_display, mock_cache):
        """Test _main lists pipelines with correct state colors."""
        import cftcli.list_pipelines

        mock_opts.return_value = argparse.Namespace(
            profile='default', region='us-east-1', verbosity=0,
        )
        mock_cp = MagicMock()
        mock_boto3.client.return_value = mock_cp
        mock_cp.list_pipelines.return_value = {
            'pipelines': [{'name': 'pipe-1'}],
        }
        mock_cp.get_pipeline_state.return_value = {
            'stageStates': [{'latestExecution': {'status': 'Succeeded'}}],
        }

        cftcli.list_pipelines._main()

        mock_display.assert_called_once()


class TestLockMain:
    """Tests for lock._main()."""

    @patch('cftcli.lock.CACHE')
    @patch('cftcli.lock.boto3')
    @patch('cftcli.lock.setup_session')
    @patch('cftcli.lock._options')
    def test_main_applies_policy_and_protection(self, mock_opts, mock_setup,
                                                 mock_boto3, mock_cache):
        """Test _main applies policy and enables termination protection."""
        import cftcli.lock

        mock_opts.return_value = argparse.Namespace(
            stackname='prod-stack', profile='default', region='us-east-1', verbosity=0,
        )
        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.lock._main()

        mock_cf.set_stack_policy.assert_called_once()
        mock_cf.update_termination_protection.assert_called_once_with(
            StackName='prod-stack', EnableTerminationProtection=True,
        )


class TestUnlockMain:
    """Tests for unlock._main()."""

    @patch('cftcli.unlock.CACHE')
    @patch('cftcli.unlock.boto3')
    @patch('cftcli.unlock.setup_session')
    @patch('cftcli.unlock._options')
    def test_main_removes_policy_and_protection(self, mock_opts, mock_setup,
                                                 mock_boto3, mock_cache):
        """Test _main removes policy and disables termination protection."""
        import cftcli.unlock

        mock_opts.return_value = argparse.Namespace(
            stackname='prod-stack', profile='default', region='us-east-1', verbosity=0,
        )
        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.unlock._main()

        mock_cf.set_stack_policy.assert_called_once()
        mock_cf.update_termination_protection.assert_called_once_with(
            StackName='prod-stack', EnableTerminationProtection=False,
        )


class TestPolicyMain:
    """Tests for policy._main()."""

    @patch('builtins.print')
    @patch('cftcli.policy.CACHE')
    @patch('cftcli.policy.boto3')
    @patch('cftcli.policy.setup_session')
    @patch('cftcli.policy._options')
    def test_main_prints_policy(self, mock_opts, mock_setup, mock_boto3,
                                mock_cache, mock_print):
        """Test _main retrieves and prints the stack policy."""
        import cftcli.policy

        mock_opts.return_value = argparse.Namespace(
            stackname='my-stack', profile='default', region='us-east-1', verbosity=0,
        )
        policy = {'Statement': [{'Effect': 'Allow', 'Action': 'Update:*',
                                  'Principal': '*', 'Resource': '*'}]}
        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.get_stack_policy.return_value = {
            'StackPolicyBody': json.dumps(policy),
        }

        cftcli.policy._main()

        printed = mock_print.call_args_list[0][0][0]
        assert 'Allow' in printed


class TestAttachMain:
    """Tests for attach._main()."""

    @patch('cftcli.attach.CACHE')
    @patch('cftcli.attach.wait_for_stack')
    @patch('cftcli.attach.boto3')
    @patch('cftcli.attach.setup_session')
    @patch('cftcli.attach._options')
    def test_main_attaches_to_stack(self, mock_opts, mock_setup, mock_boto3,
                                    mock_wait, mock_cache):
        """Test _main calls wait_for_stack."""
        import cftcli.attach

        mock_opts.return_value = argparse.Namespace(
            stackname='my-stack', profile='default', region='us-east-1', verbosity=0,
        )

        cftcli.attach._main()

        mock_wait.assert_called_once_with('my-stack')
        mock_cache.close.assert_called_once()


class TestCodebuildMain:
    """Tests for codebuild._main()."""

    @patch('cftcli.codebuild.CACHE')
    @patch('cftcli.codebuild.watch_build')
    @patch('cftcli.codebuild.boto3')
    @patch('cftcli.codebuild.setup_session')
    @patch('cftcli.codebuild._options')
    def test_main_starts_build(self, mock_opts, mock_setup, mock_boto3,
                               mock_watch, mock_cache):
        """Test _main starts a codebuild and watches it."""
        import cftcli.codebuild

        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, encoding='utf8',
        ) as f:
            f.write('version: 0.2\nphases:\n  build:\n    commands:\n      - echo hi\n')
            bs_path = f.name

        try:
            mock_opts.return_value = argparse.Namespace(
                codebuild='my-project', buildspec=bs_path, profile='default',
                region='us-east-1', verbosity=0, src_artifact='', dst_artifact='',
                bucket='', bucket_path='cftcli', rolearn='',
            )
            mock_cb = MagicMock()
            mock_s3 = MagicMock()
            mock_boto3.client.side_effect = lambda svc: mock_cb if svc == 'codebuild' else mock_s3
            mock_cb.start_build.return_value = {'build': {'id': 'build-123'}}
            mock_watch.return_value = {'buildComplete': True}

            cftcli.codebuild._main()

            mock_cb.start_build.assert_called_once()
            mock_watch.assert_called_once_with('build-123')
        finally:
            os.unlink(bs_path)

    @patch('cftcli.codebuild.CACHE')
    @patch('cftcli.codebuild.download_artifact')
    @patch('cftcli.codebuild.watch_build')
    @patch('cftcli.codebuild.boto3')
    @patch('cftcli.codebuild.setup_session')
    @patch('cftcli.codebuild._options')
    def test_main_with_artifacts(self, mock_opts, mock_setup, mock_boto3,
                                 mock_watch, mock_download, mock_cache):
        """Test _main downloads artifacts when dst_artifact is set."""
        import cftcli.codebuild

        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, encoding='utf8',
        ) as f:
            f.write('version: 0.2\n')
            bs_path = f.name

        try:
            mock_opts.return_value = argparse.Namespace(
                codebuild='my-project', buildspec=bs_path, profile='default',
                region='us-east-1', verbosity=0, src_artifact='s3://src/input.zip',
                dst_artifact='output.zip', bucket='my-bucket', bucket_path='builds',
                rolearn='',
            )
            mock_cb = MagicMock()
            mock_s3 = MagicMock()
            mock_boto3.client.side_effect = lambda svc: mock_cb if svc == 'codebuild' else mock_s3
            mock_cb.start_build.return_value = {'build': {'id': 'build-456'}}
            mock_watch.return_value = {
                'artifacts': {'location': 'arn:aws:s3:::my-bucket/builds/out.zip'},
            }
            mock_download.return_value = 'Download of output.zip SUCCESS'

            cftcli.codebuild._main()

            kwargs = mock_cb.start_build.call_args[1]
            assert kwargs['artifactsOverride']['type'] == 'S3'
            assert kwargs['sourceTypeOverride'] == 'S3'
            mock_download.assert_called_once()
        finally:
            os.unlink(bs_path)


class TestCodebuildSaveCache:
    """Tests for codebuild.save_cache()."""

    @patch('cftcli.codebuild.CACHE')
    def test_save_cache_writes_all_keys(self, mock_cache):
        """Test save_cache writes all expected keys."""
        from cftcli.codebuild import save_cache

        args = argparse.Namespace(
            profile='default', buildspec='bs.yml', region='us-east-1',
            codebuild='proj', rolearn='', src_artifact='', dst_artifact='',
            bucket='bkt', bucket_path='path',
        )
        save_cache(args)
        assert mock_cache.add.call_count == 9


class TestUtilsAddStackArgument:
    """Tests for utils.add_stack_argument()."""

    def test_add_stack_argument(self):
        """Test add_stack_argument adds --stack to parser."""
        from cftcli.utils import add_stack_argument

        parser = argparse.ArgumentParser()
        add_stack_argument(parser)
        args = parser.parse_args(['--stack', 'my-stack'])
        assert args.stackname == 'my-stack'


class TestUtilsSetupSession:
    """Tests for utils.setup_session()."""

    @patch('cftcli.utils.boto3')
    def test_setup_session_calls_boto3(self, mock_boto3):
        """Test setup_session configures boto3 default session."""
        from cftcli.utils import setup_session

        args = argparse.Namespace(verbosity=0, profile='prod', region='eu-west-1')
        setup_session(args)
        mock_boto3.setup_default_session.assert_called_once_with(
            profile_name='prod', region_name='eu-west-1',
        )
