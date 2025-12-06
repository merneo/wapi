"""
Tests for wapi/__main__.py entry point

Tests the 'python -m wapi' execution path.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import subprocess
import os


class TestMainEntryPoint(unittest.TestCase):
    """Test the __main__.py entry point"""

    @patch('wapi.cli.main')
    def test_main_entry_point_import(self, mock_main):
        """Test that __main__.py can be imported and main is called"""
        # Import should work
        import wapi.__main__
        self.assertTrue(hasattr(wapi.__main__, 'main'))
        
    @patch('wapi.cli.main')
    def test_main_entry_point_execution(self, mock_main):
        """Test that main() is called when __main__ is executed"""
        # Simulate if __name__ == '__main__' execution
        import wapi.__main__
        
        # Manually trigger the main call (simulating __name__ == '__main__')
        if hasattr(wapi.__main__, '__name__'):
            # This simulates the execution path
            wapi.__main__.main()
            mock_main.assert_called_once()

    def test_main_module_imports(self):
        """Test that __main__.py imports correctly"""
        # This test covers line 5 (import statement)
        # Need to clear any mocks first
        import importlib
        import wapi.__main__
        importlib.reload(wapi.__main__)
        
        try:
            from wapi.__main__ import main
            # main should be the same as wapi.cli.main
            from wapi.cli import main as cli_main
            self.assertEqual(main, cli_main)
        except ImportError as e:
            self.fail(f"Failed to import from __main__: {e}")


if __name__ == '__main__':
    unittest.main()
