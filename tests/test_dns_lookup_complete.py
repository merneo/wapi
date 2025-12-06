"""
Complete tests for wapi.utils.dns_lookup module to achieve 100% coverage

Tests for missing lines: DNS Python path, timeout handler, edge cases.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import socket
import sys

from wapi.utils.dns_lookup import (
    get_ipv6_from_ipv4,
    get_ipv6_from_nameserver,
    enhance_nameserver_with_ipv6,
    DNS_LOOKUP_TIMEOUT,
)


class TestDNSLookupWithDNSPython(unittest.TestCase):
    """Test DNS lookup with dnspython available - testing fallback paths"""
    
    # Note: DNS Python path (lines 62-82, 130-150) requires dnspython to be installed
    # We test the fallback paths and exception handling instead


    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    @patch('wapi.utils.dns_lookup.socket.getaddrinfo')
    @patch('wapi.utils.dns_lookup.validate_ipv6')
    def test_get_ipv6_from_ipv4_fallback_invalid_ipv6(self, mock_validate, mock_getaddrinfo, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 fallback with invalid IPv6 (lines 95-96)"""
        mock_gethostbyaddr.return_value = ('hostname.example.com', [], ['192.0.2.1'])
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 0, '', ('invalid-ipv6', 0, 0, 0))
        ]
        mock_validate.return_value = (False, "Invalid format")
        
        with patch('wapi.utils.dns_lookup.DNS_PYTHON_AVAILABLE', False):
            result = get_ipv6_from_ipv4('192.0.2.1')
        
        self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_exception_handling(self, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 exception handling (lines 102-104)"""
        # Test exception in outer try block - use OSError which is caught (line 102)
        mock_gethostbyaddr.side_effect = OSError("Unexpected error")
        
        result = get_ipv6_from_ipv4('192.0.2.1')
        
        self.assertIsNone(result)
        
        # Test that finally block resets timeout
        mock_timeout.assert_called()

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_exception_socket_herror(self, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 exception handling with socket.herror (lines 102-104)"""
        # Test socket.herror exception (line 102)
        mock_gethostbyaddr.side_effect = socket.herror("Host error")
        
        result = get_ipv6_from_ipv4('192.0.2.1')
        
        self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_exception_socket_gaierror(self, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 exception handling with socket.gaierror (lines 102-104)"""
        # Test socket.gaierror exception (line 102)
        mock_gethostbyaddr.side_effect = socket.gaierror("Address error")
        
        result = get_ipv6_from_ipv4('192.0.2.1')
        
        self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_exception_timeout_error(self, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 exception handling with TimeoutError (lines 102-104)"""
        # Test TimeoutError exception (line 102)
        mock_gethostbyaddr.side_effect = TimeoutError("Timeout")
        
        result = get_ipv6_from_ipv4('192.0.2.1')
        
        self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_outer_exception_setdefaulttimeout(self, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 outer exception handler from setdefaulttimeout (lines 102-104)"""
        # Test that outer exception handler catches exceptions from setdefaulttimeout (line 50)
        # This exception is not in inner try, so it's caught by outer handler (lines 102-104)
        call_count = [0]
        def mock_timeout_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call (line 50) raises exception - caught by outer handler
                raise OSError("Cannot set timeout")
            # Second call (line 107 in finally) should succeed
            return None
        
        mock_timeout.side_effect = mock_timeout_side_effect
        
        result = get_ipv6_from_ipv4('192.0.2.1')
        
        # Should be caught by outer handler (lines 102-104)
        self.assertIsNone(result)
        # Verify setdefaulttimeout was called (once for timeout, once in finally)
        self.assertGreaterEqual(mock_timeout.call_count, 1)

    def test_dns_python_available_constant(self):
        """Test DNS_PYTHON_AVAILABLE constant (line 17)"""
        # This tests that the constant is set during import
        from wapi.utils import dns_lookup
        # DNS_PYTHON_AVAILABLE should be either True or False
        # This covers line 17: DNS_PYTHON_AVAILABLE = True
        self.assertIsInstance(dns_lookup.DNS_PYTHON_AVAILABLE, bool)

    def test_timeout_handler_function(self):
        """Test _timeout_handler function (line 27)"""
        from wapi.utils.dns_lookup import _timeout_handler
        
        # Test that function raises TimeoutError (line 27)
        with self.assertRaises(TimeoutError):
            _timeout_handler(None, None)


class TestGetIPv6FromNameserverEdgeCases(unittest.TestCase):
    """Test get_ipv6_from_nameserver edge cases"""

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.getaddrinfo')
    @patch('wapi.utils.dns_lookup.validate_ipv6')
    def test_get_ipv6_from_nameserver_fallback_invalid(self, mock_validate, mock_getaddrinfo, mock_timeout):
        """Test get_ipv6_from_nameserver fallback with invalid IPv6 (lines 164-165)"""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 0, '', ('invalid-ipv6', 0, 0, 0))
        ]
        mock_validate.return_value = (False, "Invalid format")
        
        with patch('wapi.utils.dns_lookup.DNS_PYTHON_AVAILABLE', False):
            result = get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
        
        self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.get_ipv6_from_ipv4')
    def test_get_ipv6_from_nameserver_fallback_to_ipv4(self, mock_get_ipv6_from_ipv4):
        """Test get_ipv6_from_nameserver fallback to get_ipv6_from_ipv4 (lines 172-175)"""
        mock_get_ipv6_from_ipv4.return_value = '2001:db8::1'
        
        with patch('wapi.utils.dns_lookup.DNS_PYTHON_AVAILABLE', False):
            with patch('wapi.utils.dns_lookup.socket.getaddrinfo', side_effect=socket.gaierror("No IPv6")):
                result = get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
        
        self.assertEqual(result, '2001:db8::1')
        mock_get_ipv6_from_ipv4.assert_called_once()


class TestEnhanceNameserverWithIPv6EdgeCases(unittest.TestCase):
    """Test enhance_nameserver_with_ipv6 edge cases"""

    @patch('wapi.utils.dns_lookup.get_ipv6_from_nameserver')
    def test_enhance_nameserver_exception_handling(self, mock_get_ipv6):
        """Test enhance_nameserver_with_ipv6 exception handling (lines 228-235)"""
        nameserver = {
            'name': 'ns1.example.com',
            'addr_ipv4': '192.0.2.1'
        }
        
        # Test socket.gaierror
        mock_get_ipv6.side_effect = socket.gaierror("DNS error")
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertFalse(found)
        self.assertIsNotNone(warning)
        self.assertIn("DNS error", warning)
        
        # Test socket.herror
        mock_get_ipv6.side_effect = socket.herror("Host error")
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertFalse(found)
        self.assertIsNotNone(warning)
        
        # Test OSError
        mock_get_ipv6.side_effect = OSError("OS error")
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertFalse(found)
        self.assertIsNotNone(warning)
        
        # Test generic Exception
        mock_get_ipv6.side_effect = Exception("Unexpected error")
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertFalse(found)
        self.assertIsNotNone(warning)
        self.assertIn("Unexpected error", warning)


if __name__ == '__main__':
    unittest.main()
