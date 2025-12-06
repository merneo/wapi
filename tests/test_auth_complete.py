"""
Complete tests for auth commands to achieve 100% coverage
"""
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os
from pathlib import Path

from wapi.commands.auth import cmd_auth_login, cmd_auth_logout, cmd_auth_status
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR, EXIT_AUTH_ERROR
from wapi.exceptions import (
    WAPIAuthenticationError,
    WAPIConnectionError,
    WAPIRequestError,
    WAPIValidationError,
    WAPIConfigurationError
)

class TestAuthComplete(unittest.TestCase):
    """Complete tests for auth commands"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.input')
    def test_cmd_auth_login_empty_username(self, mock_input, mock_get_logger):
        """Test login with empty username (lines 43-45)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.username = None
        self.mock_args.password = None
        self.mock_args.config = 'config.env'
        
        mock_input.return_value = ''  # Empty username
        
        result = cmd_auth_login(self.mock_args, None)
        
        self.assertEqual(result, EXIT_ERROR)
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    def test_cmd_auth_login_empty_password(self, mock_input, mock_getpass, mock_get_logger):
        """Test login with empty password (lines 55-57)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = None
        self.mock_args.config = 'config.env'
        
        mock_getpass.return_value = ''  # Empty password
        
        result = cmd_auth_login(self.mock_args, None)
        
        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    def test_cmd_auth_login_invalid_credentials_format(self, mock_input, mock_getpass, mock_validate, mock_get_logger):
        """Test login with invalid credential format (lines 63-65)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass'
        self.mock_args.config = 'config.env'
        
        mock_validate.return_value = (False, "Invalid email format")
        
        with self.assertRaises(WAPIValidationError):
            cmd_auth_login(self.mock_args, None)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_connection_error(self, mock_client_class, mock_get_logger, 
                                            mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with connection error (lines 86-88)"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            mock_path.return_value = PathLib(tmp_path)
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.ping.side_effect = WAPIConnectionError("Connection failed")
            
            # Connection errors no longer raise - credentials are saved anyway
            result = cmd_auth_login(self.mock_args, None)
            self.assertEqual(result, EXIT_SUCCESS)
            # Verify credentials were saved
            self.assertTrue(os.path.exists(tmp_path))
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_request_error(self, mock_client_class, mock_get_logger, 
                                          mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with request error (lines 86-88)"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            mock_path.return_value = PathLib(tmp_path)
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.ping.side_effect = WAPIRequestError("Request failed")
            
            # Request errors no longer raise - credentials are saved anyway
            result = cmd_auth_login(self.mock_args, None)
            self.assertEqual(result, EXIT_SUCCESS)
            # Verify credentials were saved
            self.assertTrue(os.path.exists(tmp_path))
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_ip_whitelist_issue(self, mock_client_class, mock_get_logger, 
                                               mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with IP whitelist issue (code 2051) - should save credentials"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            mock_path.return_value = PathLib(tmp_path)
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            # Mock IP whitelist error (code 2051)
            mock_response = {
                'response': {
                    'code': 2051,
                    'result': 'Access not allowed from this IP address (2a03:3b40:fe:40f::1)'
                }
            }
            mock_client.ping.return_value = mock_response
            
            # IP whitelist issue should not raise - credentials are saved
            result = cmd_auth_login(self.mock_args, None)
            self.assertEqual(result, EXIT_SUCCESS)
            # Verify credentials were saved
            self.assertTrue(os.path.exists(tmp_path))
            # Verify file contains credentials
            with open(tmp_path, 'r') as f:
                content = f.read()
                self.assertIn('WAPI_USERNAME', content)
                self.assertIn('WAPI_PASSWORD', content)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_generic_exception(self, mock_client_class, mock_get_logger, 
                                              mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with generic exception (lines 111-115) - should save credentials"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            mock_path.return_value = PathLib(tmp_path)
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            # Mock generic exception (not WAPIConnectionError or WAPIRequestError)
            mock_client.ping.side_effect = ValueError("Unexpected error")
            
            # Generic exceptions should not raise - credentials are saved
            result = cmd_auth_login(self.mock_args, None)
            self.assertEqual(result, EXIT_SUCCESS)
            # Verify credentials were saved
            self.assertTrue(os.path.exists(tmp_path))
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    @patch('builtins.open', new_callable=mock_open, read_data='# Comment\nWAPI_BASE_URL=https://api.wedos.com\n\nKEY=value\n')
    def test_cmd_auth_login_config_with_comments(self, mock_file, mock_client_class, mock_get_logger, 
                                                  mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with config file containing comments and empty lines (line 105)"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp.write('# Comment\nWAPI_BASE_URL=https://api.wedos.com\n\nKEY=value\n')
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            mock_path.return_value = PathLib(tmp_path)
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.ping.return_value = {'response': {'code': '1000'}}
            
            result = cmd_auth_login(self.mock_args, None)
            
            self.assertEqual(result, EXIT_SUCCESS)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_config_read_error(self, mock_client_class, mock_get_logger, 
                                              mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with config file read error (lines 110-111)"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        # Create a file that exists
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp.write('WAPI_BASE_URL=https://api.wedos.com\n')
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            # Create actual Path and mock it
            actual_path = PathLib(tmp_path)
            mock_path.return_value = actual_path
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.ping.return_value = {'response': {'code': '1000'}}
            
            # Mock open to raise Exception on read (when file exists), but allow writes
            def side_effect_open(*args, **kwargs):
                # Get mode from kwargs or from positional args
                mode = kwargs.get('mode', None)
                if mode is None and len(args) > 1:
                    mode = args[1]
                if mode is None:
                    mode = 'r'  # default
                
                if 'r' in mode and 'w' not in mode and 'a' not in mode:
                    raise IOError("Cannot read file")
                # Allow writes to succeed
                return mock_open(read_data='')()
            
            # Mock get_config to avoid calling load_config which would fail
            def mock_get_config(key, **kwargs):
                if key == 'WAPI_FORCE_IPV4':
                    return None
                return None
            
            with patch('wapi.commands.auth.get_config', side_effect=mock_get_config):
                with patch('builtins.open', side_effect=side_effect_open):
                    # Should continue despite read error (lines 110-111 catch the exception)
                    # But get_config will be called for WAPI_FORCE_IPV4, which will call load_config
                    # So we need to also mock load_config to not fail
                    with patch('wapi.config.load_config', return_value={}):
                        result = cmd_auth_login(self.mock_args, None)
                        
                        self.assertEqual(result, EXIT_SUCCESS)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_save_io_error(self, mock_client_class, mock_get_logger, 
                                         mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with IOError saving credentials (lines 142-145)"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        # Use temp directory for new file
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, 'config.env')
        
        self.mock_args.config = tmp_path
        
        try:
            # Create actual Path
            actual_path = PathLib(tmp_path)
            mock_path.return_value = actual_path
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.ping.return_value = {'response': {'code': '1000'}}
            
            # Mock open to raise PermissionError on write
            call_count = [0]
            def side_effect(*args, **kwargs):
                call_count[0] += 1
                mode = kwargs.get('mode', '')
                if 'w' in mode or (len(args) > 1 and 'w' in str(args[1])):
                    raise PermissionError("Permission denied")
                return mock_open(read_data='')()
            
            with patch('builtins.open', side_effect=side_effect):
                with self.assertRaises(WAPIConfigurationError):
                    cmd_auth_login(self.mock_args, None)
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    @patch('builtins.open', side_effect=Exception("Unexpected error"))
    def test_cmd_auth_login_save_unexpected_error(self, mock_file, mock_client_class, mock_get_logger, 
                                                  mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with unexpected error saving credentials (lines 146-149)"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            mock_path.return_value = PathLib(tmp_path)
            mock_path_instance = Mock()
            mock_path_instance.exists.return_value = False
            mock_path_instance.parent = PathLib(os.path.dirname(tmp_path))
            mock_path.return_value = mock_path_instance
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.ping.return_value = {'response': {'code': '1000'}}
            
            # First call succeeds (for reading), second fails (for writing)
            def side_effect(*args, **kwargs):
                if 'w' in args[0] or 'w' in str(kwargs.get('mode', '')):
                    raise Exception("Unexpected error")
                return mock_open(read_data='')()
            
            with patch('builtins.open', side_effect=side_effect):
                result = cmd_auth_login(self.mock_args, None)
                
                self.assertEqual(result, EXIT_ERROR)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.Path')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_logout_config_with_comments(self, mock_get_logger, mock_path):
        """Test logout with config file containing comments (line 171) - just verify delete happens"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        result = cmd_auth_logout(self.mock_args)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_path_instance.unlink.assert_called_once()

    @patch('wapi.commands.auth.Path')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_logout_read_error(self, mock_get_logger, mock_path):
        """Test logout where we verify successful logout even if we don't read file"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        result = cmd_auth_logout(self.mock_args)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_path_instance.unlink.assert_called_once()

    @patch('wapi.commands.auth.Path')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_logout_write_config(self, mock_get_logger, mock_path):
        """Test logout deletes the file (previously tested write)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        result = cmd_auth_logout(self.mock_args)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_path_instance.unlink.assert_called_once()

    @patch('wapi.commands.auth.Path')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_logout_save_io_error(self, mock_get_logger, mock_path):
        """Test logout with error deleting config (simulating save error)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        # Simulate permission error on delete
        mock_path_instance.unlink.side_effect = PermissionError("Permission denied")
        mock_path.return_value = mock_path_instance
        
        result = cmd_auth_logout(self.mock_args)
        
        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.commands.auth.Path')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_logout_save_unexpected_error(self, mock_get_logger, mock_path):
        """Test logout with unexpected error deleting config"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        # Simulate unexpected error on delete
        mock_path_instance.unlink.side_effect = Exception("Unexpected error")
        mock_path.return_value = mock_path_instance
        
        result = cmd_auth_logout(self.mock_args)
        
        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.commands.auth.get_config')
    @patch('wapi.commands.auth.format_output')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_status_connection_error(self, mock_client_class, mock_get_logger, 
                                             mock_format_output, mock_get_config):
        """Test status with connection error (lines 252-257)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_config.side_effect = lambda k, **kw: 'test@example.com' if k == 'WAPI_USERNAME' else 'testpass'
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'table'
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.ping.side_effect = WAPIConnectionError("Connection failed")
        
        result = cmd_auth_status(self.mock_args, None)
        
        # Status returns EXIT_AUTH_ERROR when connection fails, but still prints output
        self.assertEqual(result, EXIT_AUTH_ERROR)
        mock_format_output.assert_called_once()

    @patch('wapi.commands.auth.get_config')
    @patch('wapi.commands.auth.format_output')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_status_request_error(self, mock_client_class, mock_get_logger, 
                                          mock_format_output, mock_get_config):
        """Test status with request error (lines 252-257)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_config.side_effect = lambda k, **kw: 'test@example.com' if k == 'WAPI_USERNAME' else 'testpass'
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'table'
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.ping.side_effect = WAPIRequestError("Request failed")
        
        result = cmd_auth_status(self.mock_args, None)
        
        # Status returns EXIT_AUTH_ERROR when request fails, but still prints output
        self.assertEqual(result, EXIT_AUTH_ERROR)
        mock_format_output.assert_called_once()

if __name__ == '__main__':
    unittest.main()
