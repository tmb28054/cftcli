"""Version information for cftcli package."""

import os


def get_version() -> str:
    """Extract the latest version from CHANGELOG.md.

    Returns:
        str: Version string from the first non-unreleased entry in CHANGELOG.md,
            or 'unknown' if not found.
    """
    changelog = os.path.join(os.path.dirname(__file__), '..', 'CHANGELOG.md')
    with open(changelog) as f:
        for line in f:
            if line.startswith('## [') and 'unreleased' not in line.lower():
                return line.split(']')[0].split('[')[1]
    return 'unknown'


__version__ = get_version()
