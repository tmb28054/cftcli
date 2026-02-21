"""Tests for cftcli package."""

import unittest
import tempfile
import os
from cftcli import __version__
from cftcli.__version__ import get_version


class TestVersion(unittest.TestCase):
    """Test version information."""

    def test_version_exists(self):
        """Test that version is defined."""
        self.assertIsNotNone(__version__)
        self.assertNotEqual(__version__, 'unknown')

    def test_version_format(self):
        """Test version follows semantic versioning."""
        parts = __version__.split('.')
        self.assertGreaterEqual(len(parts), 2)

    def test_get_version_function(self):
        """Test get_version function with mock CHANGELOG."""
        changelog_content = '''# Changelog

## [1.2.3] - 2024-01-01

### Added
- New feature
'''
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md', encoding='utf8') as f:
            f.write(changelog_content)
            temp_path = f.name
        
        try:
            # Temporarily replace CHANGELOG.md path
            import cftcli.__version__ as version_module
            original_open = open
            
            def mock_open(filename, *args, **kwargs):
                if 'CHANGELOG.md' in filename:
                    return original_open(temp_path, *args, **kwargs)
                return original_open(filename, *args, **kwargs)
            
            with unittest.mock.patch('builtins.open', mock_open):
                version = get_version()
                self.assertEqual(version, '1.2.3')
        finally:
            os.unlink(temp_path)

    def test_get_version_no_version(self):
        """Test get_version returns unknown when no version found."""
        changelog_content = '''# Changelog

## [Unreleased]

### Added
- Future feature
'''
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md', encoding='utf8') as f:
            f.write(changelog_content)
            temp_path = f.name
        
        try:
            original_open = open
            
            def mock_open(filename, *args, **kwargs):
                if 'CHANGELOG.md' in filename:
                    return original_open(temp_path, *args, **kwargs)
                return original_open(filename, *args, **kwargs)
            
            with unittest.mock.patch('builtins.open', mock_open):
                version = get_version()
                self.assertEqual(version, 'unknown')
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
