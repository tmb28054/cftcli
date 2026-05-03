"""Tests for deploy.wait_for_stack — the spinner/polling loop and failure path.

These cover the core UX of the tool: waiting for a stack operation to
complete, displaying failures, and printing the final status.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch, MagicMock, call

import pytest

import cftcli.deploy
from cftcli.deploy import wait_for_stack, get_stack_state


class TestWaitForStackSuccess:
    """Tests for wait_for_stack when the stack completes successfully."""

    @patch('builtins.print')
    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_already_complete(self, mock_cf, mock_print):
        """Stack is already CREATE_COMPLETE — no polling, prints green."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{'StackStatus': 'CREATE_COMPLETE',
                         'CreationTime': datetime(2024, 1, 1)}],
        }
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        wait_for_stack('my-stack')

        output = mock_print.call_args[0][0]
        assert 'my-stack' in output
        assert 'CREATE_COMPLETE' in output

    @patch('builtins.print')
    @patch('cftcli.deploy.time.sleep')
    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_polls_until_complete(self, mock_cf, mock_sleep, mock_print):
        """Stack transitions from IN_PROGRESS to COMPLETE with polling."""
        mock_cf.describe_stacks.side_effect = [
            # First call: in progress
            {'Stacks': [{'StackStatus': 'CREATE_IN_PROGRESS',
                          'CreationTime': datetime(2024, 1, 1)}]},
            # Second call (inside polling loop): still in progress (same state)
            {'Stacks': [{'StackStatus': 'CREATE_IN_PROGRESS',
                          'CreationTime': datetime(2024, 1, 1)}]},
            # Third call: complete
            {'Stacks': [{'StackStatus': 'CREATE_COMPLETE',
                          'CreationTime': datetime(2024, 1, 1)}]},
            # Fourth call: final state check after loop exits
            {'Stacks': [{'StackStatus': 'CREATE_COMPLETE',
                          'CreationTime': datetime(2024, 1, 1)}]},
        ]
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        wait_for_stack('my-stack')

        assert mock_sleep.called
        output = mock_print.call_args[0][0]
        assert 'CREATE_COMPLETE' in output


class TestWaitForStackFailure:
    """Tests for wait_for_stack when the stack fails."""

    @patch('builtins.print')
    @patch('cftcli.deploy.cftcli.common.display_table')
    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_rollback_displays_failed_resources(self, mock_cf, mock_display, mock_print):
        """ROLLBACK_COMPLETE triggers display of failed resources."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{'StackStatus': 'ROLLBACK_COMPLETE',
                         'CreationTime': datetime(2024, 1, 1)}],
        }
        mock_cf.describe_stack_resources.side_effect = [
            # First call from get_inprogress_resources
            {'StackResources': []},
            # Second call from get_failed_resources
            {'StackResources': [
                {'LogicalResourceId': 'BadResource',
                 'ResourceStatus': 'CREATE_FAILED',
                 'ResourceStatusReason': 'Something went wrong'},
            ]},
        ]

        wait_for_stack('my-stack')

        mock_display.assert_called_once()
        failed = mock_display.call_args[0][0]
        assert len(failed) == 1
        assert failed[0]['name'] == 'BadResource'

        output = mock_print.call_args[0][0]
        assert 'ROLLBACK_COMPLETE' in output

    @patch('builtins.print')
    @patch('cftcli.deploy.cftcli.common.display_table')
    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_failed_state_displays_table(self, mock_cf, mock_display, mock_print):
        """UPDATE_FAILED triggers the failure path."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{'StackStatus': 'UPDATE_FAILED',
                         'CreationTime': datetime(2024, 1, 1)}],
        }
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        wait_for_stack('my-stack')

        mock_display.assert_called_once()
        output = mock_print.call_args[0][0]
        assert 'UPDATE_FAILED' in output

    @patch('builtins.print')
    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_delete_complete_is_success(self, mock_cf, mock_print):
        """DELETE_COMPLETE is not a failure — prints green."""
        mock_cf.describe_stacks.side_effect = Exception(
            'Stack with id my-stack does not exist',
        )

        wait_for_stack('my-stack')

        output = mock_print.call_args[0][0]
        assert 'DELETE_COMPLETE' in output


class TestGetStackStateComplete:
    """Tests for get_stack_state when no resources are in progress."""

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_returns_plain_status(self, mock_cf):
        """Returns just the status string when no resources are in progress."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{'StackStatus': 'CREATE_COMPLETE',
                         'CreationTime': datetime(2024, 1, 1)}],
        }
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        result = get_stack_state('my-stack')

        assert result == 'CREATE_COMPLETE'
        assert ' - ' not in result

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_reraises_unknown_exception(self, mock_cf):
        """Reraises exceptions that aren't 'does not exist'."""
        mock_cf.describe_stacks.side_effect = Exception('AccessDenied')

        with pytest.raises(Exception, match='AccessDenied'):
            get_stack_state('my-stack')
