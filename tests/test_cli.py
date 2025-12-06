"""
Unit tests for wapi.cli module

Tests for CLI argument parsing, command routing, and error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO

from wapi.cli import main, get_client
from wapi.constants import (
    EXIT_SUCCESS,
    EXIT_ERROR,
    EXIT_CONFIG_ERROR,
    EXIT_AUTH_ERROR,
    EXIT_CONNECTION_ERROR,
)
from wapi.exceptions import (
    WAPIConfigurationError,
    WAPIAuthenticationError,
    WAPIConnectionError,
    WAPIRequestError,
)


class TestGetClient(unittest.TestCase):
    """Test get_client function"""

    @patch('wapi.cli.validate_config')
    @patch('wapi.cli.get_config')
    @patch('wapi.cli.WedosAPIClient')
    def test_get_client_success(self, mock_client_class, mock_get_config, mock_validate_config):
        """Test successful client creation"""
        mock_validate_config.return_value = (True, None)
        mock_get_config.side_effect = lambda k, **kw: 'test_user' if k == 'WAPI_USERNAME' else 'test_pass'
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = get_client("config.env")
        
        self.assertIsNotNone(client)
        mock_client_class.assert_called_once()

    @patch('wapi.cli.validate_config')
    def test_get_client_invalid_config(self, mock_validate_config):
        """Test client creation with invalid config"""
        mock_validate_config.return_value = (False, "Config error")
        
        client = get_client("config.env")
        
        self.assertIsNone(client)

    @patch('wapi.cli.validate_config')
    @patch('wapi.cli.get_config')
    def test_get_client_missing_credentials(self, mock_get_config, mock_validate_config):
        """Test client creation with missing credentials"""
        mock_validate_config.return_value = (True, None)
        mock_get_config.return_value = None
        
        client = get_client("config.env")
        
        self.assertIsNone(client)



class TestCLIErrorHandling(unittest.TestCase):
    """Test CLI error handling"""

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_cli_no_command(self, mock_run_wizard, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test CLI with no command"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.module = None
        # Ensure flags are False
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None
        
        mock_parser.parse_args.return_value = mock_args

        result = main()

        mock_parser.print_help.assert_called_once()
        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_cli_config_error(self, mock_run_wizard, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test CLI with configuration error"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.module = 'domain'
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        # Ensure flags are False
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None

        mock_parser.parse_args.return_value = mock_args
        mock_get_client.return_value = None
        
        # Mock run_config_wizard to return False (failed or cancelled)
        mock_run_wizard.return_value = False

        result = main()

        self.assertEqual(result, EXIT_CONFIG_ERROR)

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_cli_authentication_error(self, mock_run_wizard, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test CLI with authentication error"""
        from wapi.commands.domain import cmd_domain_info

        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.module = 'domain'
        mock_args.command = 'info'
        mock_args.domain = 'example.com'
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        mock_args.func = cmd_domain_info
        # Ensure flags are False
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None

        mock_parser.parse_args.return_value = mock_args

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock run_config_wizard to return False
        mock_run_wizard.return_value = False

        # Create a mock function that raises authentication error
        def mock_cmd(*args, **kwargs):
            raise WAPIAuthenticationError("Auth failed")

        mock_args.func = mock_cmd

        result = main()
        self.assertEqual(result, EXIT_AUTH_ERROR)

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_cli_connection_error(self, mock_run_wizard, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test CLI with connection error"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.module = 'domain'
        mock_args.command = 'info'
        mock_args.domain = 'example.com'
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        # Ensure flags are False
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None

        mock_parser.parse_args.return_value = mock_args

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock run_config_wizard to return False
        mock_run_wizard.return_value = False

        # Create a mock function that raises connection error
        def mock_cmd(*args, **kwargs):
            raise WAPIConnectionError("Connection failed")

        mock_args.func = mock_cmd

        result = main()
        self.assertEqual(result, EXIT_CONNECTION_ERROR)

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_cli_keyboard_interrupt(self, mock_run_wizard, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test CLI with keyboard interrupt"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.module = 'domain'
        mock_args.command = 'info'
        mock_args.domain = 'example.com'
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        # Ensure flags are False
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None

        mock_parser.parse_args.return_value = mock_args

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Create a mock function that raises keyboard interrupt
        def mock_cmd(*args, **kwargs):
            raise KeyboardInterrupt()

        mock_args.func = mock_cmd

        result = main()
        self.assertEqual(result, EXIT_ERROR)

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.run_config_wizard')
    def test_cli_generic_exception(self, mock_run_wizard, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test CLI with generic exception"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.module = 'domain'
        mock_args.command = 'info'
        mock_args.domain = 'example.com'
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        # Ensure flags are False
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None

        mock_parser.parse_args.return_value = mock_args

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Create a mock function that raises generic exception
        def mock_cmd(*args, **kwargs):
            raise ValueError("Unexpected error")

        mock_args.func = mock_cmd

        result = main()
        self.assertEqual(result, EXIT_ERROR)


class TestCLICommandRouting(unittest.TestCase):
    """Test CLI command routing"""

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.commands.config.cmd_config_show')
    @patch('wapi.cli.run_config_wizard')
    def test_cli_config_commands_no_client(self, mock_run_wizard, mock_cmd, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test that config commands are called without client parameter"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.module = 'config'
        mock_args.command = 'show'
        mock_args.config = 'config.env'
        mock_args.format = 'table'
        # Ensure flags are False
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.aliases = False
        mock_args.search_domain = None

        mock_parser.parse_args.return_value = mock_args

        # Import the actual function to set as func
        from wapi.commands.config import cmd_config_show
        mock_args.func = cmd_config_show

        # Mock get_client to return a client (even though config commands don't need it)
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Mock cmd_config_show to return success
        mock_cmd.return_value = EXIT_SUCCESS

        result = main()

        # Config command should be called with args only, not with client
        mock_cmd.assert_called_once_with(mock_args)
        self.assertEqual(result, EXIT_SUCCESS)


if __name__ == '__main__':
    unittest.main()
