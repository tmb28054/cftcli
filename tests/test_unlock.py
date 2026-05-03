"""Tests for cftcli.unlock module."""

import unittest
from unittest.mock import patch, MagicMock
import cftcli.unlock


class TestUnlock(unittest.TestCase):
    """Test unlock module functions."""

    @patch('cftcli.unlock.CACHE')
    @patch('cftcli.unlock.boto3')
    @patch('cftcli.unlock.setup_session')
    @patch('cftcli.unlock._options')
    def test_main_applies_unlock_policy(self, mock_options, mock_setup,
                                        mock_boto3, mock_cache):
        """Test _main applies the unlock policy."""
        mock_args = MagicMock()
        mock_args.stackname = 'test-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.unlock._main()

        mock_cf.set_stack_policy.assert_called_once()

    @patch('cftcli.unlock.CACHE')
    @patch('cftcli.unlock.boto3')
    @patch('cftcli.unlock.setup_session')
    @patch('cftcli.unlock._options')
    def test_main_disables_termination_protection(self, mock_options, mock_setup,
                                                   mock_boto3, mock_cache):
        """Test _main disables termination protection."""
        mock_args = MagicMock()
        mock_args.stackname = 'test-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.unlock._main()

        mock_cf.update_termination_protection.assert_called_once_with(
            StackName='test-stack',
            EnableTerminationProtection=False
        )

    def test_unlock_policy_has_only_allow(self):
        """Test UNLOCK_POLICY only contains Allow statements."""
        for statement in cftcli.unlock.UNLOCK_POLICY['Statement']:
            self.assertEqual(statement['Effect'], 'Allow')


if __name__ == '__main__':
    unittest.main()
