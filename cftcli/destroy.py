#!/usr/bin/env python3
"""Delete CloudFormation stacks."""


import argparse
import json

import boto3

from cftcli.deploy import wait_for_stack
from cftcli.utils import LOG, CACHE, setup_session, add_common_arguments


CLOUDFORMATION = None


def _options() -> argparse.Namespace:
    """Provide the argparse option set.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', '-r',
                        required=False,
                        dest='role',
                        help='The role to use.')
    parser.add_argument('--stack', '-s',
                        dest='stackname',
                        required=True,
                        default='',
                        help='The Stack Name to use.')
    add_common_arguments(parser)
    return parser.parse_args()


def _main() -> None:
    """Main entry point for delete-stack command."""
    args = _options()

    setup_session(args)

    global CLOUDFORMATION  # pylint: disable=global-statement
    CLOUDFORMATION = boto3.client('cloudformation')

    kwargs = {
        'StackName': args.stackname,
    }
    if args.role:
        kwargs['RoleARN'] = args.role
    response = CLOUDFORMATION.delete_stack(**kwargs)
    LOG.debug(json.dumps(response, indent=2, default=str))
    wait_for_stack(args.stackname)
    CACHE.close()


if __name__ == '__main__':
    _main()
