"""
Unit tests for wapi.api.client module

Tests for API client error handling, timeouts, and exception raising.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests

from wapi.api.client import WedosAPIClient
from wapi.exceptions import (
    WAPIConnectionError,
    WAPIRequestError,
    WAPITimeoutError,
)


class TestAPIClientInitialization(unittest.TestCase):
    """Test API client initialization"""

    def test_client_initialization(self):
        """Test that client can be initialized"""
        client = WedosAPIClient("user@example.com", "password")
        self.assertEqual(client.username, "user@example.com")
        self.assertEqual(client.password, "password")
        self.assertFalse(client.use_json)
        self.assertIn("xml", client.base_url)

    def test_client_initialization_json(self):
        """Test that client can be initialized with JSON format"""
        client = WedosAPIClient("user@example.com", "password", use_json=True)
        self.assertTrue(client.use_json)
        self.assertIn("json", client.base_url)

    def test_client_initialization_custom_url(self):
        """Test that client can be initialized with custom URL"""
        custom_url = "https://custom.api.wedos.com/wapi"
        client = WedosAPIClient("user@example.com", "password", base_url=custom_url)
        self.assertIn(custom_url, client.base_url)


class TestAPIClientErrorHandling(unittest.TestCase):
    """Test API client error handling"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password")

    @patch('wapi.api.client.requests.post')
    def test_connection_error_raises_wapi_connection_error(self, mock_post):
        """Test that connection errors raise WAPIConnectionError"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with self.assertRaises(WAPIConnectionError) as context:
            self.client.call("ping", {})
        
        self.assertIn("Connection error", str(context.exception))

    @patch('wapi.api.client.requests.post')
    def test_timeout_error_raises_wapi_timeout_error(self, mock_post):
        """Test that timeout errors raise WAPITimeoutError"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with self.assertRaises(WAPITimeoutError) as context:
            self.client.call("ping", {})
        
        self.assertIn("timeout", str(context.exception).lower())

    @patch('wapi.api.client.requests.post')
    def test_request_exception_raises_wapi_request_error(self, mock_post):
        """Test that request exceptions raise WAPIRequestError"""
        mock_post.side_effect = requests.exceptions.RequestException("Request failed")
        
        with self.assertRaises(WAPIRequestError) as context:
            self.client.call("ping", {})
        
        self.assertIn("Request failed", str(context.exception))

    @patch('wapi.api.client.requests.post')
    def test_http_error_raises_wapi_request_error(self, mock_post):
        """Test that HTTP errors raise WAPIRequestError"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_post.return_value = mock_response
        
        with self.assertRaises(WAPIRequestError):
            self.client.call("ping", {})

    @patch('wapi.api.client.requests.post')
    @patch('wapi.api.client.ET.fromstring')
    def test_xml_parse_error_raises_wapi_request_error(self, mock_fromstring, mock_post):
        """Test that XML parse errors raise WAPIRequestError"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<invalid>xml</invalid>"
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Mock ET.fromstring to raise ParseError
        import xml.etree.ElementTree as ET
        mock_fromstring.side_effect = ET.ParseError("XML Parse Error")
        
        with self.assertRaises(WAPIRequestError) as context:
            self.client.call("ping", {})
        
        # Check that exception message contains parse error info
        exception_msg = str(context.exception).lower()
        self.assertIn("parse error", exception_msg)


