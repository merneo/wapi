"""
Final tests to achieve 100% coverage.
Targeting remaining missing lines in CLI, commands, and utils.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO
import socket

from wapi.cli import main
from wapi.constants import (
    EXIT_SUCCESS, EXIT_ERROR, EXIT_CONFIG_ERROR, 
    EXIT_AUTH_ERROR, EXIT_CONNECTION_ERROR, EXIT_TIMEOUT_ERROR
)
from wapi.exceptions import WAPIConfigurationError, WAPITimeoutError
from wapi.commands.search import (
    interpret_api_availability, 
    _discover_whois_server, 
    _query_whois, 
    infer_availability_from_whois,
    cmd_search
)
from wapi.utils.batch import write_results_to_file
from wapi.utils.interactive import WAPIInteractiveShell
from wapi.utils.config_wizard import run_config_wizard

class TestFinalCoverage(unittest.TestCase):
    
    def setUp(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
    def tearDown(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    # --- wapi/cli.py coverage ---

    @patch('wapi.cli.get_client')
    @patch('wapi.cli.argparse.ArgumentParser')
    def test_main_interactive_config_error(self, mock_parser_class, mock_get_client):
        """Test main --interactive with config error (lines 350-351)"""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.interactive = True
        mock_args.wizard = False
        mock_args.aliases = False
        mock_args.search_domain = None
        mock_args.config = 'bad_config.env'
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        mock_get_client.side_effect = WAPIConfigurationError("Test config error")
        
        result = main()
        self.assertEqual(result, EXIT_CONFIG_ERROR)

    # --- wapi/commands/search.py coverage ---

    def test_interpret_api_availability_structures(self):
        """Test various API response structures (lines 106, 114, 120)"""
        # domains list structure
        res1 = {'response': {'code': '1000', 'data': {'domains': [{'name': 'example.com', 'status': 'taken'}]}}}
        self.assertFalse(interpret_api_availability(res1, 'example.com'))
        
        # availability dict structure
        res2 = {'response': {'code': '1000', 'data': {'availability': {'domain': 'example.com', 'status': 'free'}}}}
        self.assertTrue(interpret_api_availability(res2, 'example.com'))

    @patch('wapi.commands.search._query_whois')
    def test_discover_whois_server_exception(self, mock_query):
        """Test exception in discovery (line 170)"""
        mock_query.side_effect = Exception("Network error")
        server = _discover_whois_server("example.com", 5)
        self.assertIsNone(server)

    @patch('socket.socket')
    def test_query_whois_timeout_recv(self, mock_socket_class):
        """Test socket timeout during recv (lines 206-209)"""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        # First recv returns data, second raises timeout
        mock_socket.recv.side_effect = [b"Partial data", socket.timeout()]
        
        result = _query_whois("whois.test", "example.com", 5)
        self.assertEqual(result, "Partial data")

    def test_infer_availability_none(self):
        """Test infer availability with None (line 239)"""
        self.assertIsNone(infer_availability_from_whois(None))

    @patch('wapi.commands.search.validate_domain')
    @patch('wapi.commands.search.interpret_api_availability')
    @patch('wapi.commands.search.perform_whois_lookup')
    @patch('wapi.commands.search.format_output')
    def test_cmd_search_whois_error(self, mock_fmt, mock_whois, mock_interpret, mock_validate):
        """Test cmd_search with WHOIS error (line 309)"""
        mock_validate.return_value = (True, None)
        mock_interpret.return_value = None # Force WHOIS lookup
        mock_whois.side_effect = Exception("WHOIS failed")
        
        # We need interpret to return False/None to trigger WHOIS, but then WHOIS fails
        # If WHOIS fails, availability remains None -> raises WAPIRequestError
        # Wait, line 309 is `if whois_error: result_payload["whois_error"] = whois_error`
        # We need availability to be set somehow even if WHOIS failed, OR checking logic flow.
        # If WHOIS fails, availability is None. Then line 312 raises RequestError.
        # So line 309 is unreachable if availability is None?
        # Ah, we need availability to be set (e.g. by WAPI) but we still try WHOIS?
        # No, WHOIS is only tried if availability is False or None.
        # If availability is False (registered), we try WHOIS. If WHOIS fails, we catch exception.
        # Then we proceed. Availability is False.
        
        mock_interpret.return_value = False # Registered according to WAPI
        mock_whois.side_effect = Exception("Connection reset")
        
        args = Mock()
        args.domain = "example.com"
        args.format = "json"
        client = Mock()
        client.domain_availability.return_value = {}
        
        result = cmd_search(args, client)
        self.assertEqual(result, EXIT_SUCCESS)
        
        # Check that format_output was called with dict containing whois_error
        call_args = mock_fmt.call_args[0][0]
        self.assertIn("whois_error", call_args)
        self.assertEqual(call_args["whois_error"], "Connection reset")

    # --- wapi/utils/interactive.py coverage ---

    @patch('builtins.input')
    def test_interactive_shell_eof(self, mock_input):
        """Test EOF handling (Ctrl+D) (lines 67-70)"""
        mock_input.side_effect = EOFError()
        
        shell = WAPIInteractiveShell(Mock())
        result = shell.run()
        
        self.assertEqual(result, 0)
        # Should print Exiting...
        self.assertIn("Exiting...", sys.stdout.getvalue())

    @patch('builtins.input')
    def test_interactive_shell_fatal_error(self, mock_input):
        """Test fatal error in loop (lines 71-74)"""
        mock_input.side_effect = Exception("Fatal crash")
        
        shell = WAPIInteractiveShell(Mock())
        result = shell.run()
        
        self.assertEqual(result, 1)
        self.assertIn("Fatal error", sys.stderr.getvalue())

    def test_interactive_subcommand_usage_help(self):
        """Test usage messages for subcommands (lines 91-92, 168-169, etc.)"""
        shell = WAPIInteractiveShell(Mock())
        
        # Capture stdout
        with patch('builtins.print') as mock_print:
            shell._execute_command("domain")
            mock_print.assert_any_call("Usage: domain <list|info|update-ns> [arguments]")
            
            shell._execute_command("dns")
            mock_print.assert_any_call("Usage: dns <records|add|delete> [arguments]")
            
            shell._execute_command("nsset")
            mock_print.assert_any_call("Usage: nsset <info|create> [arguments]")
            
            shell._execute_command("contact")
            mock_print.assert_any_call("Usage: contact <info> [arguments]")
            
            shell._execute_command("config")
            mock_print.assert_any_call("Usage: config <show|validate|set> [arguments]")

    # --- wapi/utils/config_wizard.py coverage ---

    @patch('builtins.input')
    @patch('wapi.utils.config_wizard.getpass')
    def test_config_wizard_password_retry_fail(self, mock_getpass, mock_input):
        """Test password required second prompt failure (lines 52-53)"""
        mock_input.return_value = "user@example.com"
        # First getpass empty, second getpass empty
        mock_getpass.side_effect = ["", ""]
        
        with patch('builtins.print'):
            result = run_config_wizard("test.env")
            
        self.assertFalse(result)

    @patch('builtins.input')
    @patch('wapi.utils.config_wizard.getpass')
    def test_config_wizard_save_exception(self, mock_getpass, mock_input):
        """Test exception during save (lines 108-111)"""
        mock_input.side_effect = ["user", "yes"]
        mock_getpass.return_value = "pass"
        
        # Mock open to raise exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with patch('builtins.print') as mock_print:
                result = run_config_wizard("test.env")
                
                self.assertFalse(result)
                # Check that error was printed
                # We look for any call that contains the error message
                found = False
                for call in mock_print.call_args_list:
                    args, kwargs = call
                    if args and "Failed to save configuration" in str(args[0]):
                        found = True
                        break
                self.assertTrue(found, "Error message not printed")

    # --- wapi/utils/batch.py coverage ---

    def test_write_results_to_file_csv(self):
        """Test writing results to CSV (lines 108-114ish)"""
        import tempfile
        import os
        
        data = {
            'success': [{'domain': 'd1.com', 'result': 'ok'}],
            'failed': [{'domain': 'd2.com', 'error': 'bad'}]
        }
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
            
        try:
            write_results_to_file(data, path, 'csv')
            with open(path, 'r') as f:
                content = f.read()
                self.assertIn('d1.com,Success,ok', content)
                self.assertIn('d2.com,Failed,bad', content)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_write_results_to_file_invalid_format(self):
        """Test invalid format exception"""
        with self.assertRaises(ValueError):
            write_results_to_file({}, "test.txt", "xml")

    # --- wapi/commands/domain.py coverage (polling timeouts) ---
    
    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    def test_domain_polling_timeout_blocks(self, mock_validate):
        """Test polling timeout blocks in domain commands"""
        from wapi.commands.domain import (
            cmd_domain_update_ns, cmd_domain_create, 
            cmd_domain_renew, cmd_domain_delete, cmd_domain_update
        )
        
        # Setup common mock client behavior for timeout
        client = Mock()
        # Return "started" (1001) first
        client.domain_update_ns.return_value = {'response': {'code': '1001'}}
        client.domain_create.return_value = {'response': {'code': '1001'}}
        client.domain_renew.return_value = {'response': {'code': '1001'}}
        client.domain_delete.return_value = {'response': {'code': '1001'}}
        client.domain_update.return_value = {'response': {'code': '1001'}}
        
        # Poll returns successful completion but with a warning/timeout message
        # or returns a code that indicates partial success but we treat as success in loop
        # The code checks specifically for:
        # if 'timeout' in error_msg.lower() or final_code == '9998': raise WAPITimeoutError
        
        poll_result_timeout = {
            'response': {
                'code': '9998', 
                'result': 'Operation timed out'
            }
        }
        
        client.poll_until_complete.return_value = poll_result_timeout
        
        args = Mock()
        args.domain = "example.com"
        args.wait = True
        args.quiet = True
        args.nsset = "TEST"
        args.force = True # for delete
        args.auth_info = "auth" # for transfer/update
        args.period = 1
        
        # Test timeout in update_ns
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_update_ns(args, client)
            
        # Test timeout in create
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_create(args, client)
            
        # Test timeout in renew
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_renew(args, client)
            
        # Test timeout in update
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_update(args, client)

        # Test delete error (not polling, just direct error)
        client.domain_delete.return_value = {'response': {'code': '2000', 'result': 'Failed'}}
        from wapi.exceptions import WAPIRequestError
        with self.assertRaises(WAPIRequestError):
            cmd_domain_delete(args, client)

if __name__ == '__main__':
    unittest.main()
