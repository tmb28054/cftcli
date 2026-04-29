"""Custom hatchling build hook to set version from CHANGELOG.md and include it in the wheel."""

import os
import shutil
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def get_version_from_changelog():
    """Extract latest version from CHANGELOG.md.

    Returns:
        str: Version string from the first non-unreleased entry.
    """
    with open('CHANGELOG.md') as f:
        for line in f:
            if line.startswith('## [') and 'unreleased' not in line.lower():
                return line.split(']')[0].split('[')[1]
    return 'unknown'


class CustomBuildHook(BuildHookInterface):
    """Custom build hook to inject CHANGELOG.md and dynamic version."""

    def initialize(self, version, build_data):
        """Run before the build to inject version and extra files.

        Args:
            version (str): The current version string.
            build_data (dict): Build metadata to modify.
        """
        build_data['force_include']['CHANGELOG.md'] = 'CHANGELOG.md'
        build_data['version'] = get_version_from_changelog()
