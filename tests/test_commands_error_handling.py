"""
Unit tests for command error handling

Tests that commands properly raise custom exceptions and use constants.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

from wapi.api.client import WedosAPIClient
from wapi.constants import (
    EXIT_SUCCESS,
    EXIT_ERROR,
    EXIT_VALIDATION_ERROR,
)
from wapi.exceptions import (
    WAPIValidationError,
    WAPIRequestError,
    WAPITimeoutError,
)
from wapi.commands.domain import cmd_domain_info, cmd_domain_list
from wapi.commands.dns import cmd_dns_list, cmd_dns_record_list


class TestDomainCommandsErrorHandling(unittest.TestCase):
    """Test domain command error handling"""

    def setUp(self):
        """Set up test client"""
        self.client = Mock(spec=WedosAPIClient)

    def test_domain_info_validation_error(self):
        """Test that invalid domain raises WAPIValidationError"""
        args = Mock()
        args.domain = "invalid..domain"
        args.format = "table"
        
        with self.assertRaises(WAPIValidationError):
            cmd_domain_info(args, self.client)

    def test_domain_info_request_error(self):
        """Test that API errors raise WAPIRequestError"""
        args = Mock()
        args.domain = "example.com"
        args.format = "table"
        
        self.client.domain_info.return_value = {
            "response": {"code": "2001", "result": "Domain not found"}
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_info(args, self.client)

    def test_domain_list_request_error(self):
        """Test that domain list errors raise WAPIRequestError"""
        args = Mock()
        args.format = "table"
        args.tld = None
        args.status = None
        
        self.client.call.return_value = {
            "response": {"code": "2001", "result": "API error"}
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_domain_list(args, self.client)

    def test_domain_list_success(self):
        """Test successful domain list"""
        args = Mock()
        args.format = "table"
        args.tld = None
        args.status = None
        
        self.client.call.return_value = {
            "response": {
                "code": "1000",
                "data": {
                    "domain": [
                        {"name": "example.com", "status": "ok", "expiration": "2025-12-31", "nsset": "NS-EXAMPLE"}
                    ]
                }
            }
        }
        
        with patch('wapi.commands.domain.print'):
            result = cmd_domain_list(args, self.client)
            self.assertEqual(result, EXIT_SUCCESS)


class TestDNSCommandsErrorHandling(unittest.TestCase):
    """Test DNS command error handling"""

    def setUp(self):
        """Set up test client"""
        self.client = Mock(spec=WedosAPIClient)

    def test_dns_list_validation_error(self):
        """Test that invalid domain raises WAPIValidationError"""
        args = Mock()
        args.domain = "invalid..domain"
        args.format = "table"
        
        with self.assertRaises(WAPIValidationError):
            cmd_dns_list(args, self.client)

    def test_dns_list_request_error(self):
        """Test that DNS list errors raise WAPIRequestError"""
        args = Mock()
        args.domain = "example.com"
        args.format = "table"
        
        self.client.domain_info.return_value = {
            "response": {"code": "2001", "result": "Domain not found"}
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_dns_list(args, self.client)

    def test_dns_record_list_validation_error(self):
        """Test that invalid domain raises WAPIValidationError"""
        args = Mock()
        args.domain = "invalid..domain"
        args.format = "table"
        
        with self.assertRaises(WAPIValidationError):
            cmd_dns_record_list(args, self.client)

    def test_dns_record_list_request_error(self):
        """Test that DNS record list errors raise WAPIRequestError"""
        args = Mock()
        args.domain = "example.com"
        args.format = "table"
        
        self.client.call.return_value = {
            "response": {"code": "2001", "result": "API error"}
        }
        
        with self.assertRaises(WAPIRequestError):
            cmd_dns_record_list(args, self.client)


class TestCommandsUseConstants(unittest.TestCase):
    """Test that commands use constants instead of hardcoded values"""

    def test_exit_success_constant_used(self):
        """Test that EXIT_SUCCESS constant is used"""
        from wapi.constants import EXIT_SUCCESS
        self.assertEqual(EXIT_SUCCESS, 0)
        
        # Verify it's imported in commands
        from wapi.commands.domain import EXIT_SUCCESS as domain_exit_success
        self.assertEqual(domain_exit_success, 0)

    def test_exit_error_constant_used(self):
        """Test that EXIT_ERROR constant is used"""
        from wapi.constants import EXIT_ERROR
        self.assertEqual(EXIT_ERROR, 1)


if __name__ == '__main__':
    unittest.main()
