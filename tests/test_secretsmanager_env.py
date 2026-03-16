"""Tests for cftcli.secretsmanager_env module."""

import json
import sys
import unittest
from unittest.mock import patch, MagicMock
from cftcli.secretsmanager_env import get_secret, _main


class TestGetSecret(unittest.TestCase):
    """Test get_secret function."""

    @patch('boto3.Session')
    def test_get_secret_returns_dict(self, mock_session):
        """Test get_secret returns parsed JSON dict."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps({'DB_HOST': 'localhost', 'DB_PASS': 'secret'})
        }
        result = get_secret('arn:aws:secretsmanager:us-east-1:123:secret:my-secret', None, None)
        self.assertEqual(result['DB_HOST'], 'localhost')
        self.assertEqual(result['DB_PASS'], 'secret')

    @patch('boto3.Session')
    def test_get_secret_calls_correct_arn(self, mock_session):
        """Test get_secret calls Secrets Manager with the correct ARN."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps({'KEY': 'VALUE'})
        }
        arn = 'arn:aws:secretsmanager:us-east-1:123:secret:my-secret'
        get_secret(arn, 'default', 'us-east-1')
        mock_client.get_secret_value.assert_called_once_with(SecretId=arn)

    @patch('boto3.Session')
    def test_get_secret_invalid_json_raises(self, mock_session):
        """Test get_secret raises ValueError for non-JSON secret."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': 'not-json'
        }
        with self.assertRaises(ValueError):
            get_secret('arn:aws:secretsmanager:us-east-1:123:secret:my-secret', None, None)

    @patch('boto3.Session')
    def test_get_secret_uses_profile_and_region(self, mock_session):
        """Test get_secret passes profile and region to boto3 Session."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps({'KEY': 'VALUE'})
        }
        get_secret('arn:aws:secretsmanager:us-east-1:123:secret:my-secret', 'prod', 'eu-west-1')
        mock_session.assert_called_once_with(profile_name='prod', region_name='eu-west-1')


class TestMain(unittest.TestCase):
    """Test _main entry point."""

    @patch('boto3.Session')
    def test_main_outputs_export_statements(self, mock_session):
        """Test _main prints export statements for each key."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps({'DB_HOST': 'localhost', 'DB_PORT': '5432'})
        }
        with patch('sys.argv', ['secretsmanager-env', 'arn:aws:secretsmanager:us-east-1:123:secret:test']):
            with patch('builtins.print') as mock_print:
                _main()
                output = [str(call) for call in mock_print.call_args_list]
                self.assertTrue(any('DB_HOST' in line for line in output))
                self.assertTrue(any('DB_PORT' in line for line in output))

    @patch('boto3.Session')
    def test_main_escapes_single_quotes(self, mock_session):
        """Test _main escapes single quotes in secret values."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps({'PASS': "it's a secret"})
        }
        with patch('sys.argv', ['secretsmanager-env', 'arn:aws:secretsmanager:us-east-1:123:secret:test']):
            with patch('builtins.print') as mock_print:
                _main()
                printed = mock_print.call_args[0][0]
                self.assertIn("PASS", printed)
                self.assertNotIn("it's a secret", printed)  # raw unescaped form should not appear

    @patch('boto3.Session')
    def test_main_exits_on_invalid_json(self, mock_session):
        """Test _main exits with code 1 on invalid JSON secret."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': 'not-json'
        }
        with patch('sys.argv', ['secretsmanager-env', 'arn:aws:secretsmanager:us-east-1:123:secret:test']):
            with self.assertRaises(SystemExit) as ctx:
                _main()
            self.assertEqual(ctx.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
