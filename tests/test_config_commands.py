"""
Unit tests for config command operations

Tests for configuration commands: show, validate, set.
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os

from wapi.commands.config import cmd_config_show, cmd_config_validate, cmd_config_set
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR, EXIT_CONFIG_ERROR
from wapi.exceptions import WAPIConfigurationError


class TestConfigShowCommand(unittest.TestCase):
    """Test config show command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()

    @patch('wapi.commands.config.load_config')
    @patch('wapi.commands.config.format_output')
    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_show_success(self, mock_get_logger, mock_format_output, mock_load_config):
        """Test successful config show command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'table'
        
        mock_config = {
            'WAPI_USERNAME': 'test@example.com',
            'WAPI_PASSWORD': 'secret123',
            'WAPI_BASE_URL': 'https://api.wedos.com/wapi/json'
        }
        mock_load_config.return_value = mock_config
        
        result = cmd_config_show(self.mock_args)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_load_config.assert_called_once_with('config.env')
        mock_format_output.assert_called_once()
        
        # Verify password is filtered
        call_args = mock_format_output.call_args[0]
        output_data = call_args[0]
        self.assertIn('[HIDDEN]', str(output_data))

    @patch('wapi.commands.config.load_config')
    @patch('wapi.commands.config.format_output')
    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_show_empty_config(self, mock_get_logger, mock_format_output, mock_load_config):
        """Test config show with empty config"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'json'
        
        mock_load_config.return_value = {}
        
        result = cmd_config_show(self.mock_args)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format_output.assert_called_once()

    @patch('wapi.commands.config.load_config')
    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_show_config_error(self, mock_get_logger, mock_load_config):
        """Test config show with configuration error"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'table'
        
        mock_load_config.side_effect = WAPIConfigurationError("Cannot read config file")
        
        # cmd_config_show doesn't catch exceptions, it will propagate
        with self.assertRaises(WAPIConfigurationError):
            result = cmd_config_show(self.mock_args)


class TestConfigValidateCommand(unittest.TestCase):
    """Test config validate command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()

    @patch('wapi.commands.config.validate_config')
    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_validate_success(self, mock_get_logger, mock_validate_config):
        """Test successful config validate command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        mock_validate_config.return_value = (True, None)
        
        result = cmd_config_validate(self.mock_args)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_validate_config.assert_called_once_with('config.env')

    @patch('wapi.commands.config.validate_config')
    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_validate_failure(self, mock_get_logger, mock_validate_config):
        """Test config validate with validation failure"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        mock_validate_config.return_value = (False, "Missing WAPI_USERNAME")
        
        result = cmd_config_validate(self.mock_args)
        
        self.assertEqual(result, EXIT_CONFIG_ERROR)
        mock_validate_config.assert_called_once_with('config.env')

    @patch('wapi.commands.config.validate_config')
    @patch('wapi.commands.config.get_logger')
    def test_cmd_config_validate_missing_password(self, mock_get_logger, mock_validate_config):
        """Test config validate with missing password"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        mock_validate_config.return_value = (False, "Missing WAPI_PASSWORD")
        
        result = cmd_config_validate(self.mock_args)
        
        self.assertEqual(result, EXIT_CONFIG_ERROR)


class TestConfigSetCommand(unittest.TestCase):
    """Test config set command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()

    @patch('wapi.commands.config.Path')
    @patch('wapi.commands.config.get_logger')
    @patch('builtins.open', new_callable=mock_open, read_data='WAPI_BASE_URL="https://api.wedos.com/wapi/json"\n')
    def test_cmd_config_set_success(self, mock_file, mock_get_logger, mock_path):
        """Test successful config set command"""
        import tempfile
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp.write('WAPI_BASE_URL="https://api.wedos.com/wapi/json"\n')
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        self.mock_args.key = 'WAPI_USERNAME'
        self.mock_args.value = 'test@example.com'
        
        try:
            # Mock Path to return actual Path object
            from pathlib import Path as PathLib
            mock_path.return_value = PathLib(tmp_path)
            
            result = cmd_config_set(self.mock_args)
            
            self.assertEqual(result, EXIT_SUCCESS)
            # Verify file was opened for writing
            self.assertGreater(mock_file.call_count, 0)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.config.Path')
    @patch('wapi.commands.config.get_logger')
    @patch('builtins.open', new_callable=mock_open)
    def test_cmd_config_set_invalid_key(self, mock_file, mock_get_logger, mock_path):
        """Test config set with any key (config_set accepts any key)"""
        import tempfile
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        self.mock_args.key = 'INVALID_KEY'
        self.mock_args.value = 'value'
        
        try:
            # Mock Path to return actual Path object
            from pathlib import Path as PathLib
            mock_path.return_value = PathLib(tmp_path)
            
            result = cmd_config_set(self.mock_args)
            
            # cmd_config_set accepts any key, so it should succeed
            self.assertEqual(result, EXIT_SUCCESS)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.config.Path')
    @patch('wapi.commands.config.get_logger')
    @patch('builtins.open', new_callable=mock_open)
    def test_cmd_config_set_file_not_exists(self, mock_file, mock_get_logger, mock_path):
        """Test config set when file doesn't exist (creates new file)"""
        import tempfile
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Use non-existent file path
        tmp_path = tempfile.mktemp(suffix='.env')
        
        self.mock_args.config = tmp_path
        self.mock_args.key = 'WAPI_USERNAME'
        self.mock_args.value = 'test@example.com'
        
        try:
            # Mock Path to return actual Path object
            from pathlib import Path as PathLib
            mock_path.return_value = PathLib(tmp_path)
            
            result = cmd_config_set(self.mock_args)
            
            # Should succeed even if file doesn't exist (creates it)
            self.assertEqual(result, EXIT_SUCCESS)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.config.Path')
    @patch('wapi.commands.config.get_logger')
    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_cmd_config_set_password(self, mock_file, mock_get_logger, mock_path):
        """Test config set for password (should be written as [HIDDEN])"""
        import tempfile
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        self.mock_args.key = 'WAPI_PASSWORD'
        self.mock_args.value = 'secret123'
        
        try:
            # Mock Path to return actual Path object
            from pathlib import Path as PathLib
            mock_path.return_value = PathLib(tmp_path)
            
            result = cmd_config_set(self.mock_args)
            
            self.assertEqual(result, EXIT_SUCCESS)
            # Verify file was written
            self.assertGreater(mock_file.call_count, 0)
            # Verify password was written as [HIDDEN]
            written_content = ''.join(call.args[0] for call in mock_file.return_value.write.call_args_list)
            self.assertIn('[HIDDEN]', written_content)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == '__main__':
    unittest.main()
