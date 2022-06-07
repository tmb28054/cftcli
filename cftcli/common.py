#!env python
"""
    I manage cloudformation stacks
"""


import json
import logging


import textwrap
from tabulate import tabulate
from termcolor import colored


LOG = logging.getLogger()


def display_table(records, title='Resources') -> None:
    """ foo
    """
    result = []
    headers = []
    for record in records:
        if not headers:
            headers = record.keys()
        row = []
        for _, value in record.items():
            if len(value) > 50:
                value = textwrap.fill(value, 50)
            if value in ['CREATE_FAILED']:
                value = colored(value, 'red')
            row += [value]
        result += [row]
    LOG.debug(json.dumps(result, indent=2, default=str))
    print(title)
    print(
        tabulate(
            result,
            headers,
            tablefmt="grid"
        )
    )
