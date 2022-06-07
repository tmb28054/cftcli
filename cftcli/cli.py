#!env python
"""
    I provide a federated auth into aws using a bastion account paradigm.
"""


# python libraries
import argparse
import configparser
import getpass
import json
import logging
import os
from pathlib import Path


# external libraries aka not from python
import boto3
import diskcache
from tabulate import tabulate


CACHE = diskcache.Cache('~/.bauth')
LOG = logging.getLogger()


ACCOUNT_LIST_FILE = 'accounts/AccountsByName.json'
BUCKET = 'botthouse-canonical-us-east-1'
CACHE = diskcache.Cache('~/.validator')


try:
    boto3.setup_default_session(profile_name='bastion')
except:  # pylint: disable=bare-except
    pass


def set_level(verbosity=0):
    """
        Sets the logging level based on verbosity.

    Args
        verbosity: integer value of 0, 1, or 2
            0 - informational
            1 - debug logs from authaws
            2 - debug logs including boto3

    Returns
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
    LOG.setLevel(level)


def _load_config(filepath, filename, profile) -> object:
    """
        I ensure the path and file exists, and return the contents if it does.

        Args
            filepath: String of the file path, generally ~/.aws
            filename: The filename to review
            profile: The profile we are managing

        Return
            The config object with a cleared section for the profile we are adding.
    """
    # init our config object
    config = configparser.ConfigParser()

    # if the directory doesn't exist make it.
    if not os.path.exists(filepath):
        LOG.debug('Creating Directory %s', filepath)
        os.makedirs(filepath)
        return config

    # if the file doesn't exist make it.
    config_file = f'{filepath}/{filename}'
    if not os.path.exists(config_file):
        LOG.debug('No config file not loaded')
        return config

    # Load Config
    config.read(config_file)

    # remove new profile section if it exists
    if config.has_section(profile):
        config.remove_section(profile)

    return config


def apply_config(token, **kwargs) -> None:
    """
        I apply the token to the aws profile configuration.

        Args
            token: an sts object for the credentials of the session.
            kwargs: the session configuration, requiring the region and profile keys.
                region: string of the region to configure.
                profile: string of the profile to configure.
    """
    apply = {
        'aws_access_key_id': token['Credentials']['AccessKeyId'],
        'aws_secret_access_key': token['Credentials']['SecretAccessKey'],
        'aws_session_token': token['Credentials']['SessionToken'],
        'region': kwargs['region'],
    }
    LOG.debug(json.dumps(apply))
    profile = kwargs['profile']

    # home_path is either the environment value of 'HOME' or 'USERPROFILE' or ''
    aws_path = f"{Path.home()}/.aws/"

    # Load Configs
    credentials = _load_config(aws_path, 'credentials', profile)
    config = _load_config(aws_path, 'config', profile)
    credentials.add_section(profile)
    config.add_section(profile)

    # list what keys go in config, all others will go in credentials
    config_keys = ['region']
    for key, value in apply.items():

        # the apply dict has both config and credentials key values.
        # the config_keys has the keys which we will store in config,
        # all other values are stored in credentials.
        if key in config_keys:
            config.set(profile, key, value)
        else:
            credentials.set(profile, key, value)

    # write config
    with open(f'{aws_path}config', 'w', encoding='utf-8') as handler:
        config.write(handler)

    # write credentials
    with open(f'{aws_path}credentials', 'w', encoding='utf-8') as handler:
        credentials.write(handler)


def _get_account_list() -> None:
    """
        I fetch the account list from the canonical bucket.

        Returns
            dict of account list
            {
                "Sandbox": {
                    "Id": "808140515775",
                },
                "Validator": {
                    "Id": "885220705533",
                },
            }
    """
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(
        Bucket=BUCKET,
        Key=ACCOUNT_LIST_FILE
    )
    return json.loads(
        obj['Body'].read().decode('utf8').lower()
    )


def _options(account_list) -> object:
    """
        I provide the argparse option set.

        Args
            account_list: dict of the account list
                {
                    "Sandbox": {
                        "Id": "808140515775",
                    },
                    "Validator": {
                        "Id": "885220705533",
                    },
                }

        Returns
            argparse parser object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', '-p',
                        required=False,
                        default='default',
                        help='AWS profile to steward.')
    parser.add_argument('--region',
                        required=False,
                        default='us-east-1',
                        help='Region to configure.  Example: us-east-1')
    parser.add_argument('-v', '--verbose',
                        dest='verbosity',
                        action='count',
                        default=0,
                        help="Use multiple times to increase logging level")
    parser.add_argument('--rolename',
                        required=False,
                        dest='rolename',
                        default='topaz',
                        help="what role to assume")
    parser.add_argument('--list',
                        required=False,
                        dest='list',
                        default=False,
                        action='store_true',
                        help="print a list of account")
    parser.add_argument('--account', '-a',
                        required=False,
                        dest='account',
                        default='',
                        choices=account_list.keys(),
                        help="What account to assume a role in?")
    parser.add_argument('--purge',
                        required=False,
                        dest='purge',
                        action='store_true',
                        default=False,
                        help="Purge Cache?")
    return parser.parse_args()


def _main() -> None:
    """
        Main Logic
    """
    # By default lets log at info
    logging.basicConfig(level=logging.INFO)
    account_list = _get_account_list()
    args = _options(account_list)
    set_level(args.verbosity)

    if args.purge:
        CACHE.clear()

    if args.list:
        result = [['Name', 'AccountId']]
        for key in account_list.keys():
            record = account_list[key]
            new_record = [
                record['name'],
                record['id']
            ]
            result.append(new_record)
        print(tabulate(result, headers='firstrow'))

    if args.account:
        account_id = account_list[args.account]['id']
        role = f'arn:aws:iam::{account_id}:role/{args.rolename}'

        client = boto3.client("sts")
        token = client.assume_role(
            RoleArn=role,
            RoleSessionName=getpass.getuser()
        )
        kwargs = {
            'profile': args.profile,
            'region': args.region
        }
        apply_config(token, **kwargs)

    CACHE.close()


if __name__ == '__main__':
    _main()