class TestAPIClientPolling(unittest.TestCase):
    """Test API client polling functionality"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password")

    @patch('wapi.api.client.time.sleep')
    @patch.object(WedosAPIClient, 'call')
    def test_poll_until_complete_success(self, mock_call, mock_sleep):
        """Test successful polling"""
        # First call returns async (1001), second returns success (1000)
        mock_call.side_effect = [
            {"response": {"code": "1001", "result": "Processing"}},
            {"response": {"code": "1000", "result": "OK"}},
        ]
        
        result = self.client.poll_until_complete(
            "domain-info",
            {"name": "example.com"},
            max_attempts=2,
            interval=1
        )
        
        self.assertEqual(result["response"]["code"], "1000")
        self.assertEqual(mock_call.call_count, 2)

    @patch('wapi.api.client.time.sleep')
    @patch.object(WedosAPIClient, 'call')
    def test_poll_until_complete_timeout(self, mock_call, mock_sleep):
        """Test polling timeout"""
        # All calls return async (1001)
        mock_call.return_value = {"response": {"code": "1001", "result": "Processing"}}
        
        with self.assertRaises(WAPITimeoutError) as context:
            self.client.poll_until_complete(
                "domain-info",
                {"name": "example.com"},
                max_attempts=2,
                interval=0.1
            )
        
        self.assertIn("timeout", str(context.exception).lower())
        self.assertEqual(mock_call.call_count, 2)

    @patch('wapi.api.client.time.sleep')
    @patch.object(WedosAPIClient, 'call')
    def test_poll_until_complete_with_custom_check(self, mock_call, mock_sleep):
        """Test polling with custom completion check"""
        def is_complete(result):
            return result.get("response", {}).get("code") == "1000"
        
        mock_call.side_effect = [
            {"response": {"code": "1001", "result": "Processing"}},
            {"response": {"code": "1000", "result": "OK"}},
        ]
        
        result = self.client.poll_until_complete(
            "domain-info",
            {"name": "example.com"},
            is_complete=is_complete,
            max_attempts=2,
            interval=0.1
        )
        
        self.assertEqual(result["response"]["code"], "1000")

    @patch('wapi.api.client.time.sleep')
    @patch.object(WedosAPIClient, 'call')
    def test_poll_until_complete_error_code(self, mock_call, mock_sleep):
        """Test polling stops on error code (2xxx)"""
        mock_call.return_value = {"response": {"code": "2001", "result": "Error"}}
        
        result = self.client.poll_until_complete(
            "domain-info",
            {"name": "example.com"},
            max_attempts=2,
            interval=0.1
        )
        
        self.assertEqual(result["response"]["code"], "2001")
        self.assertEqual(mock_call.call_count, 1)  # Should stop immediately


class TestAPIClientMethods(unittest.TestCase):
    """Test API client methods"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password")

    @patch.object(WedosAPIClient, 'call')
    def test_ping_method(self, mock_call):
        """Test ping method"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.ping()
        
        mock_call.assert_called_once_with("ping", {})
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_info_method(self, mock_call):
        """Test domain_info method"""
        mock_call.return_value = {"response": {"code": "1000", "data": {"domain": {}}}}
        
        result = self.client.domain_info("example.com")
        
        mock_call.assert_called_once_with("domain-info", {"name": "example.com"})
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_create_method(self, mock_call):
        """Test domain_create method"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_create("example.com", period=1)
        
        mock_call.assert_called_once_with("domain-create", {"name": "example.com", "period": 1})
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_create_with_all_params(self, mock_call):
        """Test domain_create method with all parameters"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_create(
            "example.com",
            period=2,
            owner_c="OWNER-C",
            admin_c="ADMIN-C",
            nsset="NSSET-EXAMPLE",
            keyset="KEYSET-EXAMPLE",
            auth_info="AUTH123"
        )
        
        expected_data = {
            "name": "example.com",
            "period": 2,
            "owner_c": "OWNER-C",
            "admin_c": "ADMIN-C",
            "nsset": "NSSET-EXAMPLE",
            "keyset": "KEYSET-EXAMPLE",
            "auth_info": "AUTH123"
        }
        mock_call.assert_called_once_with("domain-create", expected_data)
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_transfer_method(self, mock_call):
        """Test domain_transfer method"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_transfer("example.com", "AUTH123", period=1)
        
        expected_data = {
            "name": "example.com",
            "auth_info": "AUTH123",
            "period": 1
        }
        mock_call.assert_called_once_with("domain-transfer", expected_data)
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_renew_method(self, mock_call):
        """Test domain_renew method"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_renew("example.com", period=1)
        
        mock_call.assert_called_once_with("domain-renew", {"name": "example.com", "period": 1})
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_renew_with_period(self, mock_call):
        """Test domain_renew method with custom period"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_renew("example.com", period=2)
        
        mock_call.assert_called_once_with("domain-renew", {"name": "example.com", "period": 2})
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_delete_method(self, mock_call):
        """Test domain_delete method"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_delete("example.com")
        
        mock_call.assert_called_once_with("domain-delete", {"name": "example.com"})
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_delete_with_date(self, mock_call):
        """Test domain_delete method with delete_after date"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_delete("example.com", delete_after="2025-12-31")
        
        expected_data = {
            "name": "example.com",
            "delete_after": "2025-12-31"
        }
        mock_call.assert_called_once_with("domain-delete", expected_data)
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_update_method(self, mock_call):
        """Test domain_update method"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_update("example.com", owner_c="OWNER-C")
        
        expected_data = {
            "name": "example.com",
            "owner_c": "OWNER-C"
        }
        mock_call.assert_called_once_with("domain-update", expected_data)
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_update_with_all_params(self, mock_call):
        """Test domain_update method with all parameters"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_update(
            "example.com",
            owner_c="OWNER-C",
            admin_c="ADMIN-C",
            tech_c="TECH-C",
            nsset="NSSET-EXAMPLE",
            keyset="KEYSET-EXAMPLE",
            auth_info="AUTH123"
        )
        
        expected_data = {
            "name": "example.com",
            "owner_c": "OWNER-C",
            "admin_c": "ADMIN-C",
            "tech_c": "TECH-C",
            "nsset": "NSSET-EXAMPLE",
            "keyset": "KEYSET-EXAMPLE",
            "auth_info": "AUTH123"
        }
        mock_call.assert_called_once_with("domain-update", expected_data)
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    def test_domain_availability_method(self, mock_call):
        """Test domain_availability method"""
        mock_call.return_value = {"response": {"code": "1000", "data": {"available": True}}}
        
        result = self.client.domain_availability("example.com")
        
        mock_call.assert_called_once_with("domains-availability", {"name": "example.com"})
        self.assertEqual(result["response"]["code"], "1000")


if __name__ == '__main__':
    unittest.main()
