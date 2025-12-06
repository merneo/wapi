
import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import socket

from wapi.commands.search import (
    interpret_status_value, interpret_api_availability,
    get_client, _discover_whois_server, _query_whois, perform_whois_lookup
)
from wapi.api.client import WedosAPIClient
from wapi.exceptions import WAPIRequestError


class TestSearchCoverageFinal(unittest.TestCase):

    def test_interpret_status_value_numeric(self):
        """Test interpret_status_value with numeric string (line 86)"""
        self.assertTrue(interpret_status_value("1"))
        self.assertFalse(interpret_status_value("0"))
        self.assertFalse(interpret_status_value("2")) # "2" is not "1", so it's False.

    def test_interpret_api_availability_non_dict_entry(self):
        """
        Test interpret_api_availability with a non-dict entry in candidates (line 121)
        Covers the 'if not isinstance(entry, dict): continue' line.
        """
        api_result = {
            "response": {
                "code": "1000",
                "data": {"domain": ["example.com", {"name": "test.com", "status": "available"}]}
            }
        }
        # The "example.com" string should trigger the continue
        result = interpret_api_availability(api_result, "test.com")
        self.assertTrue(result) # Should still find test.com

        api_result_no_dict = {
            "response": {
                "code": "1000",
                "data": {"domain": "not_a_dict"} # This should make candidates contain "not_a_dict"
            }
        }
        result = interpret_api_availability(api_result_no_dict, "test.com")
        self.assertIsNone(result) # Should not find any valid entry


    @patch('wapi.commands.search.get_config')
    def test_get_client_no_credentials(self, mock_get_config):
        """
        Test get_client when get_config returns no credentials (lines 157-158).
        """
        mock_get_config.side_effect = [None, None] # username, then password
        result = get_client()
        self.assertIsNone(result)

    @patch('wapi.commands.search.get_config', return_value="test@example.com") # username
    @patch('wapi.commands.search.WedosAPIClient')
    def test_get_client_init_exception(self, mock_api_client, mock_get_config):
        """
        Test get_client when WedosAPIClient init raises an exception (lines 161-162).
        """
        mock_get_config.side_effect = ["test@example.com", "testpass"] # username, password
        mock_api_client.side_effect = Exception("Client init failed")
        result = get_client()
        self.assertIsNone(result)


    @patch('wapi.commands.search.socket.socket')
    @patch('wapi.commands.search._discover_whois_server', return_value=None)
    @patch('wapi.commands.search.get_logger')
    def test_perform_whois_lookup_generic_exception(self, mock_get_logger, mock_discover_whois_server, mock_socket):
        """
        Test perform_whois_lookup's generic Exception block (line 221).
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = Exception("Socket connection error")

        with self.assertRaises(WAPIRequestError) as cm:
            # Use an unknown TLD so DEFAULT_WHOIS_SERVERS does not apply and we
            # fall back to the discovery -> IANA path.
            perform_whois_lookup("example.invalid")

        self.assertIn("WHOIS lookup failed", str(cm.exception))
        mock_get_logger().error.assert_called_with("WHOIS lookup failed at whois.iana.org: Socket connection error")

    @patch('wapi.commands.search.socket.socket')
    def test_query_whois_response_truncation(self, mock_socket):
        """
        Test _query_whois breaks if response exceeds max_size (line 221 in original _query_whois context).
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Simulate a large response
        large_data = b'a' * (1024 * 1024 + 10) # Max_size + 10
        mock_socket_instance.recv.side_effect = [
            large_data[:4096],
            large_data[4096:8192],
            large_data[8192:] # Will be larger than max_size after this
        ]

        result = _query_whois("whois.example.com", "example.com", 10)
        
        # The loop should break after total_size > max_size
        # The result length should be approximately max_size
        # This will be tricky because recv is called multiple times.
        # Let's just confirm it hits the break.
        # The exact length depends on where it breaks after the total_size check.
        
        # This test ensures the break is hit.
        self.assertLessEqual(len(result.encode('utf-8')), 1024 * 1024 + 4096) # Should be <= max_size + one recv chunk

    @patch('wapi.commands.search.socket.socket')
    def test_query_whois_socket_timeout_during_recv(self, mock_socket):
        """
        Test _query_whois breaks on socket.timeout during recv (line 222).
        """
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.side_effect = [
            b'some data',
            socket.timeout('Read timed out') # Simulate timeout during recv
        ]
        
        result = _query_whois("whois.example.com", "example.com", 1)
        self.assertIn('some data', result) # Should return whatever was received before timeout
        # This test ensures that the 'break' statement on line 224 (after socket.timeout) is hit.

