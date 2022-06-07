#!env python
"""
    I assume a role and save it to ~/.aws/credentials
"""


# python libraries
import argparse
import getpass
import json
import logging


import boto3
from cftcli.cli import apply_config


LOG = logging.getLogger()


def _options() -> object:
    """
        I provide the argparse option set.

        Returns
            argparse parser object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-profile',  '--src-profile', '-s',
                        dest='src_profile',
                        required=False,
                        default='',
                        help='The profile to use when assuming the role.')
    parser.add_argument('--dest-profile', '-d',
                        required=False,
                        dest='dst_profile',
                        default='',
                        help='The profile to write after assuming the role.')
    parser.add_argument('--region',
                        required=False,
                        default='us-east-1',
                        help='Region to configure.  Example: us-east-1')
    parser.add_argument('-v', '--verbose',
                        dest='verbosity',
                        action='count',
                        default=0,
                        help="Use multiple times to increase logging level")
    parser.add_argument('--role-arn', '--role', '-r',
                        required=True,
                        dest='rolearn',
                        default='',
                        help="what role to assume")
    return parser.parse_args()


def _main() -> None:
    """ main
    """
    args = _options()
    if args.src_profile:
        boto3.setup_default_session(profile_name=args.src_profile)

    client = boto3.client('sts')
    LOG.info('Assuming the role %s', args.rolearn)
    token = client.assume_role(
        RoleArn=args.rolearn,
        RoleSessionName=getpass.getuser()
    )

    if args.dst_profile:
        kwargs = {
            'profile': args.dst_profile,
            'region': args.region
        }
        apply_config(token, **kwargs)

    else:
        print(
            json.dumps(
                {
                    'aws_access_key_id': token['Credentials']['AccessKeyId'],
                    'aws_secret_access_key': token['Credentials']['SecretAccessKey'],
                    'aws_session_token': token['Credentials']['SessionToken'],
                    'region': kwargs['region'],
                }
            )
        )

if __name__ == '__main__':
    _main()
