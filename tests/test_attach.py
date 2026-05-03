"""Tests for cftcli.attach module."""

import unittest
from unittest.mock import patch, MagicMock
import cftcli.attach


class TestAttach(unittest.TestCase):
    """Test attach module functions."""

    @patch('cftcli.attach.CACHE')
    @patch('cftcli.attach.wait_for_stack')
    @patch('cftcli.attach.boto3')
    @patch('cftcli.attach.setup_session')
    @patch('cftcli.attach._options')
    def test_main_calls_wait_for_stack(self, mock_options, mock_setup,
                                       mock_boto3, mock_wait, mock_cache):
        """Test _main calls wait_for_stack with the correct stack name."""
        mock_args = MagicMock()
        mock_args.stackname = 'my-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        cftcli.attach._main()

        mock_wait.assert_called_once_with('my-stack')

    @patch('cftcli.attach.CACHE')
    @patch('cftcli.attach.wait_for_stack')
    @patch('cftcli.attach.boto3')
    @patch('cftcli.attach.setup_session')
    @patch('cftcli.attach._options')
    def test_main_sets_up_session(self, mock_options, mock_setup,
                                  mock_boto3, mock_wait, mock_cache):
        """Test _main calls setup_session."""
        mock_args = MagicMock()
        mock_args.stackname = 'my-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        cftcli.attach._main()

        mock_setup.assert_called_once_with(mock_args)

    @patch('cftcli.attach.CACHE')
    @patch('cftcli.attach.wait_for_stack')
    @patch('cftcli.attach.boto3')
    @patch('cftcli.attach.setup_session')
    @patch('cftcli.attach._options')
    def test_main_closes_cache(self, mock_options, mock_setup,
                               mock_boto3, mock_wait, mock_cache):
        """Test _main closes the cache."""
        mock_args = MagicMock()
        mock_args.stackname = 'my-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        cftcli.attach._main()

        mock_cache.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
