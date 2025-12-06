"""
Comprehensive unit tests for domain commands

Tests for all code paths including edge cases, async operations, and error scenarios.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from wapi.commands.domain import cmd_domain_info, cmd_domain_list, cmd_domain_update_ns
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR, API_SUCCESS, API_ASYNC
from wapi.exceptions import WAPIRequestError, WAPIValidationError, WAPITimeoutError


class TestDomainInfoComprehensive(unittest.TestCase):
    """Comprehensive tests for domain info command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.filter_sensitive_domain_data')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_info_with_sensitive_data_filtering(self, mock_get_logger, mock_validate,
                                                      mock_filter, mock_format_output):
        """Test domain info filters sensitive data"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'example.com',
                        'auth_info': 'secret123',
                        'owner': 'OWNER-123'
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_response
        
        mock_filter.return_value = {'name': 'example.com', 'auth_info': '[HIDDEN]'}
        
        result = cmd_domain_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_filter.assert_called_once()


class TestDomainListComprehensive(unittest.TestCase):
    """Comprehensive tests for domain list command"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_list_single_domain(self, mock_get_logger, mock_format_output):
        """Test domain list with single domain (not a list)"""
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
    def test_domain_list_with_tld_filter(self, mock_get_logger, mock_format_output):
        """Test domain list with TLD filter"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.tld = 'cz'
        self.mock_args.status = None
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': [
                        {'name': 'example.cz', 'status': 'ok'},
                        {'name': 'test.com', 'status': 'ok'}  # Should be filtered out
                    ]
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_domain_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify TLD filter was applied
        call_args = mock_format_output.call_args[0]
        filtered_domains = call_args[0]
        # Should only contain .cz domains
        self.assertTrue(all(d['name'].endswith('.cz') for d in filtered_domains))

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_list_with_status_filter(self, mock_get_logger, mock_format_output):
        """Test domain list with status filter"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.tld = None
        self.mock_args.status = 'ok'
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': [
                        {'name': 'example.com', 'status': 'ok'},
                        {'name': 'test.com', 'status': 'expired'}  # Should be filtered out
                    ]
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_domain_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify status filter was applied
        call_args = mock_format_output.call_args[0]
        filtered_domains = call_args[0]
        # Should only contain 'ok' status
        self.assertTrue(all(d['status'] == 'ok' for d in filtered_domains))


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
    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_with_source_domain(self, mock_get_logger, mock_validate,
                                                mock_format_output, mock_enhance):
        """Test domain update-ns with --source-domain option"""
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
        
        # Mock domain_info for source domain
        mock_source_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
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
        
        # Mock enhance_nameserver_with_ipv6
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        # Mock domain_update_ns response
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        self.mock_client.domain_update_ns.return_value = mock_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify domain_info was called for source domain
        self.mock_client.domain_info.assert_called_with('source.com')

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_async_with_wait(self, mock_get_logger, mock_validate, mock_enhance):
        """Test domain update-ns with async operation and --wait flag"""
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
        
        # Mock async response (code 1001)
        mock_async_response = {
            'response': {
                'code': API_ASYNC,
                'data': {'result': 'async'}
            }
        }
        
        # Mock polling response (code 1000) with nsset assigned
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
        
        self.mock_client.domain_update_ns.return_value = mock_async_response
        self.mock_client.poll_until_complete.return_value = mock_poll_response
        
        with patch('wapi.utils.validators.validate_nameserver', return_value=(True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}, None)):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)
            
            self.assertEqual(result, EXIT_SUCCESS)
            # Verify polling was called
            self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_no_options(self, mock_get_logger, mock_validate):
        """Test domain update-ns with no options (should fail)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.nsset = None
        self.mock_args.nameserver = None
        self.mock_args.source_domain = None
        
        with self.assertRaises(WAPIValidationError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)


if __name__ == '__main__':
    unittest.main()
