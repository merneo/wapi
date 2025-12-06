"""
Complete tests for config module to achieve 100% coverage

Tests for all code paths including edge cases and error handling.
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os

from wapi.config import load_config, get_config, validate_config
from wapi.exceptions import WAPIConfigurationError


class TestConfigComplete(unittest.TestCase):
    """Complete tests for config module"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    @patch('wapi.config.Path')
    def test_load_config_file_not_exists(self, mock_path):
        """Test load_config when file doesn't exist (line 45)"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = False
        mock_path.return_value = mock_path_obj
        
        config = load_config('nonexistent.env')
        
        self.assertEqual(config, {})

    @patch('wapi.config.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='# Comment\nWAPI_USERNAME=test\n\nWAPI_PASSWORD=pass\n')
    def test_load_config_with_comments_and_empty_lines(self, mock_file, mock_path):
        """Test load_config with comments and empty lines (line 45)"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path.return_value = mock_path_obj
        
        config = load_config('test.env')
        
        self.assertEqual(config.get('WAPI_USERNAME'), 'test')
        self.assertEqual(config.get('WAPI_PASSWORD'), 'pass')
        # Comment should be skipped
        self.assertNotIn('#', config)

    @patch('wapi.config.Path')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_load_config_io_error(self, mock_file, mock_path):
        """Test load_config with IOError (line 56-58)"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path.return_value = mock_path_obj
        
        with self.assertRaises(WAPIConfigurationError):
            config = load_config('test.env')

    @patch('wapi.config.Path')
    @patch('builtins.open', side_effect=OSError("OS error"))
    def test_load_config_os_error(self, mock_file, mock_path):
        """Test load_config with OSError (line 56-58)"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path.return_value = mock_path_obj
        
        with self.assertRaises(WAPIConfigurationError):
            config = load_config('test.env')

    @patch('wapi.config.Path')
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_load_config_permission_error(self, mock_file, mock_path):
        """Test load_config with PermissionError (line 56-58)"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path.return_value = mock_path_obj
        
        with self.assertRaises(WAPIConfigurationError):
            config = load_config('test.env')

    @patch('wapi.config.Path')
    @patch('builtins.open', side_effect=Exception("Unexpected error"))
    def test_load_config_unexpected_error(self, mock_file, mock_path):
        """Test load_config with unexpected error (line 56-58)"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path.return_value = mock_path_obj
        
        with self.assertRaises(WAPIConfigurationError):
            config = load_config('test.env')

    @patch('wapi.config.os.getenv')
    @patch('wapi.config.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='WAPI_USERNAME=file_user\n')
    def test_load_config_env_override(self, mock_file, mock_path, mock_getenv):
        """Test load_config with environment variable override (line 65)"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path.return_value = mock_path_obj
        
        # Mock environment variable
        def mock_env(var):
            if var == 'WAPI_USERNAME':
                return 'env_user'
            return None
        
        mock_getenv.side_effect = mock_env
        
        config = load_config('test.env')
        
        # Environment variable should override file
        self.assertEqual(config.get('WAPI_USERNAME'), 'env_user')

    @patch('wapi.config.os.getenv')
    @patch('wapi.config.Path')
    def test_get_config_env_variable(self, mock_path, mock_getenv):
        """Test get_config with environment variable (line 85)"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = False
        mock_path.return_value = mock_path_obj
        
        # Mock environment variable
        def mock_env(var):
            if var == 'WAPI_USERNAME':
                return 'env_user'
            return None
        
        mock_getenv.side_effect = mock_env
        
        value = get_config('WAPI_USERNAME')
        
        self.assertEqual(value, 'env_user')

    @patch('wapi.config.os.getenv')
    @patch('wapi.config.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='WAPI_USERNAME=file_user\n')
    def test_get_config_from_file(self, mock_file, mock_path, mock_getenv):
        """Test get_config from file when env var not set"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path.return_value = mock_path_obj
        
        # Mock environment variable - not set
        mock_getenv.return_value = None
        
        value = get_config('WAPI_USERNAME')
        
        self.assertEqual(value, 'file_user')

    @patch('wapi.config.os.getenv')
    @patch('wapi.config.Path')
    def test_get_config_default_value(self, mock_path, mock_getenv):
        """Test get_config with default value"""
        from pathlib import Path as PathLib
        
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = False
        mock_path.return_value = mock_path_obj
        
        mock_getenv.return_value = None
        
        value = get_config('NONEXISTENT', default='default_value')
        
        self.assertEqual(value, 'default_value')


if __name__ == '__main__':
    unittest.main()
