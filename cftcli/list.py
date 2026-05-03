#!/usr/bin/env python3
"""List all CloudFormation stacks in a region."""


import argparse
import json

import boto3
from termcolor import colored

import cftcli.common
from cftcli.utils import LOG, CACHE, setup_session, add_common_arguments


CLOUDFORMATION = None


def _options() -> argparse.Namespace:
    """Provide the argparse option set.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    return parser.parse_args()


def _main() -> None:
    """Main entry point for list-stacks command."""
    args = _options()

    setup_session(args)

    global CLOUDFORMATION  # pylint: disable=global-statement
    CLOUDFORMATION = boto3.client('cloudformation')

    stacks = []
    response = CLOUDFORMATION.list_stacks()
    while True:
        for stack in response['StackSummaries']:
            color = 'green'
            if 'FAILED' in stack['StackStatus']:
                color = 'red'
            elif 'ROLLBACK' in stack['StackStatus']:
                color = 'yellow'
            elif 'IN_PROGRESS' in stack['StackStatus']:
                color = 'blue'

            if stack['StackStatus'] != 'DELETE_COMPLETE':
                stacks += [
                    {
                        'name': stack['StackName'],
                        'status': colored(stack['StackStatus'], color),
                        'date': str(stack.get('LastUpdatedTime', stack['CreationTime'])),
                    }
                ]

        if 'NextToken' in response:
            response = CLOUDFORMATION.list_stacks(
                NextToken=response['NextToken']
            )
        else:
            break

    LOG.debug(json.dumps(stacks, indent=2, default=str))
    cftcli.common.display_table(stacks, 'Stacks')
    CACHE.close()


if __name__ == '__main__':
    _main()
