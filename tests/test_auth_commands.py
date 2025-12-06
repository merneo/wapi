"""
Unit tests for auth command operations

Tests for authentication commands: login, logout, status.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import os
import tempfile
import shutil

from wapi.commands.auth import cmd_auth_login, cmd_auth_logout, cmd_auth_status
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR, EXIT_AUTH_ERROR
from wapi.exceptions import WAPIAuthenticationError, WAPIConnectionError


class TestAuthLoginCommand(unittest.TestCase):
    """Test auth login command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()
        self.mock_client = Mock()

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('builtins.open', new_callable=mock_open, read_data='WAPI_BASE_URL=https://api.wedos.com/wapi/json\n')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_with_credentials(self, mock_client_class, mock_file, mock_get_logger, 
                                            mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with provided credentials"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        # Use temporary file for config
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp.write('WAPI_BASE_URL=https://api.wedos.com/wapi/json\n')
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            # Mock Path to return actual Path object
            mock_path.return_value = PathLib(tmp_path)
            
            # Mock WedosAPIClient
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = {
                'response': {
                    'code': '1000',
                    'data': {'result': 'OK'}
                }
            }
            mock_client.ping.return_value = mock_response
            
            result = cmd_auth_login(self.mock_args, None)
            
            self.assertEqual(result, EXIT_SUCCESS)
        finally:
            # Cleanup
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_prompt_username(self, mock_client_class, mock_get_logger, 
                                            mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with username prompt"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = None
        self.mock_args.password = 'testpass123'
        mock_input.return_value = 'test@example.com'
        
        # Use temporary file for config
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            # Mock Path to return actual Path object
            mock_path.return_value = PathLib(tmp_path)
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = {
                'response': {
                    'code': '1000',
                    'data': {'result': 'OK'}
                }
            }
            mock_client.ping.return_value = mock_response
            
            result = cmd_auth_login(self.mock_args, None)
            
            self.assertEqual(result, EXIT_SUCCESS)
            mock_input.assert_called_once()
        finally:
            # Cleanup
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_prompt_password(self, mock_client_class, mock_get_logger, 
                                           mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login with password prompt"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = None
        self.mock_args.config = 'config.env'
        
        # Use temporary file for config
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        try:
            # Mock Path to return actual Path object
            # Path.parent is a property, so we need to ensure the path exists
            import os
            os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
            
            mock_path.return_value = PathLib(tmp_path)
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = {
                'response': {
                    'code': '1000',
                    'data': {'result': 'OK'}
                }
            }
            mock_client.ping.return_value = mock_response
            
            result = cmd_auth_login(self.mock_args, None)
            
            self.assertEqual(result, EXIT_SUCCESS)
            mock_getpass.assert_called_once()
        finally:
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            # Cleanup directory if created
            dir_path = os.path.dirname(tmp_path)
            if dir_path and os.path.exists(dir_path) and not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                except:
                    pass

    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_authentication_failed(self, mock_client_class, mock_get_logger, 
                                                 mock_input, mock_getpass, mock_validate, mock_path):
        """Test login with authentication failure"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'wrongpass'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'wrongpass'
        self.mock_args.config = 'config.env'
        
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock failed API ping - code 2000 means authentication failed
        mock_response = {
            'response': {
                'code': '2000',
                'result': 'Authentication failed'
            }
        }
        mock_client.ping.return_value = mock_response
        
        # cmd_auth_login raises WAPIAuthenticationError, which is then wrapped in WAPIConnectionError
        with self.assertRaises(WAPIConnectionError):
            cmd_auth_login(self.mock_args, None)

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    @patch('wapi.api.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_login_no_client(self, mock_client_class, mock_get_logger, 
                                     mock_input, mock_getpass, mock_validate, mock_path, mock_chmod):
        """Test login without client (creates new client)"""
        import tempfile
        from pathlib import Path as PathLib
        
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        mock_getpass.return_value = 'testpass123'
        
        self.mock_args.username = 'test@example.com'
        self.mock_args.password = 'testpass123'
        
        # Use temporary file for config
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as tmp:
            tmp_path = tmp.name
        
        self.mock_args.config = tmp_path
        
        try:
            # Mock Path to return actual Path object
            mock_path.return_value = PathLib(tmp_path)
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = {
                'response': {
                    'code': '1000',
                    'data': {'result': 'OK'}
                }
            }
            mock_client.ping.return_value = mock_response
            
            result = cmd_auth_login(self.mock_args, None)
            
            self.assertEqual(result, EXIT_SUCCESS)
            mock_client_class.assert_called_once_with('test@example.com', 'testpass123', use_json=False)
        finally:
            # Cleanup
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestAuthLogoutCommand(unittest.TestCase):
    """Test auth logout command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()

    @patch('wapi.commands.auth.Path')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_logout_success(self, mock_get_logger, mock_path):
        """Test successful logout"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        # Mock Path.exists() to return True
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        result = cmd_auth_logout(self.mock_args)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify file was removed
        mock_path_instance.unlink.assert_called_once()

    @patch('wapi.commands.auth.Path')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_logout_no_config_file(self, mock_get_logger, mock_path):
        """Test logout when config file doesn't exist"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.config = 'config.env'
        
        # Mock Path.exists() to return False
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        result = cmd_auth_logout(self.mock_args)
        
        self.assertEqual(result, EXIT_SUCCESS)


class TestAuthStatusCommand(unittest.TestCase):
    """Test auth status command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_args = Mock()
        self.mock_client = Mock()

    @patch('wapi.commands.auth.get_config')
    @patch('wapi.commands.auth.format_output')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_status_authenticated(self, mock_client_class, mock_get_logger, 
                                           mock_format_output, mock_get_config):
        """Test status when authenticated"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_config.side_effect = lambda k, **kw: 'test@example.com' if k == 'WAPI_USERNAME' else '***'
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'table'
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = {
            'response': {
                'code': '1000',
                'data': {'result': 'OK'}
            }
        }
        mock_client.ping.return_value = mock_response
        
        result = cmd_auth_status(self.mock_args, None)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format_output.assert_called_once()
        # Verify output contains authenticated status
        call_args = mock_format_output.call_args[0]
        status_data = call_args[0]
        self.assertTrue(status_data.get('authenticated', False))

    @patch('wapi.commands.auth.get_config')
    @patch('wapi.commands.auth.format_output')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_status_not_authenticated(self, mock_get_logger, mock_format_output, mock_get_config):
        """Test status when not authenticated"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_config.return_value = None
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'table'
        
        result = cmd_auth_status(self.mock_args, None)
        
        self.assertEqual(result, EXIT_AUTH_ERROR)  # Returns EXIT_AUTH_ERROR when not authenticated
        mock_format_output.assert_called_once()
        # Verify output contains not authenticated status
        call_args = mock_format_output.call_args[0]
        status_data = call_args[0]
        self.assertFalse(status_data.get('configured', True))

    @patch('wapi.commands.auth.get_config')
    @patch('wapi.commands.auth.format_output')
    @patch('wapi.commands.auth.get_logger')
    @patch('wapi.commands.auth.WedosAPIClient')
    def test_cmd_auth_status_invalid_credentials(self, mock_client_class, mock_get_logger, 
                                                 mock_format_output, mock_get_config):
        """Test status with invalid credentials"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_config.side_effect = lambda k, **kw: 'test@example.com' if k == 'WAPI_USERNAME' else 'wrongpass'
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'table'
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock failed API ping
        mock_response = {
            'response': {
                'code': '2000',
                'result': 'Authentication failed'
            }
        }
        mock_client.ping.return_value = mock_response
        
        result = cmd_auth_status(self.mock_args, None)
        
        self.assertEqual(result, EXIT_AUTH_ERROR)  # Returns EXIT_AUTH_ERROR when invalid
        mock_format_output.assert_called_once()
        # Verify output indicates invalid credentials
        call_args = mock_format_output.call_args[0]
        status_data = call_args[0]
        self.assertFalse(status_data.get('authenticated', True))

    @patch('wapi.commands.auth.get_config')
    @patch('wapi.commands.auth.format_output')
    @patch('wapi.commands.auth.get_logger')
    def test_cmd_auth_status_no_client(self, mock_get_logger, mock_format_output, mock_get_config):
        """Test status without client"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_config.side_effect = lambda k, **kw: 'test@example.com' if k == 'WAPI_USERNAME' else None
        
        self.mock_args.config = 'config.env'
        self.mock_args.format = 'table'
        
        result = cmd_auth_status(self.mock_args, None)
        
        self.assertEqual(result, EXIT_AUTH_ERROR)  # Returns EXIT_AUTH_ERROR when password not set
        mock_format_output.assert_called_once()
        # Should show credentials exist but can't verify
        call_args = mock_format_output.call_args[0]
        status_data = call_args[0]
        self.assertIn('username', str(status_data).lower())


if __name__ == '__main__':
    unittest.main()
