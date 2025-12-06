
import unittest
from unittest.mock import MagicMock, patch
from wapi.commands.auth import cmd_auth_login, cmd_auth_status
from wapi.constants import EXIT_ERROR, EXIT_SUCCESS

class TestAuthCoverageFinal(unittest.TestCase):
    @patch('wapi.commands.auth.WedosAPIClient')
    @patch('wapi.commands.auth.validate_credentials')
    @patch('wapi.commands.auth.getpass')
    @patch('wapi.commands.auth.input')
    @patch('pathlib.Path.mkdir')
    def test_cmd_auth_login_generic_exception_saving(self, mock_mkdir, mock_input, mock_getpass, mock_validate, mock_client):
        """
        Test generic Exception during credential saving in cmd_auth_login.
        This targets the 'except Exception as e:' block at the end of the function.
        """
        # Setup valid credentials flow
        mock_input.return_value = "test@example.com"
        mock_getpass.return_value = "testpass"
        mock_validate.return_value = (True, None)
        
        # Setup successful ping
        mock_client_instance = MagicMock()
        mock_client_instance.ping.return_value = {'response': {'code': 1000}}
        mock_client.return_value = mock_client_instance
        
        # Trigger generic Exception during directory creation
        mock_mkdir.side_effect = RuntimeError("Unexpected Boom!")
        
        # Execute
        args = MagicMock()
        args.config = "test_config.env"
        args.username = None
        args.password = None
        
        # Capture stderr to verify error message
        with patch('sys.stderr') as mock_stderr:
            result = cmd_auth_login(args)
            
            # Verify we hit the generic exception block
            self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.commands.auth.get_config')
    def test_cmd_auth_status_client_provided_no_config(self, mock_get_config):
        """
        Test cmd_auth_status when client is provided but no config exists.
        This covers the 'if client:' block inside 'if not username or not password:'.
        """
        # Setup get_config to return None (no credentials)
        mock_get_config.return_value = None
        
        # Setup mock client
        mock_client = MagicMock()
        
        # Execute
        args = MagicMock()
        args.config = "test_config.env"
        args.format = "table"
        
        with patch('builtins.print'): # Suppress output
            result = cmd_auth_status(args, client=mock_client)
        
        # Verify success
        self.assertEqual(result, EXIT_SUCCESS)

