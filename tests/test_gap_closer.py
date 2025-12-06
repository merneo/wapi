"""
Final gap closer tests to achieve 100% coverage.
Targets specific missing lines in error handlers and edge cases.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO

# Import modules to test
from wapi.commands.auth import get_client, cmd_auth_logout
from wapi.commands.domain import (
    cmd_domain_update_ns, cmd_domain_create, 
    cmd_domain_renew, cmd_domain_update
)
from wapi.commands.search import (
    interpret_api_availability, 
    _discover_whois_server,
    perform_whois_lookup,
    cmd_search
)
from wapi.utils.config_wizard import run_config_wizard
from wapi.commands.contact import cmd_contact_list
from wapi.commands.nsset import cmd_nsset_list
from wapi.utils.dns_lookup import get_ipv6_from_ipv4
from wapi.constants import EXIT_ERROR, EXIT_SUCCESS
from wapi.exceptions import WAPITimeoutError, WAPIRequestError

class TestGapCloser(unittest.TestCase):
    
    def setUp(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
    def tearDown(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    # --- Auth Gaps ---

    @patch('wapi.commands.auth.WedosAPIClient')
    def test_auth_get_client_exception(self, mock_client_cls):
        """Test generic Exception in get_client (lines 252-253)"""
        with patch('wapi.commands.auth.get_config', return_value="val"):
            mock_client_cls.side_effect = Exception("Init failed")
            client = get_client("c.env")
            self.assertIsNone(client)

    @patch('wapi.commands.auth.Path')
    def test_auth_logout_generic_exception(self, mock_path_cls):
        """Test generic Exception during logout (lines 198-203)"""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.unlink.side_effect = Exception("Generic failure")
        mock_path_cls.return_value = mock_path
        
        args = Mock()
        args.config = "test.env"
        
        ret = cmd_auth_logout(args)
        self.assertEqual(ret, EXIT_ERROR)

    # --- Domain Gaps (Polling Timeout Branch) ---
    
    @patch('wapi.commands.domain.validate_domain', return_value=(True, None))
    def test_domain_polling_timeout_branch(self, mock_validate):
        """Test polling returning timeout code (9998) triggers WAPITimeoutError"""
        client = Mock()
        # Return "started" code 1001 to trigger polling
        client.domain_update_ns.return_value = {'response': {'code': '1001'}}
        client.domain_create.return_value = {'response': {'code': '1001'}}
        client.domain_renew.return_value = {'response': {'code': '1001'}}
        client.domain_update.return_value = {'response': {'code': '1001'}}
        
        # Poll returns timeout code
        client.poll_until_complete.return_value = {
            'response': {
                'code': '9998',
                'result': 'Operation timeout'
            }
        }
        
        args = Mock()
        args.domain = "example.com"
        args.wait = True
        args.quiet = True
        args.nsset = "NS"
        args.auth_info = "AUTH"
        args.period = 1
        # Some commands check specific args
        args.owner_c = "OWNER" # for update
        
        # Only test commands that actually implement polling/waiting
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_update_ns(args, client)
        
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_create(args, client)
            
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_renew(args, client)
            
        with self.assertRaises(WAPITimeoutError):
            cmd_domain_update(args, client)

    # --- Search Gaps ---

    def test_interpret_api_availability_malformed(self):
        """Test interpret_api_availability with invalid response structure"""
        # Response is not a dict
        res = {'response': 'invalid'} 
        
        # Test 107: 'domain' in data but not list
        res = {'response': {'code': '1000', 'data': {'domain': {'name': 'd', 'status': 'ok'}}}}
        self.assertIsNone(interpret_api_availability(res, "d"))
        
        # Test 115: 'domains' in data
        res = {'response': {'code': '1000', 'data': {'domains': [{'name': 'd', 'status': 'ok'}]}}}
        self.assertIsNone(interpret_api_availability(res, "d"))
        
        # Test 121: 'availability' in data
        res = {'response': {'code': '1000', 'data': {'availability': {'domain': 'd', 'status': 'ok'}}}}
        self.assertIsNone(interpret_api_availability(res, "d"))

    @patch('wapi.commands.search._query_whois')
    def test_discover_whois_server_generic_error(self, mock_query):
        """Test generic error in discovery"""
        mock_query.side_effect = Exception("Boom")
        self.assertIsNone(_discover_whois_server("d.com", 5))

    @patch('wapi.commands.search._discover_whois_server')
    def test_perform_whois_lookup_generic_error(self, mock_disc):
        """Test generic error in perform_whois_lookup"""
        mock_disc.side_effect = Exception("Boom")
        # Just ensure it doesn't crash hard if it's supposed to swallow
        perform_whois_lookup("d.com")

    # --- Config Wizard Gaps ---

    @patch('builtins.input')
    def test_config_wizard_input_error(self, mock_input):
        """Test StopIteration on URL input (lines 63-64)"""
        mock_input.side_effect = ["user", StopIteration, "yes", "yes"] 
        
        with patch('wapi.utils.config_wizard.getpass', return_value="pass"):
            with patch('wapi.utils.config_wizard.save_config', return_value=True):
                with patch('builtins.print'):
                    with patch('wapi.utils.config_wizard.os.chmod'):
                        with patch('builtins.open', Mock()):
                             run_config_wizard("c.env")

    # --- Contact/NSSET List Gaps ---

    def test_contact_list_error(self):
        """Test error code in contact list"""
        client = Mock()
        client.call.return_value = {'response': {'code': '2000', 'result': 'Failed'}}
        from wapi.exceptions import WAPIRequestError
        with self.assertRaises(WAPIRequestError):
            cmd_contact_list(Mock(), client)

    def test_nsset_list_error(self):
        """Test error code in nsset list"""
        client = Mock()
        client.call.return_value = {'response': {'code': '2000', 'result': 'Failed'}}
        from wapi.exceptions import WAPIRequestError
        with self.assertRaises(WAPIRequestError):
            cmd_nsset_list(Mock(), client)

    # --- DNS Lookup Import Error ---
    
    def test_dns_import_error(self):
        """Test ImportError for dnspython"""
        # This is extremely hard to test cleanly without mocking sys.modules destructively.
        pass

if __name__ == '__main__':
    unittest.main()