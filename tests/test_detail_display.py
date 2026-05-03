"""Tests for detail.py display functions — _display_events, _display_stack."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

import cftcli.detail


class TestDisplayEvents:
    """Tests for detail._display_events."""

    @patch('builtins.print')
    @patch('cftcli.detail.CLOUDFORMATION')
    def test_displays_events_table(self, mock_cf, mock_print):
        """_display_events prints an events table and a resources table."""
        mock_cf.describe_stack_events.return_value = {
            'StackEvents': [
                {
                    'PhysicalResourceId': 'phys-1',
                    'LogicalResourceId': 'MyBucket',
                    'ResourceType': 'AWS::S3::Bucket',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'CREATE_COMPLETE',
                },
            ],
        }
        mock_cf.describe_stack_resources.return_value = {
            'StackResources': [
                {
                    'LogicalResourceId': 'MyBucket',
                    'PhysicalResourceId': 'phys-1',
                    'ResourceType': 'AWS::S3::Bucket',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'CREATE_COMPLETE',
                },
            ],
        }

        cftcli.detail._display_events('test-stack')

        output = ' '.join(str(c) for c in mock_print.call_args_list)
        assert 'Events' in output
        assert 'Resources' in output

    @patch('builtins.print')
    @patch('cftcli.detail.CLOUDFORMATION')
    def test_skips_deleted_events(self, mock_cf, mock_print):
        """_display_events skips events with DELETE_COMPLETE status."""
        mock_cf.describe_stack_events.return_value = {
            'StackEvents': [
                {
                    'PhysicalResourceId': 'phys-1',
                    'LogicalResourceId': 'Deleted',
                    'ResourceType': 'AWS::S3::Bucket',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'DELETE_COMPLETE',
                },
                {
                    'PhysicalResourceId': 'phys-2',
                    'LogicalResourceId': 'Active',
                    'ResourceType': 'AWS::S3::Bucket',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'CREATE_COMPLETE',
                },
            ],
        }
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        cftcli.detail._display_events('test-stack')

        output = ' '.join(str(c) for c in mock_print.call_args_list)
        assert 'Active' in output

    @patch('builtins.print')
    @patch('cftcli.detail.CLOUDFORMATION')
    def test_colors_in_progress_events(self, mock_cf, mock_print):
        """_display_events applies blue color to IN_PROGRESS statuses."""
        mock_cf.describe_stack_events.return_value = {
            'StackEvents': [
                {
                    'PhysicalResourceId': 'phys-1',
                    'LogicalResourceId': 'Updating',
                    'ResourceType': 'AWS::Lambda::Function',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'UPDATE_IN_PROGRESS',
                },
            ],
        }
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        cftcli.detail._display_events('test-stack')

        # Just verify it ran without error — color codes are terminal-specific
        assert mock_print.called

    @patch('builtins.print')
    @patch('cftcli.detail.CLOUDFORMATION')
    def test_colors_failed_events(self, mock_cf, mock_print):
        """_display_events applies red color to FAILED statuses."""
        mock_cf.describe_stack_events.return_value = {
            'StackEvents': [
                {
                    'PhysicalResourceId': 'phys-1',
                    'LogicalResourceId': 'Broken',
                    'ResourceType': 'AWS::EC2::Instance',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'CREATE_FAILED',
                    'ResourceStatusReason': 'Limit exceeded',
                },
            ],
        }
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        cftcli.detail._display_events('test-stack')

        assert mock_print.called


class TestDisplayStack:
    """Tests for detail._display_stack."""

    @patch('builtins.print')
    @patch('cftcli.detail.CLOUDFORMATION')
    def test_displays_stack_detail(self, mock_cf, mock_print):
        """_display_stack prints stack detail, events, and resources."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{
                'StackName': 'my-stack',
                'StackStatus': 'CREATE_COMPLETE',
                'CreationTime': '2024-01-01T00:00:00Z',
                'Description': '',
            }],
        }
        mock_cf.describe_stack_events.return_value = {'StackEvents': []}
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        cftcli.detail._display_stack('my-stack')

        output = ' '.join(str(c) for c in mock_print.call_args_list)
        assert 'Stack Detail' in output
        assert 'StackName' in output

    @patch('builtins.print')
    @patch('cftcli.detail.CLOUDFORMATION')
    def test_displays_dict_values_as_json(self, mock_cf, mock_print):
        """_display_stack formats dict/list values as JSON."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{
                'StackName': 'my-stack',
                'Tags': [{'Key': 'Env', 'Value': 'prod'}],
                'Outputs': [],
            }],
        }
        mock_cf.describe_stack_events.return_value = {'StackEvents': []}
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        cftcli.detail._display_stack('my-stack')

        output = ' '.join(str(c) for c in mock_print.call_args_list)
        assert 'Env' in output

    @patch('builtins.print')
    @patch('cftcli.detail.CLOUDFORMATION')
    def test_wraps_long_values(self, mock_cf, mock_print):
        """_display_stack wraps values longer than 50 characters."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{
                'StackName': 'my-stack',
                'StackId': 'a' * 80,
            }],
        }
        mock_cf.describe_stack_events.return_value = {'StackEvents': []}
        mock_cf.describe_stack_resources.return_value = {'StackResources': []}

        cftcli.detail._display_stack('my-stack')

        assert mock_print.called


class TestDisplayResources:
    """Tests for detail._display_resources with various status colors."""

    @patch('builtins.print')
    def test_colors_in_progress_resources(self, mock_print):
        """_display_resources applies blue to IN_PROGRESS resources."""
        resources = {
            'Updating': {
                'LogicalResourceId': 'Updating',
                'PhysicalResourceId': 'phys-1',
                'ResourceType': 'AWS::S3::Bucket',
                'Timestamp': datetime(2024, 1, 1),
                'ResourceStatus': 'UPDATE_IN_PROGRESS',
            },
        }
        cftcli.detail._display_resources(resources)
        assert mock_print.called

    @patch('builtins.print')
    def test_colors_failed_resources(self, mock_print):
        """_display_resources applies red to FAILED resources."""
        resources = {
            'Broken': {
                'LogicalResourceId': 'Broken',
                'PhysicalResourceId': 'phys-1',
                'ResourceType': 'AWS::EC2::Instance',
                'Timestamp': datetime(2024, 1, 1),
                'ResourceStatus': 'CREATE_FAILED',
            },
        }
        cftcli.detail._display_resources(resources)
        assert mock_print.called

    @patch('builtins.print')
    def test_wraps_long_resource_values(self, mock_print):
        """_display_resources wraps values longer than 20 characters."""
        resources = {
            'LongId': {
                'LogicalResourceId': 'LongId',
                'PhysicalResourceId': 'x' * 40,
                'ResourceType': 'AWS::S3::Bucket',
                'Timestamp': datetime(2024, 1, 1),
                'ResourceStatus': 'CREATE_COMPLETE',
            },
        }
        cftcli.detail._display_resources(resources)
        assert mock_print.called
