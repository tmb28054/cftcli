#!/usr/bin/env python3
"""List all CodePipeline pipelines in a region."""

from __future__ import annotations

import argparse
import json

import boto3
from termcolor import colored

import cftcli.common
from cftcli.utils import LOG, CACHE, setup_session, add_common_arguments


INTERFACE = None


STATE_COLOR = {
    'Failed': 'red',
    'Succeeded': 'green',
    'InProgress': 'blue',
}


def _options() -> argparse.Namespace:
    """Provide the argparse option set.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    return parser.parse_args()


def _get_pipeline_state(pipeline: str) -> str:
    """Check the pipeline state.

    Args:
        pipeline (str): Name of the pipeline to check.

    Returns:
        str: 'Failed' if any stage failed, 'InProgress' if any stage is in progress,
            'Succeeded' otherwise.
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
    """Main entry point for list-pipelines command."""
    args = _options()

    setup_session(args)

    global INTERFACE  # pylint: disable=global-statement
    INTERFACE = boto3.client('codepipeline')

    pipelines: list[dict] = []
    response = INTERFACE.list_pipelines()
    while True:
        for pipeline in response['pipelines']:
            color = STATE_COLOR[_get_pipeline_state(pipeline['name'])]
            pipelines += [
                {
                    'Name': colored(pipeline['name'], color),
                }
            ]

        if 'NextToken' in response:
            response = INTERFACE.list_pipelines(
                NextToken=response['NextToken'],
            )
        else:
            break

    LOG.debug(json.dumps(pipelines, indent=2, default=str))
    cftcli.common.display_table(pipelines, 'Pipelines')
    CACHE.close()


if __name__ == '__main__':
    _main()
