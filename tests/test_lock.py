"""Tests for cftcli.lock module."""

import unittest
from unittest.mock import patch, MagicMock
import cftcli.lock


class TestLock(unittest.TestCase):
    """Test lock module functions."""

    @patch('cftcli.lock.CACHE')
    @patch('cftcli.lock.boto3')
    @patch('cftcli.lock.setup_session')
    @patch('cftcli.lock._options')
    def test_main_applies_policy(self, mock_options, mock_setup, mock_boto3, mock_cache):
        """Test _main applies stack policy."""
        mock_args = MagicMock()
        mock_args.stackname = 'test-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.lock._main()

        mock_cf.set_stack_policy.assert_called_once()
        call_kwargs = mock_cf.set_stack_policy.call_args[1]
        self.assertEqual(call_kwargs['StackName'], 'test-stack')

    @patch('cftcli.lock.CACHE')
    @patch('cftcli.lock.boto3')
    @patch('cftcli.lock.setup_session')
    @patch('cftcli.lock._options')
    def test_main_enables_termination_protection(self, mock_options, mock_setup,
                                                  mock_boto3, mock_cache):
        """Test _main enables termination protection."""
        mock_args = MagicMock()
        mock_args.stackname = 'test-stack'
        mock_args.profile = 'default'
        mock_args.region = 'us-east-1'
        mock_args.verbosity = 0
        mock_options.return_value = mock_args

        mock_cf = MagicMock()
        mock_boto3.client.return_value = mock_cf

        cftcli.lock._main()

        mock_cf.update_termination_protection.assert_called_once_with(
            StackName='test-stack',
            EnableTerminationProtection=True
        )

    def test_lock_policy_has_deny_statement(self):
        """Test LOCK_POLICY contains a Deny statement."""
        deny_statements = [
            s for s in cftcli.lock.LOCK_POLICY['Statement']
            if s['Effect'] == 'Deny'
        ]
        self.assertEqual(len(deny_statements), 1)


if __name__ == '__main__':
    unittest.main()
