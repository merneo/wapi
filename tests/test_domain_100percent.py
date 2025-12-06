"""
Tests to achieve 100% coverage for domain commands

Tests for remaining uncovered lines.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.domain import cmd_domain_update_ns, filter_sensitive_domain_data
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC
from wapi.exceptions import WAPIRequestError


class TestDomain100Percent(unittest.TestCase):
    """Tests for 100% domain coverage"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    def test_filter_sensitive_domain_data_all_fields(self):
        """Test filter_sensitive_domain_data with all sensitive fields"""
        domain = {
            'name': 'example.com',
            'own_email': 'owner@example.com',
            'own_email2': 'owner2@example.com',
            'own_phone': '123456789',
            'own_fax': '987654321',
            'own_dic': 'CZ12345678',
            'own_ic': '12345678',
            'own_other': 'Other info',
            'own_addr_street': 'Street 123',
            'own_addr_city': 'City',
            'own_addr_zip': '12345',
            'own_name': 'John Doe',
            'own_fname': 'John',
            'own_lname': 'Doe'
        }
        
        filtered = filter_sensitive_domain_data(domain)
        
        # All sensitive fields should be [HIDDEN]
        self.assertEqual(filtered['own_email'], '[HIDDEN]')
        self.assertEqual(filtered['own_email2'], '[HIDDEN]')
        self.assertEqual(filtered['own_phone'], '[HIDDEN]')
        self.assertEqual(filtered['own_fax'], '[HIDDEN]')
        self.assertEqual(filtered['own_dic'], '[HIDDEN]')
        self.assertEqual(filtered['own_ic'], '[HIDDEN]')
        self.assertEqual(filtered['own_other'], '[HIDDEN]')
        self.assertEqual(filtered['own_addr_street'], '[HIDDEN]')
        self.assertEqual(filtered['own_addr_city'], '[HIDDEN]')
        self.assertEqual(filtered['own_addr_zip'], '[HIDDEN]')
        self.assertEqual(filtered['own_name'], '[HIDDEN]')
        self.assertEqual(filtered['own_fname'], '[HIDDEN]')
        self.assertEqual(filtered['own_lname'], '[HIDDEN]')
        # Non-sensitive field should be preserved
        self.assertEqual(filtered['name'], 'example.com')

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_invalid_domain(self, mock_get_logger, mock_validate):
        """Test domain update-ns with invalid domain"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        
        self.mock_args.domain = 'invalid..domain'
        self.mock_args.nsset = 'NSSET-EXAMPLE'
        
        from wapi.exceptions import WAPIValidationError
        with self.assertRaises(WAPIValidationError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_no_ipv6_discovery_with_ipv4(self, mock_get_logger, mock_validate, mock_enhance):
        """Test domain update-ns with --no-ipv6-discovery when IPv4 exists but no IPv6"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = ['ns1.example.com:192.0.2.1']
        self.mock_args.source_domain = None
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = True  # IPv6 discovery disabled
        self.mock_args.format = 'table'
        
        # Nameserver has IPv4 but no IPv6
        with patch('wapi.utils.validators.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1', 'addr_ipv6': ''}, None)):
            mock_response = {
                'response': {
                    'code': API_SUCCESS,
                    'data': {'result': 'success'}
                }
            }
            self.mock_client.domain_update_ns.return_value = mock_response
            
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)
            
            self.assertEqual(result, EXIT_SUCCESS)
            # Should not call enhance_nameserver_with_ipv6 when no_ipv6_discovery is True
            mock_enhance.assert_not_called()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_ipv6_found_with_warning(self, mock_get_logger, mock_validate, mock_enhance):
        """Test domain update-ns when IPv6 is found but with warning"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = ['ns1.example.com:192.0.2.1']
        self.mock_args.source_domain = None
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock enhance_nameserver_with_ipv6 to return found=False but with warning
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, False, "IPv6 address not found")
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_response
        
        with patch('wapi.utils.validators.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)
            
            self.assertEqual(result, EXIT_SUCCESS)
            # Should call enhance_nameserver_with_ipv6
            mock_enhance.assert_called_once()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_warning_not_timeout(self, mock_get_logger, mock_validate, mock_enhance):
        """Test domain update-ns polling with warning but not timeout"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = 'NSSET-EXAMPLE'
        self.mock_args.nameserver = None
        self.mock_args.source_domain = None
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        # Mock async response
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_async_response
        
        # Mock polling response with warning (not timeout)
        mock_poll_response = {
            'response': {
                'code': '2000',
                'result': 'Some warning message'  # No 'timeout' and not code 9998
            }
        }
        self.mock_client.poll_until_complete.return_value = mock_poll_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        # Should return success (warning but not timeout)
        self.assertEqual(result, EXIT_SUCCESS)


if __name__ == '__main__':
    unittest.main()
