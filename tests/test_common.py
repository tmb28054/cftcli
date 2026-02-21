"""Tests for cftcli.common module."""

import unittest
from unittest.mock import patch
from cftcli.common import display_table


class TestCommon(unittest.TestCase):
    """Test common module functions."""

    @patch('builtins.print')
    def test_display_table_empty(self, mock_print):
        """Test displaying empty table."""
        display_table([])
        mock_print.assert_called()

    @patch('builtins.print')
    def test_display_table_with_data(self, mock_print):
        """Test displaying table with data."""
        records = [
            {'name': 'test1', 'status': 'active'},
            {'name': 'test2', 'status': 'inactive'}
        ]
        display_table(records, 'Test Table')
        self.assertGreater(mock_print.call_count, 0)

    @patch('builtins.print')
    def test_display_table_long_values(self, mock_print):
        """Test displaying table with long values."""
        records = [
            {'name': 'test', 'description': 'a' * 100}
        ]
        display_table(records)
        mock_print.assert_called()

    @patch('builtins.print')
    def test_display_table_failed_status(self, mock_print):
        """Test displaying table with CREATE_FAILED status."""
        records = [
            {'name': 'test', 'status': 'CREATE_FAILED'}
        ]
        display_table(records)
        mock_print.assert_called()

    @patch('builtins.print')
    def test_display_table_custom_title(self, mock_print):
        """Test displaying table with custom title."""
        records = [{'key': 'value'}]
        display_table(records, 'Custom Title')
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Custom Title' in str(call) for call in calls))

    @patch('builtins.print')
    def test_display_table_multiple_records(self, mock_print):
        """Test displaying table with multiple records."""
        records = [
            {'id': '1', 'name': 'first'},
            {'id': '2', 'name': 'second'},
            {'id': '3', 'name': 'third'}
        ]
        display_table(records)
        self.assertGreater(mock_print.call_count, 0)


if __name__ == '__main__':
    unittest.main()
