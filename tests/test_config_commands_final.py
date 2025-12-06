"""
Final tests for config commands to achieve 100% coverage

Tests for remaining uncovered lines (87-94 - IOError/OSError/PermissionError handling).
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os

from wapi.commands.config import cmd_config_set
from wapi.constants import EXIT_ERROR
from wapi.exceptions import WAPIConfigurationError


class TestConfigCommandsFinal(unittest.TestCase):
    """Final tests for config commands"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()

    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_set_io_error(self, mock_get_logger):
        """Test cmd_config_set with IOError (line 87-90)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'test.env'
        self.mock_args.key = 'WAPI_USERNAME'
        self.mock_args.value = 'test@example.com'
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp.write('WAPI_PASSWORD=oldpass\n')
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            # Mock open to raise IOError during write
            call_count = [0]
            original_open = open
            def mock_open_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    # First call: read existing file
                    return original_open(tmp_path, 'r', encoding='utf-8')
                else:
                    # Second call: write - raise IOError
                    raise IOError("Disk full")
            
            with patch('builtins.open', side_effect=mock_open_side_effect):
                with self.assertRaises(WAPIConfigurationError):
                    result = cmd_config_set(self.mock_args, None)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_set_os_error(self, mock_get_logger):
        """Test cmd_config_set with OSError (line 87-90)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'test.env'
        self.mock_args.key = 'WAPI_USERNAME'
        self.mock_args.value = 'test@example.com'
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp.write('WAPI_PASSWORD=oldpass\n')
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            # Mock open to raise OSError during write
            call_count = [0]
            original_open = open
            def mock_open_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    # First call: read existing file
                    return original_open(tmp_path, 'r', encoding='utf-8')
                else:
                    # Second call: write - raise OSError
                    raise OSError("No space left on device")
            
            with patch('builtins.open', side_effect=mock_open_side_effect):
                with self.assertRaises(WAPIConfigurationError):
                    result = cmd_config_set(self.mock_args, None)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_set_permission_error(self, mock_get_logger):
        """Test cmd_config_set with PermissionError (line 87-90)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'test.env'
        self.mock_args.key = 'WAPI_USERNAME'
        self.mock_args.value = 'test@example.com'
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp.write('WAPI_PASSWORD=oldpass\n')
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            # Mock open to raise PermissionError during write
            call_count = [0]
            original_open = open
            def mock_open_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    # First call: read existing file
                    return original_open(tmp_path, 'r', encoding='utf-8')
                else:
                    # Second call: write - raise PermissionError
                    raise PermissionError("Permission denied")
            
            with patch('builtins.open', side_effect=mock_open_side_effect):
                with self.assertRaises(WAPIConfigurationError):
                    result = cmd_config_set(self.mock_args, None)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == '__main__':
    unittest.main()
