"""
Complete tests for wapi.commands.dns module to achieve 100% coverage

Tests for missing lines: edge cases in DNS commands.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.dns import (
    cmd_dns_list,
    cmd_dns_record_list,
    cmd_dns_record_add,
    cmd_dns_record_update,
    cmd_dns_record_delete
)
from wapi.constants import EXIT_SUCCESS
from wapi.exceptions import WAPIRequestError, WAPIValidationError


class TestDNSListEdgeCases(unittest.TestCase):
    """Test cmd_dns_list edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_list_servers_not_list(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_list when servers is not a list (line 44)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'table'
        
        # Mock domain_info with server as single dict (not list)
        self.mock_client.domain_info.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'domain': {
                        'dns': {
                            'server': {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}  # Not a list
                        }
                    }
                }
            }
        }
        
        result = cmd_dns_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format.assert_called_once()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_list_server_not_dict(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_list when server entry is not a dict (lines 49-50)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'table'
        
        # Mock domain_info with server as string (not dict)
        self.mock_client.domain_info.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'domain': {
                        'dns': {
                            'server': ['not-a-dict', {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1'}]
                        }
                    }
                }
            }
        }
        
        result = cmd_dns_list(self.mock_args, self.mock_client)
        
        # Should skip non-dict entries
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format.assert_called_once()

    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_list_dns_not_dict(self, mock_validate, mock_get_logger):
        """Test cmd_dns_list when dns is not a dict (lines 60-62)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'table'
        
        # Mock domain_info with dns as string (not dict)
        self.mock_client.domain_info.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'domain': {
                        'dns': 'not-a-dict'
                    }
                }
            }
        }
        
        with self.assertRaises(WAPIRequestError) as context:
            cmd_dns_list(self.mock_args, self.mock_client)
        
        self.assertIn("No DNS information available", str(context.exception))


class TestDNSRecordListEdgeCases(unittest.TestCase):
    """Test cmd_dns_record_list edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_list_rows_not_list(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_list when rows is not a list (line 90)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.format = 'table'
        
        # Mock dns-rows-list with row as single dict (not list)
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {
                    'row': {'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}  # Not a list
                }
            }
        }
        
        result = cmd_dns_record_list(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format.assert_called_once()


class TestDNSRecordAddEdgeCases(unittest.TestCase):
    """Test cmd_dns_record_add edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_add_invalid_domain(self, mock_validate, mock_get_logger):
        """Test cmd_dns_record_add with invalid domain (lines 122-124)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        
        self.mock_args.domain = 'invalid-domain'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        
        with self.assertRaises(WAPIValidationError):
            cmd_dns_record_add(self.mock_args, self.mock_client)


class TestDNSRecordUpdateEdgeCases(unittest.TestCase):
    """Test cmd_dns_record_update edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_invalid_domain(self, mock_validate, mock_get_logger):
        """Test cmd_dns_record_update with invalid domain (lines 221-223)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        
        self.mock_args.domain = 'invalid-domain'
        self.mock_args.record_id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        
        with self.assertRaises(WAPIValidationError):
            cmd_dns_record_update(self.mock_args, self.mock_client)


class TestDNSRecordDeleteEdgeCases(unittest.TestCase):
    """Test cmd_dns_record_delete edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_invalid_domain(self, mock_validate, mock_get_logger):
        """Test cmd_dns_record_delete with invalid domain (lines 262-331)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (False, "Invalid domain format")
        
        self.mock_args.domain = 'invalid-domain'
        self.mock_args.record_id = '1'
        
        with self.assertRaises(WAPIValidationError):
            cmd_dns_record_delete(self.mock_args, self.mock_client)


class TestDNSRecordAddFullFlow(unittest.TestCase):
    """Test cmd_dns_record_add full flow including async operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_add_success_sync(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_add with synchronous success (lines 140-144)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {'result': 'OK'}
            }
        }
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        mock_format.assert_called()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_add_async_with_wait(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_add with async operation and wait (lines 145-201)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        # First call returns async
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns success with record
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Return result with record matching
                return {
                    'response': {
                        'code': '1000',
                        'data': {
                            'row': [{
                                'ID': '1',
                                'name': '@',
                                'rdtype': 'A',
                                'rdata': '192.0.2.1'
                            }]
                        }
                    }
                }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_called_once()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_add_async_timeout(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_add with async timeout (lines 194-201)"""
        from wapi.exceptions import WAPITimeoutError
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        # First call returns async
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns timeout
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '9998',
                'result': 'Timeout'
            }
        }
        
        with self.assertRaises(WAPITimeoutError):
            cmd_dns_record_add(self.mock_args, self.mock_client)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_add_async_warning(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_add with async warning (lines 194-201)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        # First call returns async
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns warning (not timeout)
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '1001',
                'result': 'Still processing'
            }
        }
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        # Should return success despite warning
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_add_check_record_added_edge_cases(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_add check_record_added with edge cases (lines 157-174)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        # First call returns async
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - simulate is_complete being called multiple times
        # The is_complete function will be called with different results
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Return result that will eventually match (after is_complete checks various cases)
                # The is_complete function checks: code, rows list, row dict, matching values
                return {
                    'response': {
                        'code': '1000',
                        'data': {
                            'row': [{
                                'ID': '1',
                                'name': '@',
                                'rdtype': 'A',
                                'rdata': '192.0.2.1'
                            }]
                        }
                    }
                }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_add_async_without_wait(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_add with async operation without wait (lines 202-204)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_not_called()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_add_error(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_add with error response (lines 205-209)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '2100',
                'result': 'Error occurred'
            }
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_dns_record_add(self.mock_args, self.mock_client)


class TestDNSRecordUpdateFullFlow(unittest.TestCase):
    """Test cmd_dns_record_update full flow"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_no_id(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update without ID (lines 225-228)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = None
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.format = 'table'
        
        with self.assertRaises(WAPIValidationError) as context:
            cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertIn("Record ID required", str(context.exception))

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_no_fields(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update without update fields (lines 231-234)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = None
        self.mock_args.type = None
        self.mock_args.value = None
        self.mock_args.ttl = None
        self.mock_args.format = 'table'
        
        with self.assertRaises(WAPIValidationError) as context:
            cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertIn("At least one field must be specified", str(context.exception))

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_success_sync(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update with synchronous success (lines 257-261)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {'result': 'OK'}
            }
        }
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_async_with_wait(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update with async and wait (lines 262-323)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        # First call returns async
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns success
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                return {
                    'response': {
                        'code': '1000',
                        'data': {
                            'row': [{
                                'ID': '1',
                                'name': '@',
                                'rdtype': 'A',
                                'rdata': '192.0.2.1'
                            }]
                        }
                    }
                }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_async_timeout(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update with async timeout (lines 316-323)"""
        from wapi.exceptions import WAPITimeoutError
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns timeout
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '9998',
                'result': 'Timeout'
            }
        }
        
        with self.assertRaises(WAPITimeoutError):
            cmd_dns_record_update(self.mock_args, self.mock_client)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_check_record_updated_edge_cases(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update check_record_updated with edge cases (lines 275-296)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - return result that matches (is_complete will check various cases internally)
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Return matching record
                return {
                    'response': {
                        'code': '1000',
                        'data': {
                            'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]
                        }
                    }
                }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_async_warning(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update with async warning (lines 316-323)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns warning (not timeout)
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '1001',
                'result': 'Still processing'
            }
        }
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        # Should return success despite warning
        self.assertEqual(result, EXIT_SUCCESS)


