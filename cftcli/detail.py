#!env python
"""
    I manage cloudformation stacks
"""


# python libraries
import argparse
import json
import logging
import os
import sys


import textwrap


from tabulate import tabulate
from termcolor import colored


import boto3
import diskcache


LOG = logging.getLogger()
TIME_DELAY = 3


CACHE = diskcache.Cache('~/.cftcli')
CACHETIME = 60 * 60 * 8  # Cache for 8 hours


CLOUDFORMATION = boto3.client('cloudformation')


def set_level(verbosity):
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
        # enable other loggers
        logging.getLogger('botocore').setLevel(logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.DEBUG)
    if verbosity == 1:
        logging.getLogger('botocore').setLevel(logging.INFO)
        logging.getLogger('urllib3').setLevel(logging.INFO)
    level -= 10 * verbosity

    logging.getLogger('validator').setLevel(level)
    if verbosity:
        logging.getLogger().setLevel(logging.DEBUG)


def _options() -> object:
    """Provide the argparse option set.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('stacks', nargs='*', help='What stacks to view')
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
    parser.add_argument('-v', '--verbose',  '--debug',
                        dest='verbosity',
                        action='count',
                        default=0,
                        help="Use multiple times to increase logging level")
    return parser.parse_args()


def _get_events(stackname:str) -> dict:
    """Return a list of the latest events.

    Args:
        stackname (str): Name of the stack to get events for.

    Returns:
        dict: Dictionary of events keyed by PhysicalResourceId.
    """
    events = {}
    response = CLOUDFORMATION.describe_stack_events(StackName=stackname)
    while True:
        for event in response['StackEvents']:
            name = event['PhysicalResourceId']
            if name not in events or event['Timestamp'] > events[name]['Timestamp']:
                events[name] = event
        if not response.get('NextToken', False):
            break
        response = CLOUDFORMATION.describe_stack_events(
            StackName=stackname,
            NextToken=response['NextToken']
        )
    return events


def _get_resources(stackname:str) -> dict:
    """Generate a list of resources for a stack.

    Args:
        stackname (str): Name of the stack.

    Returns:
        dict: Dictionary of resources keyed by LogicalResourceId.
    """
    response = CLOUDFORMATION.describe_stack_resources(
        StackName=stackname
    )
    resources = {}
    while True:
        for resource in response['StackResources']:
            name = resource['LogicalResourceId']
            if name not in resources or resource['Timestamp'] > resource[name]['Timestamp']:
                resources[name] = resource
        if not response.get('NextToken', False):
            break
        response = CLOUDFORMATION.describe_stack_resources(
            StackName=stackname,
            NextToken=response['NextToken']
        )
    return resources


def _disply_resources(resources:dict) -> None:
    """Display a list of resources for a stack.

    Args:
        resources (dict): Dictionary of stack resources.
    """
    display_keys = [
        'LogicalResourceId',
        'PhysicalResourceId',
        'ResourceType',
        'Timestamp',
        'ResourceStatus',
        'ResourceStatusReason',
        'Description',
    ]
    detail = []
    header = []
    for _, resource in resources.items():
        record = []
        if resource['ResourceStatus'] == 'DELETE_COMPLETE':
            continue
        for key, value in resource.items():
            if key not in display_keys:
                continue
            value = str(value)
            if not detail:
                header += [key]
            if key == 'LogicalResourceId':
                value = colored(value, attrs=['bold'])
            elif key == 'ResourceStatus':
                color = 'green'
                if 'PROGRESS' in value:
                    color = 'blue'
                elif 'FAIL' in value:
                    color = 'red'
                value = colored(value, color)
            elif len(value) > 20:
                value = textwrap.fill(value, 20)
            record.append(value)
        detail.append(record)
    LOG.debug(json.dumps(detail, indent=2, default=str))
    print('\n')
    print(colored('Resources', 'green', attrs=['bold']))
    print(
        tabulate(
            detail,
            header,
            tablefmt="grid"
        )
    )


def _display_events(stackname:str) -> None:
    """Print a table of the CloudFormation events for a stack.

    Args:
        stackname (str): Name of the stack.
    """
    detail = []
    header = []
    display_keys = ['LogicalResourceId', 'PhysicalResourceId', 'ResourceType',
                    'Timestamp', 'ResourceStatus', 'ResourceStatusReason',
                    'ResourceProperties']
    resources = _get_resources(stackname)
    for _, event in _get_events(stackname).items():
        event_detail = []
        if event['ResourceStatus'] == 'DELETE_COMPLETE':
            continue
        for key, value in event.items():
            if key not in display_keys:
                continue
            if not detail:
                header += [key]
            value = str(value)
            if key == 'LogicalResourceId':
                value = colored(value, attrs=['bold'])
            elif key == 'ResourceStatus':
                color = 'green'
                if 'PROGRESS' in value:
                    color = 'blue'
                elif 'FAIL' in value:
                    color = 'red'
                value = colored(value, color)
            elif len(value) > 20:
                value = textwrap.fill(value, 20)
            event_detail.append(value)
        detail.append(event_detail)
    LOG.debug(json.dumps(detail, indent=2, default=str))
    print('\nEvents')
    print(
        tabulate(
            detail,
            header,
            tablefmt="grid"
        )
    )
    _disply_resources(resources)


def _display_stack(stackname) -> None:
    """Display the stack data.

    Args:
        stackname (str): The stack name to display.
    """
    detail = []
    response = CLOUDFORMATION.describe_stacks(StackName=stackname)
    for key, value in response['Stacks'][0].items():
        if not value:
            continue
        if type(value) in [dict, list]:
            value = json.dumps(value, default=str, indent=2)
        else:
            value = str(value)
            if len(value) > 50:
                value = textwrap.fill(value, 50)

        if len(key) > 50:
            key = textwrap.fill(key, 50)
        detail.append(
            [
                colored(key, attrs=['bold']),
                value
            ]
        )

    LOG.debug(json.dumps(detail, indent=2, default=str))
    print('Stack Detail')
    print(
        tabulate(
            detail,
            tablefmt="grid"
        )
    )
    _display_events(stackname)


def _main() -> None:
    """Main entry point for describe-stack command."""
    args = _options()

    set_level(args.verbosity)
    logging.getLogger().setLevel(logging.DEBUG)

    stacks = args.stacks
    if not stacks:
        stacks = CACHE.get('stacks', [])

        if not stacks:
            stack = CACHE.get('stackname', '')
            if not stack:
                print('A StackName is required')
                sys.exit(1)
            stacks = [stack]

        stacks = json.loads(stacks)

    boto3.setup_default_session(
        profile_name=args.profile,
        region_name=args.region,
    )
    global CLOUDFORMATION  # pylint: disable=global-statement
    CLOUDFORMATION = boto3.client('cloudformation')

    for stack in stacks:
        _display_stack(stack)

    CACHE.add('stacks', json.dumps(stacks), CACHETIME)
    CACHE.add('region', args.region, CACHETIME)
    if args.profile:
        CACHE.add('profile', args.profile, CACHETIME)


if __name__ == '__main__':
    _main()
    CACHE.close()
