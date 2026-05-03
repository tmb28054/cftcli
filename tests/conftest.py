"""Shared pytest configuration and fixtures."""

from __future__ import annotations

import argparse
from unittest.mock import MagicMock

import pytest


@pytest.fixture()
def mock_cf_args():
    """Return a mock argparse.Namespace for CloudFormation commands."""
    args = argparse.Namespace(
        stackname='test-stack',
        profile='default',
        region='us-east-1',
        verbosity=0,
        role=None,
    )
    return args


@pytest.fixture()
def mock_cf_client():
    """Return a MagicMock boto3 CloudFormation client."""
    return MagicMock()
