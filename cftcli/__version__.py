def get_version():
    with open('CHANGELOG.md') as f:
        for line in f:
            if line.startswith('## [') and 'unreleased' not in line.lower():
                return line.split(']')[0].split('[')[1]
    return 'unknown'

__version__ = get_version()
