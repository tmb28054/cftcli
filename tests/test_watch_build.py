"""Tests for codebuild.watch_build — the build-watching loop."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

import cftcli.codebuild


class TestWatchBuild:
    """Tests for codebuild.watch_build."""

    @patch('builtins.print')
    @patch('cftcli.codebuild.boto3')
    @patch('cftcli.codebuild.CODEBUILD')
    def test_build_already_complete(self, mock_cb, mock_boto3, mock_print):
        """Build is already complete — no polling, prints status and logs."""
        mock_cb.batch_get_builds.return_value = {
            'builds': [{
                'buildComplete': True,
                'buildStatus': 'SUCCEEDED',
                'projectName': 'my-project',
                'currentPhase': 'COMPLETED',
                'logs': {
                    'cloudWatchLogsArn': 'arn:aws:logs:us-east-1:123:log-group:/build:*:stream:abc',
                },
            }],
        }
        mock_logs = MagicMock()
        mock_boto3.client.return_value = mock_logs
        mock_logs.get_log_events.return_value = {
            'events': [{'message': '  [Container] Build succeeded  '}],
        }

        result = cftcli.codebuild.watch_build('build-123')

        assert result['buildComplete'] is True
        printed = [c[0][0] for c in mock_print.call_args_list]
        assert any('COMPLETED' in line for line in printed)
        assert any('Build succeeded' in line for line in printed)

    @patch('builtins.print')
    @patch('cftcli.codebuild.time.sleep')
    @patch('cftcli.codebuild.boto3')
    @patch('cftcli.codebuild.CODEBUILD')
    def test_build_polls_until_complete(self, mock_cb, mock_boto3,
                                        mock_sleep, mock_print):
        """Build transitions from IN_PROGRESS to COMPLETED with polling."""
        in_progress_build = {
            'buildComplete': False,
            'buildStatus': 'IN_PROGRESS',
            'projectName': 'my-project',
            'currentPhase': 'BUILD',
            'logs': {
                'cloudWatchLogsArn': 'arn:aws:logs:us-east-1:123:log-group:/build:*:stream:abc',
            },
        }
        completed_build = {
            **in_progress_build,
            'buildComplete': True,
            'currentPhase': 'COMPLETED',
        }
        mock_cb.batch_get_builds.side_effect = [
            {'builds': [in_progress_build]},       # initial check
            {'builds': [completed_build]},          # polling loop
            {'builds': [completed_build]},          # after spinner.stop
        ]
        mock_logs = MagicMock()
        mock_boto3.client.return_value = mock_logs
        mock_logs.get_log_events.return_value = {'events': []}

        result = cftcli.codebuild.watch_build('build-456')

        assert result['currentPhase'] == 'COMPLETED'
        assert mock_sleep.called

    @patch('builtins.print')
    @patch('cftcli.codebuild.boto3')
    @patch('cftcli.codebuild.CODEBUILD')
    def test_build_failed_shows_red(self, mock_cb, mock_boto3, mock_print):
        """Failed build prints status in red (phase != COMPLETED)."""
        mock_cb.batch_get_builds.return_value = {
            'builds': [{
                'buildComplete': True,
                'buildStatus': 'FAILED',
                'projectName': 'my-project',
                'currentPhase': 'BUILD',
                'logs': {
                    'cloudWatchLogsArn': 'arn:aws:logs:us-east-1:123:log-group:/build:*:stream:abc',
                },
            }],
        }
        mock_logs = MagicMock()
        mock_boto3.client.return_value = mock_logs
        mock_logs.get_log_events.return_value = {'events': []}

        result = cftcli.codebuild.watch_build('build-789')

        assert result['buildStatus'] == 'FAILED'
        status_line = mock_print.call_args_list[0][0][0]
        assert 'build complete with status' in status_line

    @patch('builtins.print')
    @patch('cftcli.codebuild.boto3')
    @patch('cftcli.codebuild.CODEBUILD')
    def test_build_not_in_progress_exits_early(self, mock_cb, mock_boto3, mock_print):
        """Build with status != IN_PROGRESS exits the loop immediately."""
        mock_cb.batch_get_builds.return_value = {
            'builds': [{
                'buildComplete': False,
                'buildStatus': 'STOPPED',
                'projectName': 'my-project',
                'currentPhase': 'BUILD',
                'logs': {
                    'cloudWatchLogsArn': 'arn:aws:logs:us-east-1:123:log-group:/build:*:stream:abc',
                },
            }],
        }
        mock_logs = MagicMock()
        mock_boto3.client.return_value = mock_logs
        mock_logs.get_log_events.return_value = {'events': []}

        result = cftcli.codebuild.watch_build('build-stop')

        # Should exit without polling
        assert mock_cb.batch_get_builds.call_count == 1
