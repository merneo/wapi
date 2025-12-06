"""
Unit tests for configuration error handling

Tests that config module properly raises WAPIConfigurationError.
"""

import unittest
from unittest.mock import patch, mock_open
import tempfile
import os

from wapi.exceptions import WAPIConfigurationError
from wapi.config import load_config, validate_config


class TestConfigErrorHandling(unittest.TestCase):
    """Test configuration error handling"""

    def test_load_config_file_not_found(self):
        """Test that missing config file doesn't raise error (returns empty dict)"""
        # Non-existent file should return empty dict, not raise
        config = load_config("nonexistent_file.env")
        self.assertIsInstance(config, dict)

    @patch('wapi.config.Path')
    def test_load_config_io_error(self, mock_path):
        """Test that IO errors raise WAPIConfigurationError"""
        mock_path_instance = mock_path.return_value
        mock_path_instance.exists.return_value = True
        mock_path_instance.__truediv__ = lambda self, other: self
        
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with self.assertRaises(WAPIConfigurationError):
                load_config("test.env")

    @patch('wapi.config.Path')
    def test_load_config_permission_error(self, mock_path):
        """Test that permission errors raise WAPIConfigurationError"""
        mock_path_instance = mock_path.return_value
        mock_path_instance.exists.return_value = True
        mock_path_instance.__truediv__ = lambda self, other: self
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with self.assertRaises(WAPIConfigurationError):
                load_config("test.env")

    def test_validate_config_missing_username(self):
        """Test that missing username returns False"""
        with patch('wapi.config.get_config', side_effect=lambda k, **kw: None if k == 'WAPI_USERNAME' else 'password'):
            is_valid, error = validate_config()
            self.assertFalse(is_valid)
            self.assertIn("WAPI_USERNAME", error)

    def test_validate_config_missing_password(self):
        """Test that missing password returns False"""
        with patch('wapi.config.get_config', side_effect=lambda k, **kw: 'user' if k == 'WAPI_USERNAME' else None):
            is_valid, error = validate_config()
            self.assertFalse(is_valid)
            self.assertIn("WAPI_PASSWORD", error)

    def test_validate_config_success(self):
        """Test that valid config returns True"""
        with patch('wapi.config.get_config', side_effect=lambda k, **kw: 'value'):
            is_valid, error = validate_config()
            self.assertTrue(is_valid)
            self.assertIsNone(error)


if __name__ == '__main__':
    unittest.main()
