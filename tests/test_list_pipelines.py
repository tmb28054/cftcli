"""Tests for cftcli.list_pipelines module."""

import unittest
from unittest.mock import patch, MagicMock
from cftcli.list_pipelines import _get_pipeline_state


class TestListPipelines(unittest.TestCase):
    """Test list_pipelines module functions."""

    @patch('cftcli.list_pipelines.INTERFACE')
    def test_get_pipeline_state_failed(self, mock_interface):
        """Test pipeline state when failed."""
        mock_interface.get_pipeline_state.return_value = {
            'stageStates': [
                {'latestExecution': {'status': 'Failed'}}
            ]
        }
        result = _get_pipeline_state('test-pipeline')
        self.assertEqual(result, 'Failed')

    @patch('cftcli.list_pipelines.INTERFACE')
    def test_get_pipeline_state_in_progress(self, mock_interface):
        """Test pipeline state when in progress."""
        mock_interface.get_pipeline_state.return_value = {
            'stageStates': [
                {'latestExecution': {'status': 'InProgress'}}
            ]
        }
        result = _get_pipeline_state('test-pipeline')
        self.assertEqual(result, 'InProgress')

    @patch('cftcli.list_pipelines.INTERFACE')
    def test_get_pipeline_state_succeeded(self, mock_interface):
        """Test pipeline state when succeeded."""
        mock_interface.get_pipeline_state.return_value = {
            'stageStates': [
                {'latestExecution': {'status': 'Succeeded'}}
            ]
        }
        result = _get_pipeline_state('test-pipeline')
        self.assertEqual(result, 'Succeeded')

    @patch('cftcli.list_pipelines.INTERFACE')
    def test_get_pipeline_state_cancelled(self, mock_interface):
        """Test pipeline state when cancelled."""
        mock_interface.get_pipeline_state.return_value = {
            'stageStates': [
                {'latestExecution': {'status': 'Cancelled'}}
            ]
        }
        result = _get_pipeline_state('test-pipeline')
        self.assertEqual(result, 'Failed')

    @patch('cftcli.list_pipelines.INTERFACE')
    def test_get_pipeline_state_stopped(self, mock_interface):
        """Test pipeline state when stopped."""
        mock_interface.get_pipeline_state.return_value = {
            'stageStates': [
                {'latestExecution': {'status': 'Stopped'}}
            ]
        }
        result = _get_pipeline_state('test-pipeline')
        self.assertEqual(result, 'Failed')


if __name__ == '__main__':
    unittest.main()
