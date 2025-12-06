"""
Complete tests for config commands to achieve 100% coverage

Tests for remaining uncovered lines (67, 87-94).
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os

from wapi.commands.config import cmd_config_set
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR
from wapi.exceptions import WAPIConfigurationError


class TestConfigCommandsComplete(unittest.TestCase):
    """Complete tests for config commands"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()

    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_set_exception_handling(self, mock_get_logger):
        """Test cmd_config_set with Exception (line 91-94)"""
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
            # Mock open to raise Exception during write (not IOError/OSError/PermissionError)
            # First open (read) succeeds, second open (write) raises Exception
            call_count = [0]
            original_open = open
            def mock_open_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    # First call: read existing file
                    return original_open(tmp_path, 'r', encoding='utf-8')
                else:
                    # Second call: write - raise Exception
                    raise Exception("Unexpected error")
            
            with patch('builtins.open', side_effect=mock_open_side_effect):
                result = cmd_config_set(self.mock_args, None)
                
                # Should return EXIT_ERROR for unexpected exceptions
                self.assertEqual(result, EXIT_ERROR)
                # Verify logger was called
                mock_logger.error.assert_called()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_set_empty_line_handling(self, mock_get_logger):
        """Test cmd_config_set with empty lines and comments (line 67)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'test.env'
        self.mock_args.key = 'WAPI_USERNAME'
        self.mock_args.value = 'test@example.com'
        
        # Use temporary file with comments and empty lines
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp.write('# Comment\n')
            tmp.write('\n')  # Empty line
            tmp.write('WAPI_PASSWORD=oldpass\n')
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            result = cmd_config_set(self.mock_args, None)
            
            self.assertEqual(result, EXIT_SUCCESS)
            
            # Verify file was written correctly
            with open(tmp_path, 'r') as f:
                content = f.read()
                # Should contain the new value
                self.assertIn('WAPI_USERNAME', content)
                # Comments and empty lines should be preserved or handled
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == '__main__':
    unittest.main()
