#!env python
"""Read an AWS Secrets Manager secret and output shell export statements."""

import argparse
import json
import sys
import boto3


def get_secret(secret_arn: str, profile: str, region: str) -> dict:
    """Retrieve and parse a secret from AWS Secrets Manager.

    Args:
        secret_arn (str): The ARN of the secret to retrieve.
        profile (str): AWS profile name.
        region (str): AWS region name.

    Returns:
        dict: Key/value pairs from the secret.

    Raises:
        ValueError: If the secret value is not valid JSON.
    """
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_arn)
    secret_string = response['SecretString']
    try:
        return json.loads(secret_string)
    except json.JSONDecodeError as err:
        raise ValueError(f'Secret is not valid JSON: {err}') from err


def _options() -> argparse.Namespace:
    """Provide the argparse option set.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Output AWS Secrets Manager secret as shell export statements.'
    )
    parser.add_argument('secret_arn',
                        help='The ARN of the secret to retrieve.')
    parser.add_argument('--profile', '-p',
                        required=False,
                        dest='profile',
                        default=None,
                        help='The AWS profile to use.')
    parser.add_argument('--region',
                        required=False,
                        dest='region',
                        default=None,
                        help='AWS region to use.')
    return parser.parse_args()


def _main() -> None:
    """Main entry point for secretsmanager-env command."""
    args = _options()
    try:
        secret = get_secret(args.secret_arn, args.profile, args.region)
    except ValueError as err:
        print(f'# Error: {err}', file=sys.stderr)
        sys.exit(1)

    for key, value in secret.items():
        escaped = str(value).replace("'", "'\\''")
        print(f"export {key}='{escaped}'")


if __name__ == '__main__':
    _main()
