"""Version information for cftcli package."""

def get_version():
    """Extract the latest version from CHANGELOG.md.
    
    Returns:
        str: Version string from the first non-unreleased entry in CHANGELOG.md,
            or 'unknown' if not found.
    """
    with open('CHANGELOG.md') as f:
        for line in f:
            if line.startswith('## [') and 'unreleased' not in line.lower():
                return line.split(']')[0].split('[')[1]
    return 'unknown'

__version__ = get_version()
