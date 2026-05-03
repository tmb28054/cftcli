"""Tests for cftcli.destroy module."""

import unittest
from unittest.mock import patch, MagicMock
import cftcli.destroy


class TestDestroy(unittest.TestCase):
    """Test destroy module functions."""

    @patch('cftcli.destroy.wait_for_stack')
    @patch('cftcli.destroy.CACHE')
    @patch('cftcli.destroy.boto3')
    @patch('cftcli.destroy.setup_session')
    @patch('cftcli.destroy._options')
    def test_main_calls_delete_stack(self, mock_options, mock_setup, mock_boto3,
                                     mock_cache, mock_wait):
        """Test _main calls delete_stack with correct arguments."""
        mock_args = MagicMock()
        mock_args.stackname = 'test-stack'
        mock_args.role = None
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.destroy._main()

        mock_cf.delete_stack.assert_called_once_with(StackName='test-stack')
        mock_wait.assert_called_once_with('test-stack')

    @patch('cftcli.destroy.wait_for_stack')
    @patch('cftcli.destroy.CACHE')
    @patch('cftcli.destroy.boto3')
    @patch('cftcli.destroy.setup_session')
    @patch('cftcli.destroy._options')
    def test_main_with_role(self, mock_options, mock_setup, mock_boto3,
                            mock_cache, mock_wait):
        """Test _main passes role ARN when provided."""
        mock_args = MagicMock()
        mock_args.stackname = 'test-stack'
        mock_args.role = 'arn:aws:iam::123456789012:role/MyRole'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.destroy._main()

        mock_cf.delete_stack.assert_called_once_with(
            StackName='test-stack',
            RoleARN='arn:aws:iam::123456789012:role/MyRole'
        )


if __name__ == '__main__':
    unittest.main()
