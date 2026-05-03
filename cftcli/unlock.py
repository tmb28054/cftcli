#!/usr/bin/env python3
"""Remove stack policy restrictions and termination protection."""


import argparse
import json

import boto3

from cftcli.utils import LOG, CACHE, setup_session, add_common_arguments


CLOUDFORMATION = None

UNLOCK_POLICY = {
    'Statement': [
        {
            'Effect': 'Allow',
            'Action': 'Update:*',
            'Principal': '*',
            'Resource': '*'
        }
    ]
}


def _options() -> argparse.Namespace:
    """Provide the argparse option set.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--stack', '-s',
                        dest='stackname',
                        required=True,
                        default='',
                        help='The Stack Name to use.')
    add_common_arguments(parser)
    return parser.parse_args()


def _main() -> None:
    """Main entry point for unlock-stack command."""
    args = _options()

    setup_session(args)

    global CLOUDFORMATION  # pylint: disable=global-statement
    CLOUDFORMATION = boto3.client('cloudformation')

    response = CLOUDFORMATION.set_stack_policy(
        StackName=args.stackname,
        StackPolicyBody=json.dumps(UNLOCK_POLICY),
    )
    LOG.debug(json.dumps(response, indent=2, default=str))
    print(f'Policy lock removed for {args.stackname}')

    response = CLOUDFORMATION.update_termination_protection(
        StackName=args.stackname,
        EnableTerminationProtection=False
    )
    LOG.debug(json.dumps(response, indent=2, default=str))
    print(f'Termination Protection for {args.stackname} disabled')
    CACHE.close()


if __name__ == '__main__':
    _main()
