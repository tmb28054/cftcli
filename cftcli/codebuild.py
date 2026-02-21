#!env python
"""
    I manage adhoc codebuilds
"""


# python libraries
import argparse
# import json
import logging
import os
import time
from urllib.parse import urlparse


import boto3
import diskcache
from halo import Halo
from termcolor import colored


# import cftcli.common


LOG = logging.getLogger()
TIME_DELAY = 3
CACHE = diskcache.Cache('~/.cftcli')
CACHETIME = 60 * 60 * 8  # Cache for 8 hours


CODEBUILD =  boto3.client('codebuild')
S3CLIENT = boto3.client('s3')


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
    parser.add_argument('--src-artifact', '-s', '--src',
                        required=False,
                        dest='src_artifact',
                        default='',
                        help='The source artifact to use.')
    parser.add_argument('--dst-artifact', '-d', '--dst',
                        required=False,
                        dest='dst_artifact',
                        default='',
                        help='The destination artifact')
    parser.add_argument('--profile', '-p',
                        required=False,
                        dest='profile',
                        default='default',
                        help='The profile to use.')
    parser.add_argument('--region',
                        required=False,
                        dest='region',
                        default='us-east-1',
                        help='Region to use.')
    parser.add_argument('-v', '--verbose',  '--debug',
                        dest='verbosity',
                        action='count',
                        default=0,
                        help="Use multiple times to increase logging level")
    parser.add_argument('--codebuild', '--project',
                        required=False,
                        dest='codebuild',
                        default=os.getenv('CODEBUILD', CACHE.get('codebuild', 'DefaultCodeBuild')),
                        help='What codebuild to use.')
    parser.add_argument('--buildspec', '-b',
                        required=False,
                        dest='buildspec',
                        default=os.getenv('BUILDSPEC', CACHE.get('buildspec', '')),
                        help="The filename to use.")
    parser.add_argument('--rolearn', '-r',
                         dest='rolearn',
                         required=False,
                         default=os.getenv('ROLEARN', CACHE.get('rolearn', '')),
                         help='A comma delimited list ie foo=bar,cat=dog')
    parser.add_argument('--bucket',
                         dest='bucket',
                         required=False,
                         default=os.getenv('BUCKET', CACHE.get('bucket', '')),
                         help='the build bucket to use')
    parser.add_argument('--bucket-path',
                         dest='bucket_path',
                         required=False,
                         default=os.getenv('BUCKETPATH', CACHE.get('bucket_path', 'cftcli')),
                         help='the build bucket to use')
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


def save_cache(args) -> None:
    """Write arguments to cache.
    
    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    CACHE.add('profile', args.profile, CACHETIME)
    CACHE.add('buildspec', args.buildspec, CACHETIME)
    CACHE.add('region', args.region, CACHETIME)
    CACHE.add('codebuild', args.codebuild, CACHETIME)
    CACHE.add('rolearn', args.rolearn, CACHETIME)
    CACHE.add('src_artifact', args.src_artifact, CACHETIME)
    CACHE.add('dst_artifact', args.dst_artifact, CACHETIME)
    CACHE.add('bucket', args.bucket, CACHETIME)
    CACHE.add('bucket_path', args.bucket_path, CACHETIME)


def watch_build(build_id:str):
    """Watch the build and wait for it to finish.

    Args:
        build_id (str): The CodeBuild build ID to watch.
        
    Returns:
        dict: The final build record.
    """
    build = CODEBUILD.batch_get_builds(ids=[build_id])['builds'][0]

    while not build['buildComplete']:
        status = build['buildStatus']
        project = build['projectName']
        phase = build['currentPhase']
        if status != 'IN_PROGRESS' or phase == 'COMPLETED':
            break
        spinner_text = f'{project} is {status} under {phase}'
        spinner = Halo(text=spinner_text, spinner='dots')
        spinner.start()

        tracker = '-'.join([status, phase])
        while tracker == '-'.join([status, phase]):
            time.sleep(TIME_DELAY)
            build = CODEBUILD.batch_get_builds(ids=[build_id])['builds'][0]
            project = build['projectName']
            phase = build['currentPhase']

        spinner.stop()
        build = CODEBUILD.batch_get_builds(ids=[build_id])['builds'][0]

    color = 'green'
    if phase != 'COMPLETED':
        color = 'red'
    status = colored(phase, color)

    print(f'build complete with status {status}')

    # try:
    s3_arn = build['logs']['cloudWatchLogsArn'].split(':')
    client = boto3.client('logs')
    response = client.get_log_events(
        logGroupName=s3_arn[6],
        logStreamName=s3_arn[8]
    )
    for event in response['events']:
        print(
            event['message'].strip().strip('[Container]')
        )
    # except:
    #     print('no logs')

    # print(json.dumps(build, indent=2, default=str))
    return build


def s3arn_to_s3url(s3arn:str) -> str:
    """Convert an S3 object ARN to S3 URL.

    Args:
        s3arn (str): S3 ARN (e.g., arn:aws:s3:::bucket/folder/object).

    Returns:
        str: S3 URL (e.g., s3://bucket/folder/object).
    """
    return f"s3://{s3arn.split(':')[-1]}"


def download_artifact(s3_arn:str, filename:str) -> str:
    """Download the artifact to a local file.

    Args:
        s3_arn (str): The S3 ARN of the object to download.
        filename (str): The filename to download to.

    Returns:
        str: Status message indicating success or failure.
    """
    s3_url = s3arn_to_s3url(s3_arn)
    obj = urlparse(s3_url)
    try:
        bucket = obj.netloc
        key = obj.path.lstrip('/')
        S3CLIENT.download_file(bucket, key, filename)
        return f"Download of {filename} {colored('SUCCESS', 'green')}"
    except Exception as err:
        LOG.debug('failed to download %s: %s', filename, err)

    return f"Download of {s3_url} {colored('FAILED', 'red')}"


def _main() -> None:
    """Main entry point for codebuild command."""
    args = _options()
    save_cache(args)

    # set_level(args.verbosity)
    logging.getLogger().setLevel(logging.DEBUG)

    boto3.setup_default_session(
        profile_name=args.profile,
        region_name=args.region,
    )
    global CODEBUILD, S3CLIENT  # pylint: disable=global-statement
    CODEBUILD = boto3.client('codebuild')
    S3CLIENT = boto3.client('s3')

    kwargs = {
        'projectName': args.codebuild,
        'artifactsOverride': {
            'type': 'NO_ARTIFACTS',
        },
        'buildspecOverride': load_file(args.buildspec),
        'sourceTypeOverride': 'NO_SOURCE',
        'sourceLocationOverride': '',
    }

    if args.dst_artifact:
        kwargs['artifactsOverride'] = {
            'type': 'S3',
            'bucketOwnerAccess': 'FULL',
            'location': args.bucket,
            'packaging': 'ZIP',
            'overrideArtifactName': True,
            'artifactIdentifier': 'NONE',
            'path': args.bucket_path,
            'name': f'{args.codebuild}.zip'
        }

    if args.src_artifact:
        kwargs['sourceTypeOverride'] = 'S3'
        kwargs['sourceLocationOverride'] = args.src_artifact

    # print(json.dumps(kwargs, indent=2))

    result = CODEBUILD.start_build(**kwargs)

    build = watch_build(result['build']['id'])
    if build.get('artifacts', False):
        print(
            download_artifact(
                build['artifacts']['location'],
                args.dst_artifact
            )
        )
    CACHE.close()


if __name__ == '__main__':
    _main()
