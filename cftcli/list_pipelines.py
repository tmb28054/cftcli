#!env python
"""
    I manage cloudformation stacks
"""


# python libraries
import argparse
import json
import logging
import os


import boto3
import diskcache
from termcolor import colored


import cftcli.common


LOG = logging.getLogger()
TIME_DELAY = 3
CACHE = diskcache.Cache('~/.cftcli')
CACHETIME = 60 * 60 * 8  # Cache for 8 hours


INTERFACE = boto3.client('codepipeline')


STATE_COLOR = {
    'Failed': 'red',
    'Succeeded': 'green',
    'InProgress': 'blue',
}


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
    return parser.parse_args()

def _get_pipeline_state(pipeline:str) -> str:
    """
        I check the pipeline state

        Returns string
            'Failed': if the job is failed
            'InProgress': if the job is InProgress
            'Succeeded': if there is not other return result.
    """
    stages = INTERFACE.get_pipeline_state(name=pipeline)['stageStates']
    for context in stages:
        stage = context['latestExecution']
        if stage['status'] in ['Failed', 'Cancelled', 'Stopped', 'Stopping']:
            return 'Failed'
        if stage['status'] in ['InProgress']:
            return 'InProgress'

    return 'Succeeded'


def _main() -> None:
    """ main
    """
    args = _options()

    set_level(args.verbosity)
    logging.getLogger().setLevel(logging.DEBUG)

    if args.profile:
        boto3.setup_default_session(profile_name=args.src_profile)
        global INTERFACE  # pylint: disable=global-statement
        INTERFACE = boto3.client('codepipeline')

    pipelines = []
    response = INTERFACE.list_pipelines()
    while True:
        for pipeline in response['pipelines']:
            color = STATE_COLOR[_get_pipeline_state(pipeline['name'])]
            pipelines += [
                {
                    'Name': colored(pipeline['name'], color)
                }
            ]

        if 'NextToken' in response:
            response = INTERFACE.list_pipelines(
                NextToken=response['NextToken']
            )

        else:
            break

    LOG.debug(json.dumps(pipelines, indent=2, default=str))
    cftcli.common.display_table(pipelines, 'Pipelines')


if __name__ == '__main__':
    _main()
    CACHE.close()
