#!env python
"""
    I manage cloudformation stacks
"""


# python libraries
import argparse
import json
import logging
import os
import time
import yaml

import boto3
from halo import Halo
from termcolor import colored


import cftcli.common


LOG = logging.getLogger()
TIME_DELAY = 3


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
    parser.add_argument('--stack', '-s',
                        dest='stackname',
                        required=True,
                        default=os.getenv('STACKNAME', ''),
                        help='The Stack Name to use.')
    parser.add_argument('--profile', '-p',
                        required=False,
                        dest='profile',
                        default=os.getenv('AWS_PROFILE', 'default'),
                        help='The profile to use.')
    parser.add_argument('--role', '-r',
                        required=False,
                        dest='role',
                        help='The role to use.')
    parser.add_argument('--region',
                        required=False,
                        dest='region',
                        default=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                        help='Region to use.')
    parser.add_argument('-v', '--verbose',  '--debug',
                        dest='verbosity',
                        action='count',
                        default=0,
                        help="Use multiple times to increase logging level")
    parser.add_argument('--filename', '-f',
                        required=False,
                        dest='filename',
                        default=os.getenv('FILENAME', ''),
                        help="The filename to use.")
    parser.add_argument('--parameters', '--params', '-i',
                         dest='parameters',
                         required=False,
                         default='',
                         help='A comma delimited list ie foo=bar,cat=dog')
    parser.add_argument('--parameter-file',
                         dest='parameter_file',
                         required=False,
                         default='',
                         help='A key value dictionary ie {"foo": "bar"}')
    parser.add_argument('--failure',
                        dest='failure',
                        required=False,
                        default='DO_NOTHING',
                        choices=['DO_NOTHING', 'ROLLBACK', 'DELETE'],
                        help='What to do on failure')
    parser.add_argument('--protected',
                        dest='protected',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Enables Termination Protection')
    return parser.parse_args()


def load_file(filename) -> str:
    """Return the content of the file.

    Args:
        filename (str): Path to the file to load.

    Returns:
        str: File contents.
    """
    with open(filename, encoding='utf8') as file_handler:
        return file_handler.read()


def stack_exist(stackname: str) -> bool:
    """Check if a CloudFormation stack exists.

    Args:
        stackname (str): Name of the stack to check.

    Returns:
        bool: True if the stack exists, False otherwise.
    """
    try:
        result = CLOUDFORMATION.describe_stacks(StackName=stackname)
        LOG.debug('Stack Context Is:')
        LOG.debug(json.dumps(result, indent=2, default=str))
        return True
    except CLOUDFORMATION.exceptions.ClientError as err:
        if 'does not exist' in str(err):
            LOG.debug('Stack does not exist: %s', stackname)
            return False
        raise

def find_current_stack(stacks: list) -> dict:
    """Return the current stack filtering out previous deleted stacks.

    Args:
        stacks (list): List of stack dictionaries.

    Returns:
        dict: The most recently created stack.
    """
    current = {}
    for stack in stacks:
        if not current:
            current = stack
        elif  stack['CreationTime'] > current['CreationTime']:
            current = stack
    return current


def get_stack_state(stackname:str) -> str:
    """Return the stack state.

    Args:
        stackname (str): Name of the stack to get the state for.

    Returns:
        str: Stack status, optionally with in-progress resources.
    """
    try:
        response = CLOUDFORMATION.describe_stacks(StackName=stackname)
        # print(json.dumps(response, default=str, indent=2))
        LOG.debug(json.dumps(response, indent=2, default=str))
        stack = find_current_stack(response['Stacks'])
        state = stack['StackStatus']
        resources = get_inprogress_resources(stackname)
        if resources:
            return f"{state} - {', '.join(resources)}"
        return state
    except Exception as err_msg:
        if f'Stack with id {stackname} does not exist' in str(err_msg):
            return 'DELETE_COMPLETE'
        raise err_msg


def get_inprogress_resources(stackname:str) -> list:
    """Return a list of resources which are IN_PROGRESS.

    Args:
        stackname (str): Name of the stack to build the list from.

    Returns:
        list: Sorted list of logical resource IDs with IN_PROGRESS status.
    """
    result = []
    response = CLOUDFORMATION.describe_stack_resources(StackName=stackname)
    for record in response['StackResources']:
        if 'IN_PROGRESS'.lower() in record['ResourceStatus'].lower():
            result.append(record['LogicalResourceId'])
    return sorted(result)


def get_failed_resources(stackname:str) -> list:
    """Return a list of resources which failed.

    Args:
        stackname (str): Name of the stack to build the list from.

    Returns:
        list: List of dictionaries containing failed resource details.
    """
    result = []
    response = CLOUDFORMATION.describe_stack_resources(StackName=stackname)
    for record in response['StackResources']:
        LOG.debug(json.dumps(record, indent=2, default=str))
        if 'FAILED' in record['ResourceStatus'].upper():
            result.append(
                {
                    'name': record['LogicalResourceId'],
                    'status': record['ResourceStatus'],
                    'reason': record['ResourceStatusReason'],
                }
            )
    return result


def wait_for_stack(stackname:str) -> None:
    """Wait for the stack to complete.

    Args:
        stackname (str): Name of the stack to wait for.
    """
    state = get_stack_state(stackname)
    while True:
        if 'IN_PROGRESS' not in state:
            break

        spinner_text = f'{stackname} is {state}'
        spinner = Halo(text=spinner_text, spinner='dots')
        spinner.start()
        prev_state = state

        while prev_state == state:
            time.sleep(TIME_DELAY)
            state = get_stack_state(stackname)
        spinner.stop()

    bad_states = ['ROLLBACK', 'FAILED']
    if any(x in state for x in bad_states):
        failed_resources = get_failed_resources(stackname)
        LOG.debug(json.dumps(failed_resources, indent=2, default=str))
        cftcli.common.display_table(failed_resources)
        state = colored(state, 'red')
    else:
        state = colored(state, 'green')
    print(f'{stackname} is {state}')


def load_parameters(filename: str) -> list:
    """Load parameters from a JSON or YAML file.

    Args:
        filename (str): Path to the parameter file.

    Returns:
        list: List of parameter dictionaries in CloudFormation format.
        
    Raises:
        ValueError: If file format is not JSON or YAML.
    """
    file_data = load_file(filename)
    result = []
    if filename.lower().endswith('yaml') or filename.lower().endswith('yml'):
        dict_data = yaml.safe_load(file_data)
    elif filename.lower().endswith('json'):
        dict_data = json.loads(file_data)
    else:
        raise ValueError('unable to load parameter-file')

    for key, value in dict_data.items():
        result.append(
                {
                    'ParameterKey': key,
                    'ParameterValue': value
                }

        )
    return result


def fill_in_current_parameters(parameters: list, stack: str) -> list:
    """Populate current stack parameters with UsePreviousValue.
    
    Looks at the current stack and adds any parameters not in the provided
    list with UsePreviousValue set to True.

    Args:
        parameters (list): CloudFormation parameters list.
        stack (str): Stack name to be updated.

    Returns:
        list: Updated CloudFormation parameters list.
    """
    current = []
    for record in parameters:
        current.append(record['ParameterKey'])
    response = CLOUDFORMATION.describe_stacks(StackName=stack)
    for record in response['Stacks'][0].get('Parameters', []):
        if not record['ParameterKey'] in current:
            parameters.append(
                {
                    'ParameterKey': record['ParameterKey'],
                    'UsePreviousValue': True
                }
            )
    return parameters


def _main() -> None:
    """Main entry point for deploy-stack command."""
    args = _options()

    # set_level(args.verbosity)
    logging.getLogger().setLevel(logging.INFO)

    boto3.setup_default_session(
        profile_name=args.profile,
        region_name=args.region,
    )
    global CLOUDFORMATION  # pylint: disable=global-statement
    CLOUDFORMATION = boto3.client('cloudformation')

    capabilities = [
        'CAPABILITY_IAM',
        'CAPABILITY_NAMED_IAM',
        'CAPABILITY_AUTO_EXPAND'
    ]

    # cli paramters
    parameters = []
    if args.parameters:
        for parameter in args.parameters.split(','):
            name, value = parameter.split('=')
            parameters.append(
                {
                    'ParameterKey': name,
                    'ParameterValue': value
                }
            )
    if args.parameter_file:
        parameters += load_parameters(args.parameter_file)

    kwargs = {
        'StackName': args.stackname,
        'TemplateBody': load_file(args.filename),
        'Parameters': parameters,
        'Capabilities': capabilities,
    }
    if args.role:
        kwargs['RoleARN'] = args.role

    if stack_exist(args.stackname):
        kwargs['Parameters'] = \
            fill_in_current_parameters(parameters, args.stackname)
        response = CLOUDFORMATION.update_stack(**kwargs)
    else:
        kwargs['OnFailure'] = args.failure
        kwargs['EnableTerminationProtection'] = args.protected
        response = CLOUDFORMATION.create_stack(**kwargs)

    LOG.debug(json.dumps(response, indent=2, default=2))
    wait_for_stack(args.stackname)


if __name__ == '__main__':
    _main()
