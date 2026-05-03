#!/usr/bin/env python3
"""Attach to a CloudFormation stack which is under change."""

from __future__ import annotations

import argparse
import os

import boto3

from cftcli.deploy import wait_for_stack
from cftcli.utils import CACHE, setup_session, add_common_arguments


def _options() -> argparse.Namespace:
    """Provide the argparse option set.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--stack', '-s',
                        dest='stackname',
                        required=True,
                        default=os.getenv('STACKNAME', CACHE.get('stackname', '')),
                        help='The Stack Name to use.')
    add_common_arguments(parser)
    return parser.parse_args()


def _main() -> None:
    """Main entry point for attach-stack command."""
    args = _options()

    setup_session(args)

    boto3.setup_default_session(
        profile_name=args.profile,
        region_name=args.region,
    )

    wait_for_stack(args.stackname)
    CACHE.close()


if __name__ == '__main__':
    _main()
