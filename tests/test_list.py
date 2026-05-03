"""Tests for cftcli.list module."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import cftcli.list


class TestList(unittest.TestCase):
    """Test list module functions."""

    @patch('cftcli.list.CACHE')
    @patch('cftcli.list.cftcli.common.display_table')
    @patch('cftcli.list.boto3')
    @patch('cftcli.list.setup_session')
    @patch('cftcli.list._options')
    def test_main_lists_stacks(self, mock_options, mock_setup, mock_boto3,
                               mock_display, mock_cache):
        """Test _main lists stacks and displays them."""
        mock_args = MagicMock()
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.list_stacks.return_value = {
            'StackSummaries': [
                {
                    'StackName': 'my-stack',
                    'StackStatus': 'CREATE_COMPLETE',
                    'CreationTime': datetime(2024, 1, 1),
                }
            ]
        }

        cftcli.list._main()

        mock_display.assert_called_once()
        args = mock_display.call_args
        self.assertEqual(len(args[0][0]), 1)
        self.assertEqual(args[0][1], 'Stacks')

    @patch('cftcli.list.CACHE')
    @patch('cftcli.list.cftcli.common.display_table')
    @patch('cftcli.list.boto3')
    @patch('cftcli.list.setup_session')
    @patch('cftcli.list._options')
    def test_main_skips_deleted_stacks(self, mock_options, mock_setup, mock_boto3,
                                       mock_display, mock_cache):
        """Test _main skips stacks with DELETE_COMPLETE status."""
        mock_args = MagicMock()
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.list_stacks.return_value = {
            'StackSummaries': [
                {
                    'StackName': 'active-stack',
                    'StackStatus': 'CREATE_COMPLETE',
                    'CreationTime': datetime(2024, 1, 1),
                },
                {
                    'StackName': 'deleted-stack',
                    'StackStatus': 'DELETE_COMPLETE',
                    'CreationTime': datetime(2024, 1, 1),
                }
            ]
        }

        cftcli.list._main()

        args = mock_display.call_args
        self.assertEqual(len(args[0][0]), 1)

    @patch('cftcli.list.CACHE')
    @patch('cftcli.list.cftcli.common.display_table')
    @patch('cftcli.list.boto3')
    @patch('cftcli.list.setup_session')
    @patch('cftcli.list._options')
    def test_main_handles_pagination(self, mock_options, mock_setup, mock_boto3,
                                     mock_display, mock_cache):
        """Test _main handles paginated responses."""
        mock_args = MagicMock()
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.list_stacks.side_effect = [
            {
                'StackSummaries': [
                    {
                        'StackName': 'stack-1',
                        'StackStatus': 'CREATE_COMPLETE',
                        'CreationTime': datetime(2024, 1, 1),
                    }
                ],
                'NextToken': 'token123'
            },
            {
                'StackSummaries': [
                    {
                        'StackName': 'stack-2',
                        'StackStatus': 'UPDATE_COMPLETE',
                        'CreationTime': datetime(2024, 2, 1),
                    }
                ]
            }
        ]

        cftcli.list._main()

        args = mock_display.call_args
        self.assertEqual(len(args[0][0]), 2)


if __name__ == '__main__':
    unittest.main()
