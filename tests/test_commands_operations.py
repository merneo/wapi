"""
Unit tests for command operations (successful execution paths)

Tests for successful command execution, API response handling, and output formatting.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from wapi.commands.domain import cmd_domain_info, cmd_domain_list, cmd_domain_update_ns
from wapi.commands.dns import (
    cmd_dns_list,
    cmd_dns_record_list,
    cmd_dns_record_add,
    cmd_dns_record_update,
    cmd_dns_record_delete,
)
from wapi.commands.nsset import cmd_nsset_create, cmd_nsset_info, cmd_nsset_list
from wapi.constants import EXIT_SUCCESS, EXIT_ERROR, API_SUCCESS
from wapi.exceptions import WAPIRequestError


class TestDomainCommandsOperations(unittest.TestCase):
    """Test domain command operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    @patch('wapi.commands.domain.validate_domain')
    def test_cmd_domain_info_success(self, mock_validate, mock_get_logger, mock_format_output):
        """Test successful domain info command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'table'
        
        # Mock successful API response - domain_info returns {'response': {'code': ..., 'data': ...}}
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'name': 'example.com',
                        'status': 'ok',
                        'expire': '2025-12-31'
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_response
        
        result = cmd_domain_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_info.assert_called_once_with('example.com')
        mock_format_output.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    def test_cmd_domain_list_success(self, mock_get_logger, mock_format_output):
        """Test successful domain list command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.tld = None
        self.mock_args.status = None
        self.mock_args.format = 'table'
        
        # Mock successful API response - call() returns {'response': {'code': ..., 'data': ...}}
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': [
                        {'name': 'example.com', 'status': 'ok'},
                        {'name': 'test.cz', 'status': 'ok'}
                    ]
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_domain_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.call.assert_called_once()
        mock_format_output.assert_called_once()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    def test_cmd_domain_list_with_filters(self, mock_get_logger, mock_format_output):
        """Test domain list command with filters"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.tld = 'cz'
        self.mock_args.status = 'ok'
        self.mock_args.format = 'json'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'domain': []}
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_domain_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify call was made
        self.mock_client.call.assert_called_once()

    @patch('wapi.utils.dns_lookup.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    @patch('wapi.commands.domain.validate_domain')
    def test_cmd_domain_update_ns_success(self, mock_validate, mock_get_logger, mock_format_output, mock_enhance):
        """Test successful domain update-ns command"""
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
        
        # Mock enhanced nameserver (returns tuple: (nameserver_dict, found, warning))
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        # Mock successful API response - domain_update_ns uses client.domain_update_ns()
        # The response structure is: {'response': {'code': ..., 'data': ...}}
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        # domain_update_ns calls client.domain_update_ns() which returns the full response
        self.mock_client.domain_update_ns.return_value = mock_response
        
        result = cmd_domain_update_ns(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify domain_update_ns was called
        self.mock_client.domain_update_ns.assert_called_once()


class TestDNSCommandsOperations(unittest.TestCase):
    """Test DNS command operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_cmd_dns_list_success(self, mock_validate, mock_get_logger, mock_format_output):
        """Test successful DNS list command"""
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
                        'dns': {
                            'server': []
                        }
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_response
        
        result = cmd_dns_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.domain_info.assert_called_once_with('example.com')

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_cmd_dns_record_list_success(self, mock_validate, mock_get_logger, mock_format_output):
        """Test successful DNS record list command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'row': [
                        {'ID': '1', 'name': 'www', 'rdtype': 'A', 'rdata': '192.0.2.1'}
                    ]
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_dns_record_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.call.assert_called_once()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_cmd_dns_record_add_success(self, mock_validate, mock_get_logger, mock_format_output):
        """Test successful DNS record add command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = 'www'
        self.mock_args.type = 'A'
        self.mock_args.rdata = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'id': '123'}
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.call.assert_called_once()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_cmd_dns_record_update_success(self, mock_validate, mock_get_logger, mock_format_output):
        """Test successful DNS record update command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '123'
        self.mock_args.name = 'www'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.2'
        self.mock_args.ttl = 7200
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.call.assert_called_once()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_cmd_dns_record_delete_success(self, mock_validate, mock_get_logger, mock_format_output):
        """Test successful DNS record delete command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '123'
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'result': 'success'}
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.call.assert_called_once()


class TestNSSETCommandsOperations(unittest.TestCase):
    """Test NSSET command operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.utils.dns_lookup.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_cmd_nsset_create_success(self, mock_get_logger, mock_format_output, mock_enhance):
        """Test successful NSSET create command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.name = 'NSSET-EXAMPLE'
        self.mock_args.nameserver = ['ns1.example.com:192.0.2.1']
        self.mock_args.tld = 'cz'
        self.mock_args.tech_c = None
        self.mock_args.wait = False
        self.mock_args.no_ipv6_discovery = False
        self.mock_args.format = 'table'
        
        # Mock enhanced nameserver (returns tuple: (nameserver_dict, found, warning))
        mock_enhance.return_value = ({
            'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'
        }, True, None)
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'id': 'NSSET-EXAMPLE'}
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_nsset_create(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.call.assert_called_once()

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_cmd_nsset_info_success(self, mock_get_logger, mock_format_output):
        """Test successful NSSET info command"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.id = 'NSSET-EXAMPLE'
        self.mock_args.format = 'table'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'nsset': {
                        'id': 'NSSET-EXAMPLE',
                        'nameservers': []
                    }
                }
            }
        }
        self.mock_client.call.return_value = mock_response
        
        result = cmd_nsset_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.call.assert_called_once()

    @patch('wapi.commands.nsset.format_output')
    @patch('wapi.commands.nsset.get_logger')
    def test_cmd_nsset_list_not_implemented(self, mock_get_logger, mock_format_output):
        """Test NSSET list command (not yet implemented)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        self.mock_args.format = 'table'
        
        # NSSET list is not implemented, should raise error
        with self.assertRaises(WAPIRequestError) as context:
            result = cmd_nsset_list(self.mock_args, self.mock_client)
        
        self.assertIn('not yet implemented', str(context.exception).lower())


class TestCommandsOutputFormatting(unittest.TestCase):
    """Test command output formatting"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.format_output')
    @patch('wapi.commands.domain.get_logger')
    @patch('wapi.commands.domain.validate_domain')
    def test_domain_info_json_format(self, mock_validate, mock_get_logger, mock_format_output):
        """Test domain info with JSON format"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'json'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {'domain': {}}
            }
        }
        self.mock_client.domain_info.return_value = mock_response
        
        result = cmd_domain_info(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify format_output was called with 'json'
        call_args = mock_format_output.call_args[0]
        self.assertEqual(call_args[1], 'json')

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_list_yaml_format(self, mock_validate, mock_get_logger, mock_format_output):
        """Test DNS list with YAML format"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        # Ensure domain is a string, not a Mock
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'yaml'
        
        mock_response = {
            'response': {
                'code': API_SUCCESS,
                'data': {
                    'domain': {
                        'dns': {
                            'server': []
                        }
                    }
                }
            }
        }
        self.mock_client.domain_info.return_value = mock_response
        
        result = cmd_dns_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        # Verify format_output was called with 'yaml'
        call_args = mock_format_output.call_args[0]
        self.assertEqual(call_args[1], 'yaml')


if __name__ == '__main__':
    unittest.main()
