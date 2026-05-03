#!/usr/bin/env python3
"""Display current CloudFormation stack policy."""

from __future__ import annotations

import argparse
import json

import boto3

from cftcli.utils import LOG, CACHE, setup_session, add_stack_argument, add_common_arguments


CLOUDFORMATION = None


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
    """Main entry point for stack-policy command."""
    args = _options()

    setup_session(args)

    global CLOUDFORMATION  # pylint: disable=global-statement
    CLOUDFORMATION = boto3.client('cloudformation')

    response = CLOUDFORMATION.get_stack_policy(
        StackName=args.stackname,
    )
    policy = json.loads(response.get('StackPolicyBody', '{}'))
    LOG.debug(json.dumps(response, indent=2, default=str))
    print(json.dumps(policy, indent=2, default=str))
    CACHE.close()


if __name__ == '__main__':
    _main()
