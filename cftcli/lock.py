#!/usr/bin/env python3
"""Apply stack policy and termination protection to CloudFormation stacks."""

from __future__ import annotations

import argparse
import json

import boto3

from cftcli.utils import LOG, CACHE, setup_session, add_stack_argument, add_common_arguments


CLOUDFORMATION = None

LOCK_POLICY = {
    'Statement': [
        {
            'Effect': 'Allow',
            'Action': 'Update:*',
            'Principal': '*',
            'Resource': '*',
        },
        {
            'Effect': 'Deny',
            'Action': 'Update:*',
            'Principal': '*',
            'Resource': '*',
        },
    ],
}


def _options() -> argparse.Namespace:
    """Provide the argparse option set.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    add_stack_argument(parser)
    add_common_arguments(parser)
    return parser.parse_args()


def _main() -> None:
    """Main entry point for lock-stack command."""
    args = _options()

    setup_session(args)

    global CLOUDFORMATION  # pylint: disable=global-statement
    CLOUDFORMATION = boto3.client('cloudformation')

    response = CLOUDFORMATION.set_stack_policy(
        StackName=args.stackname,
        StackPolicyBody=json.dumps(LOCK_POLICY),
    )
    LOG.debug(json.dumps(response, indent=2, default=str))
    print(f'Policy lock applied for {args.stackname}')

    response = CLOUDFORMATION.update_termination_protection(
        StackName=args.stackname,
        EnableTerminationProtection=True,
    )
    LOG.debug(json.dumps(response, indent=2, default=str))
    print(f'Termination Protection for {args.stackname} enabled')
    CACHE.close()


if __name__ == '__main__':
    _main()
