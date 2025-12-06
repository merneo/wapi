"""
Unit tests to cover remaining missing lines for 100% coverage.
Targeting:
- wapi/commands/auth.py (198-203)
- wapi/commands/contact.py (85)
- wapi/commands/nsset.py (219)
- wapi/utils/config_wizard.py (63-64, 124-134)
"""
import unittest
from unittest.mock import Mock, patch
import sys
from io import StringIO

from wapi.commands.auth import cmd_auth_logout
from wapi.commands.contact import cmd_contact_list
from wapi.commands.nsset import cmd_nsset_list
from wapi.utils.config_wizard import run_config_wizard, save_config
from wapi.constants import EXIT_ERROR

class TestFullCoverage(unittest.TestCase):
    
    def setUp(self):
        self.original_stderr = sys.stderr
        sys.stderr = StringIO()
        
    def tearDown(self):
        sys.stderr = self.original_stderr

    # --- Auth: cmd_auth_logout exceptions (198-203) ---
    @patch('wapi.commands.auth.Path')
    def test_auth_logout_unlink_exception(self, mock_path_cls):
        """Test exception during file deletion in logout"""
        mock_path = Mock()
        mock_path.exists.return_value = True
        # Raise generic exception on unlink
        mock_path.unlink.side_effect = Exception("Disk error")
        mock_path_cls.return_value = mock_path
        
        args = Mock()
        args.config = "test.env"
        
        ret = cmd_auth_logout(args)
        self.assertEqual(ret, EXIT_ERROR)

    # --- Contact: cmd_contact_list implementation check (85) ---
    def test_contact_list_not_implemented_response(self):
        """Test contact list when API returns error/not implemented"""
        client = Mock()
        # Return a code that is NOT 1000/1001
        client.call.return_value = {'response': {'code': '2000', 'result': 'Not implemented'}}
        
        from wapi.exceptions import WAPIRequestError
        with self.assertRaises(WAPIRequestError):
            cmd_contact_list(Mock(), client)

    # --- NSSET: cmd_nsset_list implementation check (219) ---
    def test_nsset_list_not_implemented_response(self):
        """Test nsset list when API returns error/not implemented"""
        client = Mock()
        client.call.return_value = {'response': {'code': '2000', 'result': 'Not implemented'}}
        
        from wapi.exceptions import WAPIRequestError
        with self.assertRaises(WAPIRequestError):
            cmd_nsset_list(Mock(), client)

    # --- Config Wizard: Input exceptions (63-64) ---
    @patch('builtins.input')
    def test_config_wizard_url_input_exception(self, mock_input):
        """Test StopIteration/EOF during URL input"""
        # Sequence: username -> password (via getpass) -> URL (RAISE)
        mock_input.side_effect = ["user", StopIteration, "yes", "yes"]
        
        with patch('wapi.utils.config_wizard.getpass', return_value="pass"):
            with patch('wapi.utils.config_wizard.save_config', return_value=True):
                with patch('builtins.print'):
                    with patch('wapi.utils.config_wizard.os.chmod'):
                        with patch('builtins.open', unittest.mock.mock_open()):
                             # Should catch StopIteration and use default URL
                             res = run_config_wizard("c.env")
                             self.assertTrue(res)

    # --- Config Wizard: save_config helper (124-134) ---
    def test_save_config_helper_success(self):
        """Test save_config helper success"""
        with patch('builtins.open', unittest.mock.mock_open()):
            with patch('wapi.utils.config_wizard.os.chmod'):
                res = save_config("test.env", {"K": "V"})
                self.assertTrue(res)

    def test_save_config_helper_failure(self):
        """Test save_config helper failure"""
        with patch('builtins.open', side_effect=Exception("Write failed")):
            res = save_config("test.env", {"K": "V"})
            self.assertFalse(res)

if __name__ == '__main__':
    unittest.main()
