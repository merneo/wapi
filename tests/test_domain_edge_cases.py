"""
Edge case tests for domain commands to reach 100% coverage

Tests for remaining uncovered code paths.
"""

import unittest
from unittest.mock import Mock, patch

from wapi.commands.domain import cmd_domain_update_ns
from wapi.constants import EXIT_SUCCESS, API_SUCCESS, API_ASYNC
from wapi.exceptions import WAPITimeoutError


class TestDomainUpdateNSEdgeCases(unittest.TestCase):
    """Test edge cases for domain update-ns"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_args = Mock()

    @patch('wapi.commands.domain.enhance_nameserver_with_ipv6')
    @patch('wapi.commands.domain.validate_domain')
    @patch('wapi.commands.domain.get_logger')
    def test_domain_update_ns_polling_timeout_in_message(self, mock_get_logger, mock_validate, mock_enhance):
        """Test polling with 'timeout' in error message"""
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
        
        # Mock polling response with 'timeout' in message (but not code 9998)
        mock_poll_response = {
            'response': {
                'code': '2000',
                'result': 'Operation timeout occurred'  # Contains 'timeout'
            }
        }
        self.mock_client.poll_until_complete.return_value = mock_poll_response
        
        with self.assertRaises(WAPITimeoutError):
            result = cmd_domain_update_ns(self.mock_args, self.mock_client)


if __name__ == '__main__':
    unittest.main()
