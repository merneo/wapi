"""
Unit tests for contact command operations

Tests for contact commands: info, list.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.contact import cmd_contact_info, cmd_contact_list
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR, API_SUCCESS
from wapi.exceptions import WAPIRequestError, WAPIValidationError


class TestContactInfoCommand(unittest.TestCase):
    """Test contact info command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.contact.format_output')
    @patch('wapi.commands.contact.get_logger')
    def test_cmd_contact_info_success(self, mock_get_logger, mock_format_output):
        """Test successful contact info command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.id = 'CONTACT-EXAMPLE'
        self.mock_args.format = 'table'
        
        # Mock successful API response
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'contact': {
                        'id': 'CONTACT-EXAMPLE',
                        'name': 'John Doe',
                        'email': 'john@example.com'
                    }
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_contact_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.call.assert_called_once()
        mock_format_output.assert_called_once()

    @patch('wapi.commands.contact.get_logger')
    def test_cmd_contact_info_api_error(self, mock_get_logger):
        """Test contact info with API error"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.id = 'CONTACT-EXAMPLE'
        self.mock_args.format = 'table'
        
        # Mock failed API response
        mock_response = {
            'response': {
                'code': '2000',
                'result': 'Contact not found'
            }
        }
        self.mock_client.call.return_value = mock_response
        
        with self.assertRaises(WAPIRequestError):
            result = cmd_contact_info(self.mock_args, self.mock_client)


class TestContactListCommand(unittest.TestCase):
    """Test contact list command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.contact.get_logger')
    def test_cmd_contact_list_not_implemented(self, mock_get_logger):
        """Test contact list command (not yet implemented)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.format = 'table'
        
        # Contact list is not implemented, should raise error
        with self.assertRaises(WAPIRequestError) as context:
            result = cmd_contact_list(self.mock_args, self.mock_client)
        
        self.assertIn('not yet implemented', str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()
