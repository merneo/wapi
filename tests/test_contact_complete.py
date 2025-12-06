"""
Complete tests for contact commands to achieve 100% coverage

Tests for all code paths including edge cases.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.contact import cmd_contact_info, cmd_contact_list, filter_sensitive_contact_data
from wapi.constants import EXIT_SUCCESS, API_SUCCESS
from wapi.exceptions import WAPIRequestError


class TestContactComplete(unittest.TestCase):
    """Complete tests for contact commands"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    def test_filter_sensitive_contact_data_all_fields(self):
        """Test filter_sensitive_contact_data with all sensitive fields"""
        contact = {
            'id': 'CONTACT-123',
            'email': 'test@example.com',
            'email2': 'test2@example.com',
            'phone': '123456789',
            'fax': '987654321',
            'ident': 'ID123',
            'ident_type': 'PASSPORT',
            'addr_street': 'Street 123',
            'addr_city': 'City',
            'addr_zip': '12345',
            'notify_email': 'notify@example.com'
        }
        
        filtered = filter_sensitive_contact_data(contact)
        
        # All sensitive fields should be [HIDDEN]
        self.assertEqual(filtered['email'], '[HIDDEN]')
        self.assertEqual(filtered['email2'], '[HIDDEN]')
        self.assertEqual(filtered['phone'], '[HIDDEN]')
        self.assertEqual(filtered['fax'], '[HIDDEN]')
        self.assertEqual(filtered['ident'], '[HIDDEN]')
        self.assertEqual(filtered['ident_type'], '[HIDDEN]')
        self.assertEqual(filtered['addr_street'], '[HIDDEN]')
        self.assertEqual(filtered['addr_city'], '[HIDDEN]')
        self.assertEqual(filtered['addr_zip'], '[HIDDEN]')
        self.assertEqual(filtered['notify_email'], '[HIDDEN]')
        # Non-sensitive field should be preserved
        self.assertEqual(filtered['id'], 'CONTACT-123')

    @patch('wapi.commands.contact.format_output')
    @patch('wapi.commands.contact.get_logger')
    def test_contact_info_with_tld(self, mock_get_logger, mock_format_output):
        """Test contact info with TLD argument"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.handle = 'CONTACT-123'
        self.mock_args.tld = 'com'
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'contact': {
                        'id': 'CONTACT-123',
                        'name': 'Test Contact'
                    }
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_contact_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify call was made with correct TLD
        self.mock_client.call.assert_called_once_with("contact-info", {"name": "CONTACT-123", "tld": "com"})

    @patch('wapi.commands.contact.format_output')
    @patch('wapi.commands.contact.get_logger')
    def test_contact_info_without_tld(self, mock_get_logger, mock_format_output):
        """Test contact info without TLD (defaults to cz, line 52)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.handle = 'CONTACT-123'
        self.mock_args.tld = None
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'contact': {
                        'id': 'CONTACT-123',
                        'name': 'Test Contact'
                    }
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_contact_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify call was made with default TLD 'cz'
        self.mock_client.call.assert_called_once_with("contact-info", {"name": "CONTACT-123", "tld": "cz"})

    @patch('wapi.commands.contact.get_logger')
    def test_contact_info_api_error(self, mock_get_logger):
        """Test contact info with API error"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.handle = 'CONTACT-123'
        self.mock_args.tld = None
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': '2000',
                'result': 'Contact not found'
            }
        }
        self.mock_client.call.return_value = mock_response
        
        with self.assertRaises(WAPIRequestError):
            result = cmd_contact_info(self.mock_args, self.mock_client)

    @patch('wapi.commands.contact.get_logger')
    def test_contact_list_not_implemented(self, mock_get_logger):
        """Test contact list command (not implemented)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.format = 'table'
        
        with self.assertRaises(WAPIRequestError):
            result = cmd_contact_list(self.mock_args, self.mock_client)


if __name__ == '__main__':
    unittest.main()