class TestDNSRecordDeleteFullFlow(unittest.TestCase):
    """Test cmd_dns_record_delete full flow"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_success_sync(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_delete with synchronous success"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.record_id = '1'
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1000',
                'data': {'result': 'OK'}
            }
        }
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_async_with_wait(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_delete with async and wait"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        # First call returns async
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns success (record deleted)
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Record not found (deleted)
                return {
                    'response': {
                        'code': '1000',
                        'data': {
                            'row': []  # Record deleted
                        }
                    }
                }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_no_id(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_delete without ID (lines 346-349)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = None
        self.mock_args.format = 'table'
        
        with self.assertRaises(WAPIValidationError) as context:
            cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertIn("Record ID required", str(context.exception))

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_async_without_wait(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_delete with async without wait (lines 417-418)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_not_called()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_async_timeout(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_delete with async timeout (lines 410-416)"""
        from wapi.exceptions import WAPITimeoutError
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns timeout
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '9998',
                'result': 'Timeout'
            }
        }
        
        with self.assertRaises(WAPITimeoutError):
            cmd_dns_record_delete(self.mock_args, self.mock_client)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_check_record_deleted_edge_cases(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_delete check_record_deleted with edge cases (lines 376-391)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - return result where record is deleted (not found)
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Record deleted (not in list)
                return {
                    'response': {
                        'code': '1000',
                        'data': {
                            'row': [{'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]
                        }
                    }
                }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_async_warning(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_delete with async warning (lines 410-416)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns warning (not timeout)
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '1001',
                'result': 'Still processing'
            }
        }
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        # Should return success despite warning
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_delete_error(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_delete with error response (lines 419-423)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '2100',
                'result': 'Error occurred'
            }
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_dns_record_delete(self.mock_args, self.mock_client)


class TestDNSRecordAddCheckFunctions(unittest.TestCase):
    """Test check_record_added function edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_added_code_not_1000(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_added with code not 1000 (lines 157-160)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - simulate that is_complete is called with different results
        # The check_record_added function checks poll_code, so we need to simulate
        # that poll_until_complete calls is_complete with results that eventually match
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Simulate polling: first attempt fails (code not 1000), second succeeds
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        # First attempt: code not 1000 -> returns False (covers line 159)
                        return False
                    else:
                        # Second attempt: code 1000 with matching record -> returns True
                        return True
                
                # Return results that will be passed to is_complete
                results = [
                    {'response': {'code': '1001'}},  # First: is_complete returns False
                    {'response': {'code': '1000', 'data': {'row': [{'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}  # Second: is_complete returns True
                ]
                
                # Simulate poll_until_complete behavior - call is_complete until it returns True
                for result in results:
                    if is_complete(result):
                        return result
                # If we get here, return last result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_added_rows_not_list(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_added with rows not list (lines 163-166)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - rows not list, then matching record
        call_count = [0]
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                call_count[0] += 1
                if call_count[0] == 1:
                    # Rows not list
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': {'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}  # Not list
                            }
                        }
                    }
                else:
                    # Matching record
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{
                                    'name': '@',
                                    'rdtype': 'A',
                                    'rdata': '192.0.2.1'
                                }]
                            }
                        }
                    }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_added_row_not_dict(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_added with row not dict (lines 168-173)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - row not dict, then matching record
        call_count = [0]
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                call_count[0] += 1
                if call_count[0] == 1:
                    # Row not dict
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': ['not-a-dict']
                            }
                        }
                    }
                else:
                    # Matching record
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{
                                    'name': '@',
                                    'rdtype': 'A',
                                    'rdata': '192.0.2.1'
                                }]
                            }
                        }
                    }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)


class TestDNSRecordUpdateCheckFunctions(unittest.TestCase):
    """Test check_record_updated function edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_code_not_1000(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with code not 1000 (lines 275-278)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - simulate that is_complete eventually returns True
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Simulate polling: first attempt fails, second succeeds
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # First: code not 1000
                    else:
                        return True  # Second: code 1000 with matching record
                
                results = [
                    {'response': {'code': '1001'}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_rows_not_list(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with rows not list (lines 281-284)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - rows not list, then matching record
        call_count = [0]
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                call_count[0] += 1
                if call_count[0] == 1:
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': {'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}  # Not list
                            }
                        }
                    }
                else:
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{
                                    'ID': '1',
                                    'name': '@',
                                    'rdtype': 'A',
                                    'rdata': '192.0.2.1'
                                }]
                            }
                        }
                    }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_record_not_found(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with record not found (lines 286-296)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - record not found, then found
        call_count = [0]
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                call_count[0] += 1
                if call_count[0] == 1:
                    # Record not found (different ID)
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{
                                    'ID': '2',
                                    'name': '@',
                                    'rdtype': 'A',
                                    'rdata': '192.0.2.1'
                                }]
                            }
                        }
                    }
                else:
                    # Record found with matching values
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{
                                    'ID': '1',
                                    'name': '@',
                                    'rdtype': 'A',
                                    'rdata': '192.0.2.1'
                                }]
                            }
                        }
                    }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_name_mismatch(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with name mismatch (lines 288-290)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - name mismatch, then match
        call_count = [0]
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                call_count[0] += 1
                if call_count[0] == 1:
                    # Name mismatch
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{
                                    'ID': '1',
                                    'name': 'www',  # Different name
                                    'rdtype': 'A',
                                    'rdata': '192.0.2.1'
                                }]
                            }
                        }
                    }
                else:
                    # Name matches
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{
                                    'ID': '1',
                                    'name': '@',
                                    'rdtype': 'A',
                                    'rdata': '192.0.2.1'
                                }]
                            }
                        }
                    }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)


