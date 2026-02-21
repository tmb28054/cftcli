"""Shared utilities for cftcli commands."""

import logging
import boto3
import diskcache


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


def get_boto3_client(service: str, profile: str, region: str):
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
