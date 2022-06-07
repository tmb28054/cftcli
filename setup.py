#!/usr/bin/env python
"""
    I provide a package setup for the egg.
"""


from setuptools import setup


def get_requirements() -> list:
    """
        I generate a list of requirements from the requirements.txt
    """
    with open('requirements.txt', encoding='utf8') as file_handler:
        return file_handler.read().split("\n")


def get_changelog() -> str:
    """
        I return the version from changelog.

        Args
        None

        Returns
        str: string form of the current verion.
    """
    with open('CHANGELOG.md', encoding='utf8') as file_handler:
        for line in file_handler:
            if line.startswith('## ['):
                if 'unreleased' not in line.lower():
                    left = line.split(']')[0]
                    return left.split('[')[1]
    return 'unknown'


NAME = 'cftcli'
with open('README.md', encoding='utf8') as readme_handler:
    README = readme_handler.read()


setup_options = dict(
    name=NAME,
    version=get_changelog(),
    description='CloudFormation Cli',
    long_description=README,
    author='Topaz Bott',
    author_email='topaz@topazhome.net',
    url='https://github.com/tmb28054/cftcli',
    scripts=[],
    package_data={
        NAME: []
    },
    entry_points={
        'console_scripts': [
            'cfdeploy = cftcli.deploy:_main',
            'create-stack = cftcli.deploy:_main',
            'deploy-stack = cftcli.deploy:_main',
            'update-stack = cftcli.deploy:_main',
            'delete-stack = cftcli.destroy:_main',
            'list-stacks = cftcli.list:_main',
            'stack-detail = cftcli.detail:_main',
            'describe-stack = cftcli.detail:_main',
        ]
    },
    packages=[NAME],
    include_package_data=True,
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

setup(**setup_options)
