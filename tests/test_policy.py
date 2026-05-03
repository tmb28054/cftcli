"""Tests for cftcli.policy module."""

import json
import unittest
from unittest.mock import patch, MagicMock
import cftcli.policy


class TestPolicy(unittest.TestCase):
    """Test policy module functions."""

    @patch('builtins.print')
    @patch('cftcli.policy.CACHE')
    @patch('cftcli.policy.boto3')
    @patch('cftcli.policy.setup_session')
    @patch('cftcli.policy._options')
    def test_main_displays_policy(self, mock_options, mock_setup, mock_boto3,
                                  mock_cache, mock_print):
        """Test _main retrieves and displays the stack policy."""
        mock_args = MagicMock()
        mock_args.stackname = 'test-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        policy = {'Statement': [{'Effect': 'Allow', 'Action': 'Update:*',
                                  'Principal': '*', 'Resource': '*'}]}
        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.get_stack_policy.return_value = {
            'StackPolicyBody': json.dumps(policy)
        }

        cftcli.policy._main()

        mock_cf.get_stack_policy.assert_called_once_with(StackName='test-stack')
        # Verify the policy was printed
        printed = mock_print.call_args_list[0][0][0]
        self.assertIn('Allow', printed)

    @patch('builtins.print')
    @patch('cftcli.policy.CACHE')
    @patch('cftcli.policy.boto3')
    @patch('cftcli.policy.setup_session')
    @patch('cftcli.policy._options')
    def test_main_handles_empty_policy(self, mock_options, mock_setup, mock_boto3,
                                       mock_cache, mock_print):
        """Test _main handles stacks with no policy."""
        mock_args = MagicMock()
        mock_args.stackname = 'test-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf
        mock_cf.get_stack_policy.return_value = {}

        cftcli.policy._main()

        printed = mock_print.call_args_list[0][0][0]
        self.assertEqual(printed, '{}')


if __name__ == '__main__':
    unittest.main()