class TestDNSRecordDeleteCheckFunctions(unittest.TestCase):
    """Test check_record_deleted function edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_deleted_code_not_1000(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_deleted with code not 1000 (lines 376-379)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - simulate that is_complete eventually returns True (record deleted)
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                # Simulate polling: first attempt fails, second succeeds
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # First: code not 1000
                    else:
                        return True  # Second: record deleted
                
                results = [
                    {'response': {'code': '1001'}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_deleted_rows_not_list(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_deleted with rows not list (lines 382-385)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - rows not list, then record deleted
        call_count = [0]
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                call_count[0] += 1
                if call_count[0] == 1:
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': {'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}  # Not list
                            }
                        }
                    }
                else:
                    # Record deleted
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]
                            }
                        }
                    }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_deleted_record_still_exists(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_deleted with record still exists (lines 387-391)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - record still exists, then deleted
        call_count = [0]
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                call_count[0] += 1
                if call_count[0] == 1:
                    # Record still exists
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{
                                    'ID': '1',
                                    'name': '@',
                                    'rdtype': 'A',
                                    'rdata': '192.0.2.1'
                                }]
                            }
                        }
                    }
                else:
                    # Record deleted
                    return {
                        'response': {
                            'code': '1000',
                            'data': {
                                'row': [{'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]
                            }
                        }
                    }
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_added_empty_rows(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_added with empty rows (line 174)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - empty rows, then matching record
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Empty rows
                    else:
                        return True  # Matching record
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': []}}},  # Empty rows
                    {'response': {'code': '1000', 'data': {'row': [{'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_type_mismatch(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with type mismatch (lines 290-292)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - type mismatch, then match
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Type mismatch
                    else:
                        return True  # Type matches
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'AAAA', 'rdata': '192.0.2.1'}]}}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_value_mismatch(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with value mismatch (lines 293-294)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - value mismatch, then match
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Value mismatch
                    else:
                        return True  # Value matches
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.2'}]}}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_record_not_found_return_false(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with record not found (line 296)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - record not found, then found
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Record not found (line 296)
                    else:
                        return True  # Record found
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_async_warning_not_timeout(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update with async warning not timeout (lines 325-331)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling returns warning (not timeout)
        self.mock_client.poll_until_complete.return_value = {
            'response': {
                'code': '1001',
                'result': 'Still processing'
            }
        }
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        # Should return success despite warning
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_deleted_row_not_dict(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_deleted with row not dict (lines 388-390)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - row not dict, then record deleted
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Row not dict
                    else:
                        return True  # Record deleted
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': ['not-a-dict']}}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_async_without_wait(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update with async without wait (lines 324-326)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = False
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)
        self.mock_client.poll_until_complete.assert_not_called()

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_dns_record_update_error_response(self, mock_validate, mock_get_logger, mock_format):
        """Test cmd_dns_record_update with error response (lines 327-331)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.format = 'table'
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '2100',
                'result': 'Error occurred'
            }
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_dns_record_update(self.mock_args, self.mock_client)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_added_no_matching_record(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_added with no matching record (line 174)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - no matching record, then matching record
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # No matching record (line 174)
                    else:
                        return True  # Matching record
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': [{'name': 'www', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}},
                    {'response': {'code': '1000', 'data': {'row': [{'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_row_not_dict(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with row not dict (line 284)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - row not dict, then matching record
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Row not dict (line 284)
                    else:
                        return True  # Matching record
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': ['not-a-dict']}}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_deleted_record_still_exists_return_false(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_deleted with record still exists (line 390)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - record still exists, then deleted
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Record still exists (line 390)
                    else:
                        return True  # Record deleted
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_added_rows_not_list_conversion(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_added with rows not list conversion (line 166)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.ttl = 3600
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - rows not list (single dict), then matching record
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Rows not list (single dict) - covers line 166
                    else:
                        return True  # Matching record
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': {'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}}}},  # Not list
                    {'response': {'code': '1000', 'data': {'row': [{'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_add(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_rows_not_list_conversion(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with rows not list conversion (line 284)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - rows not list (single dict), then matching record
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Rows not list - covers line 284
                    else:
                        return True  # Matching record
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': {'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}}}},  # Not list
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_updated_name_check_false(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_updated with name check returning False (line 290)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.name = '@'
        self.mock_args.type = 'A'
        self.mock_args.value = '192.0.2.1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - name mismatch (returns False on line 290), then match
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Name mismatch - covers line 290
                    else:
                        return True  # Name matches
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': 'www', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}},
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '1', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_update(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)

    @patch('wapi.commands.dns.format_output')
    @patch('wapi.commands.dns.get_logger')
    @patch('wapi.commands.dns.validate_domain')
    def test_check_record_deleted_rows_not_list_conversion(self, mock_validate, mock_get_logger, mock_format):
        """Test check_record_deleted with rows not list conversion (line 385)"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_validate.return_value = (True, None)
        
        self.mock_args.domain = 'example.com'
        self.mock_args.id = '1'
        self.mock_args.record_id = '1'
        self.mock_args.wait = True
        self.mock_args.format = 'table'
        self.mock_args.quiet = False
        
        self.mock_client.call.return_value = {
            'response': {
                'code': '1001',
                'data': {'result': 'async'}
            }
        }
        
        # Polling - rows not list (single dict), then record deleted
        def mock_poll(*args, **kwargs):
            is_complete = kwargs.get('is_complete')
            if is_complete:
                attempt = [0]
                def check_func(result):
                    attempt[0] += 1
                    if attempt[0] == 1:
                        return False  # Rows not list - covers line 385
                    else:
                        return True  # Record deleted
                
                results = [
                    {'response': {'code': '1000', 'data': {'row': {'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}}}},  # Not list
                    {'response': {'code': '1000', 'data': {'row': [{'ID': '2', 'name': '@', 'rdtype': 'A', 'rdata': '192.0.2.1'}]}}}
                ]
                
                for result in results:
                    if is_complete(result):
                        return result
                return results[-1]
            return {'response': {'code': '1000'}}
        
        self.mock_client.poll_until_complete.side_effect = mock_poll
        
        result = cmd_dns_record_delete(self.mock_args, self.mock_client)
        
        self.assertEqual(result, EXIT_SUCCESS)


if __name__ == '__main__':
    unittest.main()
