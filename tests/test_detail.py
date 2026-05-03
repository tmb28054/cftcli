"""Tests for cftcli.detail module."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import cftcli.detail


class TestDetail(unittest.TestCase):
    """Test detail module functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_cf = MagicMock()
        cftcli.detail.CLOUDFORMATION = self.mock_cf

    @patch('cftcli.detail.CLOUDFORMATION')
    def test_get_events_returns_latest(self, mock_cf):
        """Test _get_events returns the latest event per resource."""
        mock_cf.describe_stack_events.return_value = {
            'StackEvents': [
                {
                    'PhysicalResourceId': 'res-1',
                    'Timestamp': datetime(2024, 1, 2),
                    'ResourceStatus': 'CREATE_COMPLETE'
                },
                {
                    'PhysicalResourceId': 'res-1',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'CREATE_IN_PROGRESS'
                },
            ]
        }
        cftcli.detail.CLOUDFORMATION = mock_cf
        result = cftcli.detail._get_events('test-stack')
        self.assertEqual(len(result), 1)
        self.assertEqual(result['res-1']['ResourceStatus'], 'CREATE_COMPLETE')

    @patch('cftcli.detail.CLOUDFORMATION')
    def test_get_events_handles_pagination(self, mock_cf):
        """Test _get_events handles paginated responses."""
        mock_cf.describe_stack_events.side_effect = [
            {
                'StackEvents': [
                    {
                        'PhysicalResourceId': 'res-1',
                        'Timestamp': datetime(2024, 1, 1),
                        'ResourceStatus': 'CREATE_COMPLETE'
                    }
                ],
                'NextToken': 'token123'
            },
            {
                'StackEvents': [
                    {
                        'PhysicalResourceId': 'res-2',
                        'Timestamp': datetime(2024, 1, 1),
                        'ResourceStatus': 'CREATE_COMPLETE'
                    }
                ]
            }
        ]
        cftcli.detail.CLOUDFORMATION = mock_cf
        result = cftcli.detail._get_events('test-stack')
        self.assertEqual(len(result), 2)

    @patch('cftcli.detail.CLOUDFORMATION')
    def test_get_resources_returns_dict(self, mock_cf):
        """Test _get_resources returns a dictionary keyed by LogicalResourceId."""
        mock_cf.describe_stack_resources.return_value = {
            'StackResources': [
                {
                    'LogicalResourceId': 'MyBucket',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'CREATE_COMPLETE'
                }
            ]
        }
        cftcli.detail.CLOUDFORMATION = mock_cf
        result = cftcli.detail._get_resources('test-stack')
        self.assertIn('MyBucket', result)

    @patch('cftcli.detail.CLOUDFORMATION')
    def test_get_resources_keeps_latest(self, mock_cf):
        """Test _get_resources keeps the latest entry for duplicate resources."""
        mock_cf.describe_stack_resources.return_value = {
            'StackResources': [
                {
                    'LogicalResourceId': 'MyBucket',
                    'Timestamp': datetime(2024, 1, 2),
                    'ResourceStatus': 'UPDATE_COMPLETE'
                },
                {
                    'LogicalResourceId': 'MyBucket',
                    'Timestamp': datetime(2024, 1, 1),
                    'ResourceStatus': 'CREATE_COMPLETE'
                }
            ]
        }
        cftcli.detail.CLOUDFORMATION = mock_cf
        result = cftcli.detail._get_resources('test-stack')
        self.assertEqual(result['MyBucket']['ResourceStatus'], 'UPDATE_COMPLETE')

    @patch('builtins.print')
    def test_display_resources_skips_deleted(self, mock_print):
        """Test _display_resources skips DELETE_COMPLETE resources."""
        resources = {
            'Active': {
                'LogicalResourceId': 'Active',
                'PhysicalResourceId': 'phys-1',
                'ResourceType': 'AWS::S3::Bucket',
                'Timestamp': datetime(2024, 1, 1),
                'ResourceStatus': 'CREATE_COMPLETE',
            },
            'Deleted': {
                'LogicalResourceId': 'Deleted',
                'PhysicalResourceId': 'phys-2',
                'ResourceType': 'AWS::S3::Bucket',
                'Timestamp': datetime(2024, 1, 1),
                'ResourceStatus': 'DELETE_COMPLETE',
            }
        }
        cftcli.detail._display_resources(resources)
        output = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('Active', output)


if __name__ == '__main__':
    unittest.main()
