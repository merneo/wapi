"""
Comprehensive tests for domain commands to achieve 100% coverage

Tests for all code paths including edge cases, async operations, and error scenarios.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from wapi.commands.domain import (
    cmd_domain_info,
    cmd_domain_list,
    cmd_domain_update_ns,
    filter_sensitive_domain_data,
)
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC
from wapi.exceptions import WAPIRequestError, WAPIValidationError, WAPITimeoutError


class TestFilterSensitiveDomainData(unittest.TestCase):
    """Test filter_sensitive_domain_data function"""

    def test_filter_sensitive_fields(self):
        """Test that sensitive fields are filtered"""
        domain = {
            'name': 'example.com',
            'own_email': 'owner@example.com',
            'own_phone': '123456789',
            'own_addr_street': 'Street 123'
        }
        
        filtered = filter_sensitive_domain_data(domain)
        
        self.assertEqual(filtered['name'], 'example.com')
        self.assertEqual(filtered['own_email'], '[HIDDEN]')
        self.assertEqual(filtered['own_phone'], '[HIDDEN]')
        self.assertEqual(filtered['own_addr_street'], '[HIDDEN]')

    def test_filter_preserves_non_sensitive_fields(self):
        """Test that non-sensitive fields are preserved"""
        domain = {
            'name': 'example.com',
            'status': 'ok',
            'expiration': '2025-12-31'
        }
        
        filtered = filter_sensitive_domain_data(domain)
        
        self.assertEqual(filtered['name'], 'example.com')
        self.assertEqual(filtered['status'], 'ok')
        self.assertEqual(filtered['expiration'], '2025-12-31')


class TestDomainListComprehensive(unittest.TestCase):
    """Comprehensive tests for domain list command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_list_single_domain_dict(self, mock_get_logger, mock_format_output):
        """Test domain list with single domain dict (not a list)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.tld = None
        self.mock_args.status = None
        self.mock_args.format = 'table'
        
        # API sometimes returns single domain dict instead of list
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {'name': 'example.com', 'status': 'ok'}  # Single dict, not list
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_domain_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format_output.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_list_non_dict_domain(self, mock_get_logger, mock_format_output):
        """Test domain list with non-dict domain entries"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.tld = None
        self.mock_args.status = None
        self.mock_args.format = 'table'
        
        # Domain entry that is not a dict (edge case)
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': ['string', {'name': 'example.com', 'status': 'ok'}]
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_domain_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Should only process dict entries
        call_args = mock_format_output.call_args[0]
        domain_list = call_args[0]
        self.assertEqual(len(domain_list), 1)  # Only dict entry processed


class TestDomainUpdateNSComprehensive(unittest.TestCase):
    """Comprehensive tests for domain update-ns command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_with_nsset(self, mock_get_logger, mock_validate):
        """Test domain update-ns with --nsset option"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = 'NSSET-EXAMPLE'
        self.mock_args.nameserver = None
        self.mock_args.source_domain = None
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify domain_update_ns was called with nsset_name
        self.mock_client.domain_update_ns.assert_called_once()
        call_kwargs = self.mock_client.domain_update_ns.call_args[1]
        self.assertEqual(call_kwargs.get('nsset_name'), 'NSSET-EXAMPLE')

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.utils.validators.validate_nameserver')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_source_domain_error(self, mock_get_logger, mock_validate,
                                                  mock_validate_ns, mock_enhance):
        """Test domain update-ns with source domain that fails"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.com'
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock failed domain_info for source domain
        mock_source_response = {
            'response': {
                'code': '2000',
                'result': 'Domain not found'
            }
        }
        self.mock_client.domain_info.return_value = mock_source_response
        
        with self.assertRaises(WAPIRequestError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.utils.validators.validate_nameserver')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_source_domain_no_dns(self, mock_get_logger, mock_validate,
                                                   mock_validate_ns, mock_enhance):
        """Test domain update-ns with source domain that has no DNS"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.com'
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock domain_info with no DNS
        mock_source_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'source.com',
                        'dns': None  # No DNS dict
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_source_response
        
        with self.assertRaises(WAPIRequestError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.utils.validators.validate_nameserver')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_source_domain_single_server(self, mock_get_logger, mock_validate,
                                                         mock_validate_ns, mock_enhance):
        """Test domain update-ns with source domain that has single server (not list)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.com'
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock domain_info with single server (not a list)
        mock_source_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'source.com',
                        'dns': {
                            'server': {'name': 'ns1.source.com', 'addr_ipv4': '192.0.2.1'}  # Single dict, not list
                        }
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_source_response
        
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.utils.validators.validate_nameserver')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_source_domain_empty_servers(self, mock_get_logger, mock_validate,
                                                          mock_validate_ns, mock_enhance):
        """Test domain update-ns with source domain that has empty servers"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.com'
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock domain_info with empty servers list
        mock_source_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'source.com',
                        'dns': {
                            'server': []  # Empty list
                        }
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_source_response
        
        with self.assertRaises(WAPIRequestError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.utils.validators.validate_nameserver')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_source_domain_different_tld(self, mock_get_logger, mock_validate,
                                                           mock_validate_ns, mock_enhance):
        """Test domain update-ns with source domain different TLD"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.cz'  # Different TLD
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock domain_info for source domain
        mock_source_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'source.cz',
                        'dns': {
                            'server': [
                                {'name': 'ns1.source.cz', 'addr_ipv4': '192.0.2.1'}
                            ]
                        }
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_source_response
        
        mock_enhance.return_value = ({
            'name': 'ns1.source.cz', 'addr_ipv4': '192.0.2.1'  # Name not replaced (different TLD)
        }, True, None)
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.utils.validators.validate_nameserver')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_async_no_wait(self, mock_get_logger, mock_validate,
                                           mock_validate_ns, mock_enhance):
        """Test domain update-ns with async operation but no --wait flag"""
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
        
        mock_validate_ns.return_value = (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        # Mock async response (code 1001) without wait
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_async_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Should not poll
        self.mock_client.domain_info.assert_not_called()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.utils.validators.validate_nameserver')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_async_polling_timeout(self, mock_get_logger, mock_validate,
                                                   mock_validate_ns, mock_enhance):
        """Test domain update-ns with async operation that times out"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = ['ns1.example.com:192.0.2.1']
        self.mock_args.source_domain = None
        self.mock_args.wait = True
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        mock_validate_ns.return_value = (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        # Mock async response
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_async_response
        
        # Mock polling timeout
        from wapi.exceptions import WAPITimeoutError
        self.mock_client.poll_until_complete.side_effect = WAPITimeoutError("Polling timeout")
        
        with self.assertRaises(WAPITimeoutError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_no_ipv6_discovery(self, mock_get_logger, mock_validate, mock_enhance):
        """Test domain update-ns with --no-ipv6-discovery flag"""
        from wapi.utils.validators import validate_nameserver
        
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
        
        # validate_nameserver is called inside the function, so we patch it where it's used
        with patch('wapi.utils.validators.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
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


if __name__ == '__main__':
    unittest.main()
