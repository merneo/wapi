"""
Tests for remaining missing lines to achieve 100% coverage.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO
import importlib

from wapi.commands.auth import get_client, cmd_auth_logout, cmd_auth_login
from wapi.commands.contact import cmd_contact_list
from wapi.commands.nsset import cmd_nsset_list
from wapi.utils.interactive import WAPIInteractiveShell
from wapi.constants import EXIT_ERROR
from wapi.exceptions import WAPIRequestError


class TestFinal100PercentCoverage(unittest.TestCase):

    def setUp(self):
        self.original_stderr = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self.original_stderr

    # --- wapi/commands/auth.py (Missing: 198-203, 252-253) ---

    @patch('wapi.commands.auth.WedosAPIClient')
    def test_auth_get_client_exception_coverage(self, mock_client_cls):
        """Test get_client catching exception during WedosAPIClient init (lines 252-253)"""
        mock_client_cls.side_effect = Exception("Init failed")
        with patch('wapi.commands.auth.get_config', side_effect=lambda k, **kw: "val"):
            client = get_client("c.env")
            self.assertIsNone(client)

    @patch('wapi.commands.auth.Path')
    def test_auth_logout_unlink_exception_coverage(self, mock_path_cls):
        """Test cmd_auth_logout catching exception during unlink (lines 198-203)"""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.unlink.side_effect = Exception("Delete failed")
        mock_path_cls.return_value = mock_path

        args = Mock()
        args.config = "c.env"

        ret = cmd_auth_logout(args)
        self.assertEqual(ret, EXIT_ERROR)
        self.assertIn("Error: Could not update config file", sys.stderr.getvalue())

    # --- wapi/commands/contact.py (Missing: 85) ---

    @patch('wapi.commands.contact.format_output', return_value="formatted output")
    def test_contact_list_contacts_not_list(self, mock_format_output):
        """Test cmd_contact_list when API returns contact as non-list (line 85)"""
        client = Mock()
        # Mock API response where 'contact' is a dict, not a list
        client.call.return_value = {'response': {'code': '1000', 'data': {'contact': {'name': 'test'}}}}

        args = Mock()
        args.format = "json"

        ret = cmd_contact_list(args, client)
        self.assertEqual(ret, 0)
        # Verify it passed the dict contact as a list to format_output
        mock_format_output.assert_called_with([{'name': 'test'}], 'json')


    # --- wapi/commands/nsset.py (Missing: 219) ---

    @patch('wapi.commands.nsset.format_output', return_value="formatted output")
    def test_nsset_list_nssets_not_list(self, mock_format_output):
        """Test cmd_nsset_list when API returns nsset as non-list (line 219)"""
        client = Mock()
        # Mock API response where 'nsset' is a dict, not a list
        client.call.return_value = {'response': {'code': '1000', 'data': {'nsset': {'name': 'NS-TEST'}}}}

        args = Mock()
        args.format = "json"

        ret = cmd_nsset_list(args, client)
        self.assertEqual(ret, 0)
        # Verify it passed the dict nsset as a list to format_output
        mock_format_output.assert_called_with([{'name': 'NS-TEST'}], 'json')

    # --- wapi/utils/interactive.py (Missing: 71-73) ---

    @patch('builtins.input')
    def test_interactive_fatal_error_coverage(self, mock_input):
        """Test interactive shell catching generic Exception in main loop (lines 71-73)"""
        from wapi.utils.interactive import WAPIInteractiveShell
        mock_input.side_effect = Exception("Fatal Input Error")

        shell = WAPIInteractiveShell(Mock())
        ret = shell.run()
        self.assertEqual(ret, EXIT_ERROR)
        self.assertIn("Fatal error", sys.stderr.getvalue())

    # --- wapi/commands/auth.py (Missing: 198-203) ---

    @patch('wapi.commands.auth.os.chmod')
    @patch('wapi.commands.auth.Path')
    def test_cmd_auth_login_generic_exception(self, mock_path_cls, mock_chmod):
        """Test cmd_auth_login catching generic exception during credential save (lines 198-201)"""
        mock_chmod.side_effect = Exception("Chmod failed unexpectedly") # Force generic exception on chmod

        mock_path = Mock()
        mock_path.exists.return_value = False # So it writes a new file
        mock_path.parent.mkdir.return_value = None # Mock mkdir
        mock_path_cls.return_value = mock_path
        
        # Mock open to succeed initially
        m_open = unittest.mock.mock_open()
        
        args = Mock()
        args.config = "test.env"
        args.username = "user@example.com"
        args.password = "password"

        with patch('wapi.commands.auth.validate_credentials', return_value=(True, None)):
            with patch('wapi.commands.auth.WedosAPIClient') as mock_api_client_cls:
                mock_api_client_cls.return_value.ping.return_value = {'response': {'code': '1000'}}
                with patch('builtins.open', m_open):
                            ret = cmd_auth_login(args)
                            self.assertEqual(ret, EXIT_ERROR)
                            self.assertIn("Error: Could not save credentials:", sys.stderr.getvalue())
    # --- wapi/utils/interactive.py (Missing: 71-73) - specific inner loop exception ---

    # --- wapi/commands/search.py (Missing: 86, 107, 115, 121, 155-162, 221, 285) ---

    @patch('wapi.commands.search.interpret_status_value')
    def test_search_interpret_api_availability_data_structures(self, mock_interpret_status_value):
        """Test interpret_api_availability with various data structures (lines 107, 115, 121)"""
        from wapi.commands.search import interpret_api_availability
        
        domain_name = "example.com"
        
        # Test 'domain' is a dict (line 107)
        mock_interpret_status_value.return_value = None
        api_result_dict_domain = {'response': {'code': '1000', 'data': {'domain': {'name': domain_name, 'status': 'unknown'}}}}
        self.assertIsNone(interpret_api_availability(api_result_dict_domain, domain_name))
        
        # Test 'domain' is a list (line 108)
        mock_interpret_status_value.return_value = None
        api_result_list_domain = {'response': {'code': '1000', 'data': {'domain': [{'name': domain_name, 'status': 'unknown'}]}}}
        self.assertIsNone(interpret_api_availability(api_result_list_domain, domain_name))

        # Test 'domains' is a dict (line 115)
        mock_interpret_status_value.return_value = None
        api_result_dict_domains = {'response': {'code': '1000', 'data': {'domains': {'name': domain_name, 'status': 'unknown'}}}}
        self.assertIsNone(interpret_api_availability(api_result_dict_domains, domain_name))
        
        # Test 'domains' is a list (line 116)
        mock_interpret_status_value.return_value = None
        api_result_list_domains = {'response': {'code': '1000', 'data': {'domains': [{'name': domain_name, 'status': 'unknown'}]}}}
        self.assertIsNone(interpret_api_availability(api_result_list_domains, domain_name))

        # Test 'availability' in data (line 121)
        mock_interpret_status_value.return_value = None
        api_result_availability = {'response': {'code': '1000', 'data': {'availability': {'domain': domain_name, 'status': 'unknown'}}}}
        self.assertIsNone(interpret_api_availability(api_result_availability, domain_name))

        # Test that name mismatch in entry continues (lines 126-127)
        mock_interpret_status_value.return_value = None # Ensure it returns None here
        api_result_mismatch = {'response': {'code': '1000', 'data': {'domain': [{'name': 'other.com', 'status': 'available'}]}}}
        self.assertIsNone(interpret_api_availability(api_result_mismatch, domain_name))

        # Test fallback to top-level flags (lines 135-137)
        mock_interpret_status_value.return_value = True
        api_result_top_level = {'response': {'code': '1000', 'data': {'state': 'available'}}}
        self.assertTrue(interpret_api_availability(api_result_top_level, domain_name))

        # Test code not 1000 (line 98)
        api_result_error_code = {'response': {'code': '2000'}}
        self.assertIsNone(interpret_api_availability(api_result_error_code, domain_name))

        # Test empty data (line 104)
        mock_interpret_status_value.return_value = None # Explicitly set to None for this case
        api_result_empty_data = {'response': {'code': '1000', 'data': None}}
        self.assertIsNone(interpret_api_availability(api_result_empty_data, domain_name))


    @patch('wapi.commands.search._query_whois')
    def test_discover_whois_server_generic_exception(self, mock_query_whois):
        """Test _discover_whois_server catching generic Exception (lines 155-162)"""
        from wapi.commands.search import _discover_whois_server
        mock_query_whois.side_effect = Exception("Discovery failed")
        
        server = _discover_whois_server("example.com", 10)
        self.assertIsNone(server)
        # Check that the logger.debug was called (sys.stderr is not used here)
        # To check logger, we would need to mock the logger itself or capture its output.
        # For now, just ensuring the code path is hit.

    @patch('wapi.commands.search._query_whois')
    @patch('wapi.commands.search._discover_whois_server')
    def test_perform_whois_lookup_generic_exception(self, mock_discover, mock_query_whois):
        """Test perform_whois_lookup catching generic Exception (line 221)"""
        from wapi.commands.search import perform_whois_lookup
        from wapi.exceptions import WAPIRequestError
        
        mock_discover.return_value = "whois.test" # Ensure server is found
        mock_query_whois.side_effect = Exception("Query failed")
        
        with self.assertRaises(WAPIRequestError):
            perform_whois_lookup("example.com")
        # Check that the logger.error was called (sys.stderr is not used here)

    @patch('wapi.commands.search.perform_whois_lookup')
    @patch('wapi.commands.search.interpret_api_availability', return_value=None)
    @patch('wapi.commands.search.get_client') # We'll mock the client instance next
    @patch('wapi.commands.search.validate_domain', return_value=(True, None))
    def test_cmd_search_unspecified_availability(self, mock_validate, mock_get_client, mock_interpret_api, mock_perform_whois):
        """Test cmd_search when availability cannot be determined (line 285)"""
        from wapi.commands.search import cmd_search
        from wapi.exceptions import WAPIRequestError
        
        mock_client_instance = Mock()
        mock_client_instance.domain_availability.side_effect = Exception("WAPI error")
        mock_get_client.return_value = mock_client_instance # Ensure get_client returns a client that errors

        mock_perform_whois.side_effect = Exception("WHOIS error") # WHOIS also fails
        
        args = Mock()
        args.domain = "example.com"
        args.config = "config.env"
        args.format = "json"
        
        with self.assertRaises(WAPIRequestError):
            cmd_search(args)
        self.assertIn("Could not determine domain availability", sys.stderr.getvalue())
        # Check logger for "WAPI availability lookup failed"
        # Check logger for "WHOIS lookup failed"

    # --- wapi/commands/domain.py (Missing: various error paths) ---

    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    def test_cmd_domain_create_api_generic_error(self, mock_validate):
        """Test cmd_domain_create with generic API error (lines 399-401 for generic error)"""
        from wapi.commands.domain import cmd_domain_create
        from wapi.exceptions import WAPIRequestError
        
        client = Mock()
        client.domain_create.return_value = {'response': {'code': '2000', 'result': 'Generic Create Error'}}
        
        args = Mock()
        args.domain = "example.com"
        args.format = "json"
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_create(args, client)
        self.assertIn("Error (2000): Generic Create Error", sys.stderr.getvalue())

    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    @patch('wapi.utils.validators.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '1.1.1.1'}, None))
    @patch('wapi.utils.dns_lookup.enhance_nameserver_with_ipv6', return_value=({'name': 'ns1.example.com', 'addr_ipv4': '1.1.1.1', 'addr_ipv6': '::1'}, True, None))
    def test_cmd_domain_update_ns_api_generic_error(self, mock_enhance, mock_validate_ns, mock_validate_domain):
        from wapi.commands.domain import cmd_domain_update_ns
        from wapi.exceptions import WAPIRequestError
        
        client = Mock()
        client.domain_update_ns.return_value = {'response': {'code': '2000', 'result': 'Generic Update NS Error'}}
        
        args = Mock()
        args.domain = "example.com"
        args.nameserver = ["ns1.example.com"]
        args.format = "json"
        args.wait = False
        args.no_ipv6_discovery = True # Disable IPv6 discovery to simplify
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_update_ns(args, client)
        self.assertIn("Error (2000): Generic Update NS Error", sys.stderr.getvalue())

    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    def test_cmd_domain_transfer_api_generic_error(self, mock_validate):
        """Test cmd_domain_transfer with generic API error (lines 427-430)"""
        from wapi.commands.domain import cmd_domain_transfer
        from wapi.exceptions import WAPIRequestError
        
        client = Mock()
        client.domain_transfer.return_value = {'response': {'code': '2000', 'result': 'Generic Transfer Error'}}
        
        args = Mock()
        args.domain = "example.com"
        args.auth_info = "authcode"
        args.format = "json"
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_transfer(args, client)
        self.assertIn("Error (2000): Generic Transfer Error", sys.stderr.getvalue())

    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    def test_cmd_domain_renew_api_generic_error(self, mock_validate):
        """Test cmd_domain_renew with generic API error (lines 516-519)"""
        from wapi.commands.domain import cmd_domain_renew
        from wapi.exceptions import WAPIRequestError
        
        client = Mock()
        client.domain_renew.return_value = {'response': {'code': '2000', 'result': 'Generic Renew Error'}}
        
        args = Mock()
        args.domain = "example.com"
        args.format = "json"
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_renew(args, client)
        self.assertIn("Error (2000): Generic Renew Error", sys.stderr.getvalue())

    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    def test_cmd_domain_delete_api_generic_error(self, mock_validate):
        """Test cmd_domain_delete with generic API error (lines 549-552)"""
        from wapi.commands.domain import cmd_domain_delete
        from wapi.exceptions import WAPIRequestError
        
        client = Mock()
        client.domain_delete.return_value = {'response': {'code': '2000', 'result': 'Generic Delete Error'}}
        
        args = Mock()
        args.domain = "example.com"
        args.force = True # Skip confirmation
        args.format = "json"
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_delete(args, client)
        self.assertIn("Error (2000): Generic Delete Error", sys.stderr.getvalue())

    def test_cmd_domain_update_no_params(self):
        """Test cmd_domain_update with no update parameters (lines 656-658)"""
        from wapi.commands.domain import cmd_domain_update
        from wapi.exceptions import WAPIValidationError
        
        args = Mock()
        args.domain = "example.com"
        args.owner_c = None
        args.admin_c = None
        args.tech_c = None
        args.nsset = None
        args.keyset = None
        args.auth_info = None
        
        client = Mock() # Client won't be called
        
        with self.assertRaises(WAPIValidationError):
            cmd_domain_update(args, client)
        self.assertIn("Error: At least one of --owner-c, --admin-c, --tech-c, --nsset, --keyset, or --auth-info must be provided", sys.stderr.getvalue())

    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    def test_cmd_domain_update_api_generic_error(self, mock_validate):
        """Test cmd_domain_update with generic API error (lines 684-687)"""
        from wapi.commands.domain import cmd_domain_update
        from wapi.exceptions import WAPIRequestError
        
        client = Mock()
        client.domain_update.return_value = {'response': {'code': '2000', 'result': 'Generic Update Error'}}
        
        args = Mock()
        args.domain = "example.com"
        args.owner_c = "OWNER-C" # Provide one param to pass initial check
        args.admin_c = None
        args.tech_c = None
        args.nsset = None
        args.keyset = None
        args.auth_info = None
        args.format = "json"
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_update(args, client)
        self.assertIn("Error (2000): Generic Update Error", sys.stderr.getvalue())
        
    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    @patch('wapi.commands.domain.DEFAULT_MAX_POLL_ATTEMPTS', 1) # Speed up polling
    @patch('wapi.commands.domain.DEFAULT_POLL_INTERVAL', 0.1) # Speed up polling
    def test_cmd_domain_renew_polling_timeout(self, mock_validate):
        """Test cmd_domain_renew with polling timeout (lines 520-523)"""
        from wapi.commands.domain import cmd_domain_renew
        from wapi.exceptions import WAPITimeoutError
        
        client = Mock()
        client.domain_renew.return_value = {'response': {'code': '1001', 'result': 'Renewal started'}}
        # Simulate poll timeout
        client.poll_until_complete.return_value = {'response': {'code': '9998', 'result': 'Polling timeout'}}
        
        args = Mock()
        args.domain = "example.com"
        args.format = "json"
        args.wait = True # Enable polling
        args.quiet = True # Suppress verbose polling output
        
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_renew(args, client)
        self.assertIn("Polling timeout", sys.stderr.getvalue())

if __name__ == '__main__':
    unittest.main()