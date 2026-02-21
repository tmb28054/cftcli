"""Tests for cftcli.deploy module."""

import unittest
import json
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock
from cftcli.deploy import (
    find_current_stack, load_parameters, get_stack_state,
    get_inprogress_resources, get_failed_resources, stack_exist,
    fill_in_current_parameters
)


class TestDeploy(unittest.TestCase):
    """Test deploy module functions."""

    def test_find_current_stack_single(self):
        """Test finding current stack with single stack."""
        stacks = [{'StackName': 'test', 'CreationTime': datetime(2024, 1, 1)}]
        result = find_current_stack(stacks)
        self.assertEqual(result['StackName'], 'test')

    def test_find_current_stack_multiple(self):
        """Test finding current stack with multiple stacks."""
        stacks = [
            {'StackName': 'old', 'CreationTime': datetime(2023, 1, 1)},
            {'StackName': 'new', 'CreationTime': datetime(2024, 1, 1)}
        ]
        result = find_current_stack(stacks)
        self.assertEqual(result['StackName'], 'new')

    def test_find_current_stack_empty(self):
        """Test finding current stack with empty list."""
        result = find_current_stack([])
        self.assertEqual(result, {})

    def test_load_parameters_json(self):
        """Test loading parameters from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf8') as f:
            json.dump({'key1': 'value1', 'key2': 'value2'}, f)
            temp_path = f.name
        
        try:
            params = load_parameters(temp_path)
            self.assertEqual(len(params), 2)
            self.assertEqual(params[0]['ParameterKey'], 'key1')
            self.assertEqual(params[0]['ParameterValue'], 'value1')
        finally:
            import os
            os.unlink(temp_path)

    def test_load_parameters_yaml(self):
        """Test loading parameters from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf8') as f:
            f.write('key1: value1\nkey2: value2\n')
            temp_path = f.name
        
        try:
            params = load_parameters(temp_path)
            self.assertEqual(len(params), 2)
        finally:
            import os
            os.unlink(temp_path)

    def test_load_parameters_yml(self):
        """Test loading parameters from .yml file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False, encoding='utf8') as f:
            f.write('key1: value1\n')
            temp_path = f.name
        
        try:
            params = load_parameters(temp_path)
            self.assertEqual(len(params), 1)
        finally:
            import os
            os.unlink(temp_path)

    def test_load_parameters_invalid(self):
        """Test loading parameters from invalid file type."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf8') as f:
            f.write('invalid')
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                load_parameters(temp_path)
        finally:
            import os
            os.unlink(temp_path)

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_stack_exist_true(self, mock_cf):
        """Test stack_exist returns True when stack exists."""
        mock_cf.describe_stacks.return_value = {'Stacks': [{'StackName': 'test'}]}
        result = stack_exist('test')
        self.assertTrue(result)

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_stack_exist_false(self, mock_cf):
        """Test stack_exist returns False when stack doesn't exist."""
        from botocore.exceptions import ClientError
        mock_cf.describe_stacks.side_effect = ClientError(
            {'Error': {'Code': 'ValidationError', 'Message': 'does not exist'}},
            'DescribeStacks'
        )
        mock_cf.exceptions.ClientError = ClientError
        result = stack_exist('test')
        self.assertFalse(result)

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_get_inprogress_resources(self, mock_cf):
        """Test getting in-progress resources."""
        mock_cf.describe_stack_resources.return_value = {
            'StackResources': [
                {'LogicalResourceId': 'Resource1', 'ResourceStatus': 'CREATE_IN_PROGRESS'},
                {'LogicalResourceId': 'Resource2', 'ResourceStatus': 'CREATE_COMPLETE'}
            ]
        }
        result = get_inprogress_resources('test')
        self.assertEqual(result, ['Resource1'])

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_get_failed_resources(self, mock_cf):
        """Test getting failed resources."""
        mock_cf.describe_stack_resources.return_value = {
            'StackResources': [
                {
                    'LogicalResourceId': 'Resource1',
                    'ResourceStatus': 'CREATE_FAILED',
                    'ResourceStatusReason': 'Error'
                },
                {'LogicalResourceId': 'Resource2', 'ResourceStatus': 'CREATE_COMPLETE'}
            ]
        }
        result = get_failed_resources('test')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Resource1')

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_fill_in_current_parameters(self, mock_cf):
        """Test filling in current parameters."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{
                'Parameters': [
                    {'ParameterKey': 'Param1', 'ParameterValue': 'Value1'},
                    {'ParameterKey': 'Param2', 'ParameterValue': 'Value2'}
                ]
            }]
        }
        params = [{'ParameterKey': 'Param1', 'ParameterValue': 'NewValue'}]
        result = fill_in_current_parameters(params, 'test')
        self.assertEqual(len(result), 2)
        self.assertTrue(any(p['ParameterKey'] == 'Param2' for p in result))

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_get_stack_state_with_resources(self, mock_cf):
        """Test getting stack state with in-progress resources."""
        mock_cf.describe_stacks.return_value = {
            'Stacks': [{'StackStatus': 'UPDATE_IN_PROGRESS', 'CreationTime': datetime.now()}]
        }
        mock_cf.describe_stack_resources.return_value = {
            'StackResources': [
                {'LogicalResourceId': 'Res1', 'ResourceStatus': 'UPDATE_IN_PROGRESS'}
            ]
        }
        result = get_stack_state('test')
        self.assertIn('UPDATE_IN_PROGRESS', result)
        self.assertIn('Res1', result)

    @patch('cftcli.deploy.CLOUDFORMATION')
    def test_get_stack_state_deleted(self, mock_cf):
        """Test getting stack state for deleted stack."""
        mock_cf.describe_stacks.side_effect = Exception('Stack with id test does not exist')
        result = get_stack_state('test')
        self.assertEqual(result, 'DELETE_COMPLETE')


if __name__ == '__main__':
    unittest.main()
