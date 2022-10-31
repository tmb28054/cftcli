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


import boto3
import diskcache
from halo import Halo
from termcolor import colored


import cftcli.common


LOG = logging.getLogger()
TIME_DELAY = 3


CACHE = diskcache.Cache('~/.cftcli')
CACHETIME = 60 * 60 * 8  # Cache for 8 hours


CLOUDFORMATION = boto3.client('cloudformation')


def set_level(verbosity):
    """Sets the logging level based on command line provided verbosity.

    By default, `botocore` and `urllib3` are quiet and only show logging
    statements at the `ERROR` level.  These logging statements will be showen
    when verbosity is greater than 1 (-vv, -vvv, etc).

    Args:
        verbosity
            0-based level of verbosity provide on CLI

    Returns:
        None
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
    """
        I provide the argparse option set.

        Returns
            argparse parser object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--stack', '-s',
                        dest='stackname',
                        required=True,
                        default=os.getenv('STACKNAME', CACHE.get('stackname', '')),
                        help='The Stack Name to use.')
    parser.add_argument('--profile', '-p',
                        required=False,
                        dest='profile',
                        default=os.getenv('AWS_PROFILE', CACHE.get('profile', '')),
                        help='The profile to use.')
    parser.add_argument('--region',
                        required=False,
                        dest='region',
                        default=os.getenv('AWS_DEFAULT_REGION', CACHE.get('region', '')),
                        help='Region to use.')
    parser.add_argument('-v', '--verbose',  '--debug',
                        dest='verbosity',
                        action='count',
                        default=0,
                        help="Use multiple times to increase logging level")
    parser.add_argument('--filename', '-f',
                        required=False,
                        dest='filename',
                        default=os.getenv('FILENAME', CACHE.get('filename', '')),
                        help="The filename to use.")
    parser.add_argument('--parameters', '--params', '-i',
                         dest='parameters',
                         required=False,
                         default='',
                         help='A comma delimited list ie foo=bar,cat=dog')
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
    """
        I return the content of the file.

        Args
            filename: string of the file to load

        Returns
            string of the file contents
    """
    with open(filename, encoding='utf8') as file_handler:
        return file_handler.read()


def stack_exist(stackname) -> bool:
    """
        I return true if the stack exsits, false if it doesn't.

        Args
            stackname: string of the stack which may or maynot exist.

        Returns
            true: if the stack exists
            false: if the stack does not exist
    """
    try:
        result = CLOUDFORMATION.describe_stacks(StackName=stackname)
        LOG.debug('Stack Context Is:')
        LOG.debug(json.dumps(result, indent=2, default=str))
        return True
    except:  # pylint: disable=bare-except
        LOG.debug('Failed to get stack, presuming does not exist')
        return False


def get_stack_state(stackname:str) -> str:
    """
        I return the stack state.

        Args:
            stackname: string of the stack to get the state for
    """
    try:
        response = CLOUDFORMATION.describe_stacks(StackName=stackname)
        LOG.debug(json.dumps(response, indent=2, default=str))
        state = response['Stacks'][0]['StackStatus']
        resources = get_inprogress_resources(stackname)
        if resources:
            return f"{state} - {', '.join(resources)}"
        return state

    except:  # pylint: disable=bare-except
        return 'DELETE_COMPLETE'


def get_inprogress_resources(stackname:str) -> list:
    """
        I return a list of resources which are IN_PROGRESS.

        Args:
            stackname: string of the stack to build the list from.

        Returns
            list of resources which have a state of IN_PROGRESS
    """
    result = []
    response = CLOUDFORMATION.describe_stack_resources(StackName=stackname)
    for record in response['StackResources']:
        if 'IN_PROGRESS'.lower() in record['ResourceStatus'].lower():
            result.append(record['LogicalResourceId'])
    return sorted(result)


def get_failed_resources(stackname:str) -> list:
    """
        I return a list of resources which failed.

        Args:
            stackname: string of the stack to build the list from.

        Returns
            list of resources which have a state failed
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


def save_cache(args) -> None:
    """
        write the cache
    """
    CACHE.add('stackname', args.stackname, CACHETIME)
    CACHE.add('filename', args.filename, CACHETIME)
    CACHE.add('region', args.region, CACHETIME)
    CACHE.add('filename', args.filename, CACHETIME)


def wait_for_stack(stackname:str) -> None:
    """
        I wait for the stack to complete.

        Args
            stackanme: string of the stackname.
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


def _main() -> None:
    """ main
    """
    args = _options()

    # set_level(args.verbosity)
    logging.getLogger().setLevel(logging.DEBUG)

    if args.profile:
        boto3.setup_default_session(profile_name=args.src_profile)
        global CLOUDFORMATION  # pylint: disable=global-statement
        CLOUDFORMATION = boto3.client('cloudformation')

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

    # blarg
    if stack_exist(args.stackname):
        response = CLOUDFORMATION.update_stack(
            StackName=args.stackname,
            TemplateBody=load_file(args.filename),
            Parameters=parameters,
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM',
                'CAPABILITY_AUTO_EXPAND'
            ],
        )
    else:
        response = CLOUDFORMATION.create_stack(
            StackName=args.stackname,
            TemplateBody=load_file(args.filename),
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM',
                'CAPABILITY_AUTO_EXPAND'
            ],
            Parameters=parameters,
            OnFailure=args.failure,
            EnableTerminationProtection=args.protected
        )
    LOG.debug(json.dumps(response, indent=2, default=2))
    wait_for_stack(args.stackname)
    CACHE.close()


if __name__ == '__main__':
    _main()
