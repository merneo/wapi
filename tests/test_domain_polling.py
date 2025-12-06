"""
Tests for domain update-ns polling functionality

Tests for async polling scenarios and completion checks.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.domain import cmd_domain_update_ns
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC
from wapi.exceptions import WAPITimeoutError


class TestDomainUpdateNSPolling(unittest.TestCase):
    """Test domain update-ns polling scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_with_nsset_check(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling completion check for nsset_name"""
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
        
        # Mock polling response with matching nsset
        mock_poll_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'nsset': 'NSSET-EXAMPLE'  # Matches what we set
                    }
                }
            }
        }
        self.mock_client.poll_until_complete.return_value = mock_poll_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_with_nameservers_check(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling completion check for nameservers"""
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
        
        # Mock polling response with nsset assigned (any nsset means success)
        mock_poll_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'nsset': 'NSSET-NEW'  # Any nsset means nameservers were set
                    }
                }
            }
        }
        self.mock_client.poll_until_complete.return_value = mock_poll_response
        
        with patch('wapi.utils.validators.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)
            
            self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_with_source_domain_check(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling completion check for source domain copy"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = 'source.com'
        self.mock_args.wait = True
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock source domain info
        mock_source_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'source.com',
                        'dns': {
                            'server': [
                                {'name': 'ns1.source.com', 'addr_ipv4': '192.0.2.1'}
                            ]
                        }
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_source_response
        
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
        
        # Mock polling response with matching nameservers
        mock_poll_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'example.com',
                        'dns': {
                            'server': [
                                {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}
                            ]
                        }
                    }
                }
            }
        }
        # First call for source domain, then polling
        self.mock_client.domain_info.side_effect = [mock_source_response, mock_poll_response]
        self.mock_client.poll_until_complete.return_value = mock_poll_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_non_success_code(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling with non-success code (not timeout)"""
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
        
        # Mock polling response with error code but not timeout
        mock_poll_response = {
            'response': {
                'code': '2000',  # Error code (not 9998)
                'result': 'Some error'  # No 'timeout' in message
            }
        }
        self.mock_client.poll_until_complete.return_value = mock_poll_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        # Should return success (polling completed, even if with warning, but not timeout)
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_timeout_code(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling with timeout code (9998)"""
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
        
        # Mock polling response with timeout code
        mock_poll_response = {
            'response': {
                'code': '9998',  # Timeout code
                'result': 'Timeout'
            }
        }
        self.mock_client.poll_until_complete.return_value = mock_poll_response
        
        with self.assertRaises(WAPITimeoutError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)


if __name__ == '__main__':
    unittest.main()
