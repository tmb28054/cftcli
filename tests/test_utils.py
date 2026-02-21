"""Tests for cftcli.utils module."""

import unittest
import tempfile
import os
import logging
from unittest.mock import patch, MagicMock
from cftcli.utils import set_level, load_file, get_boto3_client, CACHETIME, CACHE


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_load_file(self):
        """Test loading file contents."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf8') as f:
            f.write('test content')
            temp_path = f.name
        
        try:
            content = load_file(temp_path)
            self.assertEqual(content, 'test content')
        finally:
            os.unlink(temp_path)

    def test_load_file_multiline(self):
        """Test loading file with multiple lines."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf8') as f:
            f.write('line1\nline2\nline3')
            temp_path = f.name
        
        try:
            content = load_file(temp_path)
            self.assertIn('line1', content)
            self.assertIn('line2', content)
        finally:
            os.unlink(temp_path)

    def test_set_level_zero_verbosity(self):
        """Test setting log level with zero verbosity."""
        set_level(0)
        self.assertEqual(logging.getLogger('botocore').level, logging.ERROR)
        self.assertEqual(logging.getLogger('urllib3').level, logging.ERROR)

    def test_set_level_one_verbosity(self):
        """Test setting log level with verbosity 1."""
        set_level(1)
        self.assertEqual(logging.getLogger('botocore').level, logging.INFO)
        self.assertEqual(logging.getLogger('urllib3').level, logging.INFO)

    def test_set_level_two_verbosity(self):
        """Test setting log level with verbosity 2."""
        set_level(2)
        self.assertEqual(logging.getLogger('botocore').level, logging.DEBUG)
        self.assertEqual(logging.getLogger('urllib3').level, logging.DEBUG)

    def test_set_level_high_verbosity(self):
        """Test setting log level with high verbosity."""
        set_level(3)
        self.assertEqual(logging.getLogger().level, logging.DEBUG)

    @patch('boto3.Session')
    def test_get_boto3_client(self, mock_session):
        """Test creating boto3 client."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        client = get_boto3_client('s3', 'default', 'us-east-1')
        
        mock_session.assert_called_once_with(profile_name='default', region_name='us-east-1')
        mock_session.return_value.client.assert_called_once_with('s3')
        self.assertEqual(client, mock_client)

    @patch('boto3.Session')
    def test_get_boto3_client_cloudformation(self, mock_session):
        """Test creating cloudformation client."""
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        client = get_boto3_client('cloudformation', 'prod', 'us-west-2')
        
        mock_session.assert_called_once_with(profile_name='prod', region_name='us-west-2')
        mock_session.return_value.client.assert_called_once_with('cloudformation')

    def test_cachetime_constant(self):
        """Test CACHETIME constant value."""
        self.assertEqual(CACHETIME, 60 * 60 * 8)

    def test_cache_exists(self):
        """Test CACHE object exists."""
        self.assertIsNotNone(CACHE)


if __name__ == '__main__':
    unittest.main()
