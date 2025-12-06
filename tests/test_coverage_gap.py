"""
Tests for coverage gaps to achieve 100% coverage.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO

from wapi.cli import main, cmd_ping, get_client
from wapi.constants import (
    EXIT_SUCCESS, EXIT_ERROR, EXIT_CONFIG_ERROR, 
    EXIT_AUTH_ERROR, EXIT_CONNECTION_ERROR
)
from wapi.utils.interactive import WAPIInteractiveShell
from wapi.commands.domain import filter_sensitive_domain_data, cmd_domain_list, cmd_domain_info
from wapi.commands.search import interpret_status_value, interpret_api_availability
from wapi.exceptions import WAPIRequestError, WAPIValidationError

class TestCoverageGap(unittest.TestCase):
    
    def setUp(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
    def tearDown(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    # --- wapi/cli.py coverage ---

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_aliases(self, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test main with --aliases"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.aliases = True
        # Ensure other flags are False
        mock_args.wizard = False
        mock_args.interactive = False
        mock_args.search_domain = None
        
        mock_parser.parse_args.return_value = mock_args
        
        with patch('wapi.cli.list_aliases', return_value="alias1, alias2"):
            result = main()
            
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.cmd_search')
    def test_main_search_alias(self, mock_cmd_search, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test main with --search alias"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.search_domain = "example.com"
        mock_args.aliases = False
        mock_args.wizard = False
        mock_args.interactive = False
        # format might be missing in args initially
        del mock_args.format
        
        mock_parser.parse_args.return_value = mock_args
        mock_cmd_search.return_value = EXIT_SUCCESS
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = main()
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.assertEqual(mock_args.module, 'search')
        self.assertEqual(mock_args.domain, "example.com")

    @patch('wapi.cli.setup_logging')
    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    @patch('wapi.cli.start_interactive_mode')
    def test_main_interactive_success(self, mock_start_interactive, mock_parser_class, mock_get_client, mock_setup_logging):
        """Test main with --interactive success"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_args = Mock()
        mock_args.interactive = True
        mock_args.aliases = False
        mock_args.wizard = False
        mock_args.search_domain = None
        
        mock_parser.parse_args.return_value = mock_args
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_start_interactive.return_value = 0
        
        result = main()
        
        self.assertEqual(result, 0)

    @patch('wapi.cli.format_output')
    def test_cmd_ping_failure(self, mock_format):
        """Test cmd_ping with API failure code"""
        mock_args = Mock()
        mock_args.format = 'table'
        mock_client = Mock()
        mock_client.ping.return_value = {'response': {'code': '1001', 'result': 'Error'}}
        
        result = cmd_ping(mock_args, mock_client)
        
        self.assertEqual(result, EXIT_ERROR)

    # --- wapi/utils/interactive.py coverage ---

    def test_interactive_shell_unimplemented_commands(self):
        """Test unimplemented commands in interactive shell print messages"""
        client = Mock()
        shell = WAPIInteractiveShell(client)
        
        # Redirect stdout to check prints
        with patch('builtins.print') as mock_print:
            shell._execute_command('domain info example.com')
            mock_print.assert_any_call("Domain command: info (not yet implemented in interactive mode)")
            
            shell._execute_command('dns records example.com')
            mock_print.assert_any_call("DNS command: records (not yet implemented in interactive mode)")
            
            shell._execute_command('nsset info test')
            mock_print.assert_any_call("NSSET command: info (not yet implemented in interactive mode)")
            
            shell._execute_command('contact info test')
            mock_print.assert_any_call("Contact command: info (not yet implemented in interactive mode)")
            
            shell._execute_command('config show')
            mock_print.assert_any_call("Config command: show (not yet implemented in interactive mode)")

    def test_interactive_shell_empty_subcommands(self):
        """Test interactive shell commands without arguments"""
        client = Mock()
        shell = WAPIInteractiveShell(client)
        
        with patch('builtins.print') as mock_print:
            shell._execute_command('domain')
            mock_print.assert_any_call("Usage: domain <list|info|update-ns> [arguments]")
            
            shell._execute_command('dns')
            mock_print.assert_any_call("Usage: dns <records|add|delete> [arguments]")

    def test_interactive_run_exceptions(self):
        """Test exception handling in run loop"""
        client = Mock()
        shell = WAPIInteractiveShell(client)
        
        # 1. KeyboardInterrupt
        with patch('builtins.input', side_effect=[KeyboardInterrupt, 'exit']):
            with patch('builtins.print') as mock_print:
                shell.run()
                # Should print exit msg
        
        # 2. EOFError
        shell.running = True
        with patch('builtins.input', side_effect=EOFError):
            shell.run()
            
        # 3. Generic Exception
        shell.running = True
        with patch('builtins.input', side_effect=[Exception("Test error"), 'exit']):
             with patch('builtins.print') as mock_print:
                shell.run()

    # --- wapi/commands/domain.py coverage ---

    def test_filter_sensitive_domain_data(self):
        """Test sensitive data filtering"""
        data = {
            'name': 'example.com',
            'own_email': 'secret@example.com',
            'own_name': 'John Doe',
            'public_field': 'public'
        }
        filtered = filter_sensitive_domain_data(data)
        self.assertEqual(filtered['own_email'], '[HIDDEN]')
        self.assertEqual(filtered['own_name'], '[HIDDEN]')
        self.assertEqual(filtered['public_field'], 'public')

    def test_cmd_domain_list_failure(self):
        """Test domain list failure"""
        args = Mock()
        client = Mock()
        client.call.return_value = {'response': {'code': '1001', 'result': 'Error'}}
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_list(args, client)

    def test_cmd_domain_info_failure(self):
        """Test domain info failure"""
        args = Mock()
        args.domain = 'example.com'
        client = Mock()
        client.domain_info.return_value = {'response': {'code': '1001', 'result': 'Error'}}
        
        # Mock validator to return True
        with patch('wapi.commands.domain.validate_domain', return_value=(True, None)):
            with self.assertRaises(WAPIRequestError):
                cmd_domain_info(args, client)

    # --- wapi/commands/search.py coverage ---

    def test_interpret_status_value(self):
        """Test status interpretation"""
        self.assertTrue(interpret_status_value("available"))
        self.assertTrue(interpret_status_value("free"))
        self.assertTrue(interpret_status_value("true"))
        self.assertTrue(interpret_status_value("1"))
        self.assertTrue(interpret_status_value(True))
        
        self.assertFalse(interpret_status_value("registered"))
        self.assertFalse(interpret_status_value("taken"))
        self.assertFalse(interpret_status_value("false"))
        self.assertFalse(interpret_status_value("0"))
        self.assertFalse(interpret_status_value(False))
        
        self.assertIsNone(interpret_status_value(None))
        self.assertIsNone(interpret_status_value(""))
        self.assertIsNone(interpret_status_value("unknown"))

    def test_interpret_api_availability(self):
        """Test API availability interpretation"""
        # Case 1: domain field
        res1 = {'response': {'code': '1000', 'data': {'domain': {'name': 'example.com', 'status': 'available'}}}}
        self.assertTrue(interpret_api_availability(res1, 'example.com'))
        
        # Case 2: domains list
        res2 = {'response': {'code': '1000', 'data': {'domains': [{'name': 'example.com', 'status': 'taken'}]}}}
        self.assertFalse(interpret_api_availability(res2, 'example.com'))
        
        # Case 3: availability field
        res3 = {'response': {'code': '1000', 'data': {'availability': {'name': 'example.com', 'avail': '1'}}}}
        self.assertTrue(interpret_api_availability(res3, 'example.com'))
        
        # Case 4: top level status
        res4 = {'response': {'code': '1000', 'data': {'status': 'free'}}}
        self.assertTrue(interpret_api_availability(res4, 'example.com'))
        
        # Case 5: mismatch name
        res5 = {'response': {'code': '1000', 'data': {'domain': {'name': 'other.com', 'status': 'available'}}}}
        # Should fall back to top level or return None if no top level
        self.assertIsNone(interpret_api_availability(res5, 'example.com'))

if __name__ == '__main__':
    unittest.main()
