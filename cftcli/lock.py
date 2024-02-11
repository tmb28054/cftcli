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


LOG = logging.getLogger()


CACHE = diskcache.Cache('~/.cftcli')
CACHETIME = 60 * 60 * 8  # Cache for 8 hours

CLOUDFORMATION = boto3.client('cloudformation')

LOCK_POLCIY = \
    {
        'Statement' : [
            {
                'Effect' : 'Allow',
                'Action' : 'Update:*',
                'Principal': '*',
                'Resource' : '*'
            },
            {
                'Effect' : 'Deny',
                'Action' : 'Update:*',
                'Principal': '*',
                'Resource' : '*'
            }
        ]
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
    parser.add_argument('--stack', '-s',
                        dest='stackname',
                        required=True,
                        default='',
                        help='The Stack Name to use.')
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


def _main() -> None:
    """ main
    """
    args = _options()

    # set_level(args.verbosity)
    logging.getLogger().setLevel(logging.DEBUG)

    boto3.setup_default_session(
        profile_name=args.profile,
        region_name=args.region,
    )
    global CLOUDFORMATION  # pylint: disable=global-statement
    CLOUDFORMATION = boto3.client('cloudformation')

    response = CLOUDFORMATION.set_stack_policy(
        StackName=args.stackname,
        StackPolicyBody=json.dumps(LOCK_POLCIY)
    )
    LOG.debug(json.dumps(response, indent=2, default=2))
    print(f'Policy lock applied for {args.stackname}')

    response = CLOUDFORMATION.update_termination_protection(
        StackName=args.stackname,
        EnableTerminationProtection=True
    )
    LOG.debug(json.dumps(response, indent=2, default=2))
    print(f'Termination Protection for {args.stackname} enabled')

if __name__ == '__main__':
    _main()
