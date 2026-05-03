#!/usr/bin/env python3
"""Shared utilities for cftcli commands."""

from __future__ import annotations

import argparse
import logging
import os

import boto3
import diskcache


LOG = logging.getLogger()

TIME_DELAY = 3
CACHETIME = 60 * 60 * 8  # Cache for 8 hours
CACHE = diskcache.Cache('~/.cftcli')


def set_level(verbosity: int) -> None:
    """Set the logging level based on command line provided verbosity.

    By default, botocore and urllib3 are quiet and only show logging
    statements at the ERROR level. These logging statements will be shown
    when verbosity is greater than 1 (-vv, -vvv, etc).

    Args:
        verbosity (int): 0-based level of verbosity provided on CLI.
    """
    level = logging.INFO
    logging.getLogger('botocore').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    if verbosity > 1:
        logging.getLogger('botocore').setLevel(logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.DEBUG)
    if verbosity == 1:
        logging.getLogger('botocore').setLevel(logging.INFO)
        logging.getLogger('urllib3').setLevel(logging.INFO)
    level -= 10 * verbosity

    logging.getLogger('validator').setLevel(level)
    if verbosity:
        logging.getLogger().setLevel(logging.DEBUG)


def load_file(filename: str) -> str:
    """Return the content of the file.

    Args:
        filename (str): Path to the file to load.

    Returns:
        str: File contents.
    """
    with open(filename, encoding='utf8') as file_handler:
        return file_handler.read()


def get_boto3_client(service: str, profile: str, region: str) -> boto3.client:
    """Create a boto3 client with the specified configuration.

    Args:
        service (str): AWS service name (e.g., 'cloudformation', 'codebuild').
        profile (str): AWS profile name.
        region (str): AWS region name.

    Returns:
        boto3.client: Configured boto3 client.
    """
    session = boto3.Session(profile_name=profile, region_name=region)
    return session.client(service)


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common CLI arguments shared across commands.

    Adds --profile, --region, and --verbose arguments to the parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add arguments to.
    """
    parser.add_argument('--profile', '-p',
                        required=False,
                        dest='profile',
                        default=os.getenv('AWS_PROFILE', CACHE.get('profile', 'default')),
                        help='The profile to use.')
    parser.add_argument('--region',
                        required=False,
                        dest='region',
                        default=os.getenv('AWS_DEFAULT_REGION', CACHE.get('region', 'us-east-1')),
                        help='Region to use.')
    parser.add_argument('-v', '--verbose', '--debug',
                        dest='verbosity',
                        action='count',
                        default=0,
                        help="Use multiple times to increase logging level")


def add_stack_argument(parser: argparse.ArgumentParser) -> None:
    """Add the --stack argument to a parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add the argument to.
    """
    parser.add_argument('--stack', '-s',
                        dest='stackname',
                        required=True,
                        default='',
                        help='The Stack Name to use.')


def setup_session(args: argparse.Namespace) -> None:
    """Set up logging and boto3 default session from parsed arguments.

    Args:
        args (argparse.Namespace): Parsed command line arguments with
            verbosity, profile, and region attributes.
    """
    set_level(args.verbosity)
    boto3.setup_default_session(
        profile_name=args.profile,
        region_name=args.region,
    )
