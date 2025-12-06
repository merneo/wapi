"""
Unit tests for wapi.utils.dns_lookup module

Tests for DNS lookup functionality, IPv6 discovery, and error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import socket

from wapi.utils.dns_lookup import (
    get_ipv6_from_ipv4,
    get_ipv6_from_nameserver,
    enhance_nameserver_with_ipv6,
    DNS_LOOKUP_TIMEOUT,
)
from wapi.exceptions import WAPIDNSLookupError


class TestDNSLookupConstants(unittest.TestCase):
    """Test DNS lookup constants"""

    def test_dns_lookup_timeout(self):
        """Test that DNS lookup timeout is defined"""
        self.assertIsInstance(DNS_LOOKUP_TIMEOUT, int)
        self.assertGreater(DNS_LOOKUP_TIMEOUT, 0)
        self.assertLessEqual(DNS_LOOKUP_TIMEOUT, 10)  # Should be reasonable


class TestGetIPv6FromIPv4(unittest.TestCase):
    """Test get_ipv6_from_ipv4 function"""

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    @patch('wapi.utils.dns_lookup.socket.getaddrinfo')
    def test_get_ipv6_from_ipv4_success(self, mock_getaddrinfo, mock_gethostbyaddr, mock_timeout):
        """Test successful IPv6 lookup from IPv4"""
        mock_gethostbyaddr.return_value = ('hostname.example.com', [], ['192.0.2.1'])
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 0, '', ('2001:db8::1', 0, 0, 0))
        ]
        
        result = get_ipv6_from_ipv4('192.0.2.1')
        
        self.assertIsNotNone(result)
        self.assertEqual(result, '2001:db8::1')

    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_no_reverse_dns(self, mock_gethostbyaddr):
        """Test IPv6 lookup when reverse DNS fails"""
        mock_gethostbyaddr.side_effect = socket.herror("Reverse DNS failed")
        
        result = get_ipv6_from_ipv4('192.0.2.1')
        
        self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    @patch('wapi.utils.dns_lookup.socket.getaddrinfo')
    def test_get_ipv6_from_ipv4_no_ipv6(self, mock_getaddrinfo, mock_gethostbyaddr, mock_timeout):
        """Test IPv6 lookup when no IPv6 address found"""
        mock_gethostbyaddr.return_value = ('hostname.example.com', [], ['192.0.2.1'])
        mock_getaddrinfo.side_effect = socket.gaierror("No IPv6 address")
        
        result = get_ipv6_from_ipv4('192.0.2.1')
        
        self.assertIsNone(result)

    def test_get_ipv6_from_ipv4_timeout(self):
        """Test IPv6 lookup with timeout parameter"""
        with patch('wapi.utils.dns_lookup.socket.setdefaulttimeout') as mock_timeout:
            with patch('wapi.utils.dns_lookup.socket.gethostbyaddr', side_effect=socket.gaierror("Timeout")):
                result = get_ipv6_from_ipv4('192.0.2.1', timeout=10)
                self.assertIsNone(result)
                # Verify timeout was set
                mock_timeout.assert_called()


class TestGetIPv6FromNameserver(unittest.TestCase):
    """Test get_ipv6_from_nameserver function"""

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.getaddrinfo')
    def test_get_ipv6_from_nameserver_success(self, mock_getaddrinfo, mock_timeout):
        """Test successful IPv6 lookup for nameserver"""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 0, '', ('2001:db8::1', 0, 0, 0))
        ]
        
        result = get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
        
        self.assertIsNotNone(result)
        self.assertEqual(result, '2001:db8::1')

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.get_ipv6_from_ipv4')
    @patch('wapi.utils.dns_lookup.socket.getaddrinfo')
    def test_get_ipv6_from_nameserver_no_ipv6(self, mock_getaddrinfo, mock_get_ipv6_from_ipv4, mock_timeout):
        """Test IPv6 lookup when nameserver has no IPv6"""
        mock_getaddrinfo.side_effect = socket.gaierror("No IPv6 address")
        mock_get_ipv6_from_ipv4.return_value = None
        
        result = get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
        
        # Should fall back to get_ipv6_from_ipv4
        self.assertIsNone(result)

    def test_get_ipv6_from_nameserver_timeout(self):
        """Test IPv6 lookup with timeout"""
        with patch('wapi.utils.dns_lookup.socket.setdefaulttimeout') as mock_timeout:
            with patch('wapi.utils.dns_lookup.socket.getaddrinfo', side_effect=socket.gaierror("Timeout")):
                result = get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1', timeout=10)
                # Should return None on timeout
                self.assertIsNone(result)


class TestEnhanceNameserverWithIPv6(unittest.TestCase):
    """Test enhance_nameserver_with_ipv6 function"""

    def test_enhance_nameserver_already_has_ipv6(self):
        """Test that nameserver with IPv6 is not modified"""
        nameserver = {
            'name': 'ns1.example.com',
            'addr_ipv4': '192.0.2.1',
            'addr_ipv6': '2001:db8::1'
        }
        
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertEqual(result, nameserver)
        self.assertFalse(found)
        self.assertIsNone(warning)

    def test_enhance_nameserver_no_ipv4(self):
        """Test that nameserver without IPv4 is not modified"""
        nameserver = {
            'name': 'ns1.example.com',
            'addr_ipv4': ''
        }
        
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertEqual(result, nameserver)
        self.assertFalse(found)
        self.assertIsNone(warning)

    @patch('wapi.utils.dns_lookup.get_ipv6_from_nameserver')
    def test_enhance_nameserver_success(self, mock_get_ipv6):
        """Test successful IPv6 enhancement"""
        nameserver = {
            'name': 'ns1.example.com',
            'addr_ipv4': '192.0.2.1'
        }
        mock_get_ipv6.return_value = '2001:db8::1'
        
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertTrue(found)
        self.assertEqual(result['addr_ipv6'], '2001:db8::1')
        self.assertIsNone(warning)

    @patch('wapi.utils.dns_lookup.get_ipv6_from_nameserver')
    def test_enhance_nameserver_not_found(self, mock_get_ipv6):
        """Test IPv6 enhancement when IPv6 is not found"""
        nameserver = {
            'name': 'ns1.example.com',
            'addr_ipv4': '192.0.2.1'
        }
        mock_get_ipv6.return_value = None
        
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertFalse(found)
        self.assertIsNotNone(warning)
        self.assertIn('IPv6 address not found', warning)

    @patch('wapi.utils.dns_lookup.get_ipv6_from_nameserver')
    def test_enhance_nameserver_timeout(self, mock_get_ipv6):
        """Test IPv6 enhancement with timeout"""
        nameserver = {
            'name': 'ns1.example.com',
            'addr_ipv4': '192.0.2.1'
        }
        mock_get_ipv6.side_effect = TimeoutError("DNS lookup timeout")
        
        result, found, warning = enhance_nameserver_with_ipv6(nameserver)
        
        self.assertFalse(found)
        self.assertIsNotNone(warning)
        self.assertIn('timeout', warning.lower())


class TestDNSLookupWithDNSPython(unittest.TestCase):
    """Test DNS lookup with dnspython (if available)"""

    def test_dns_python_availability(self):
        """Test that DNS_PYTHON_AVAILABLE is defined"""
        from wapi.utils.dns_lookup import DNS_PYTHON_AVAILABLE
        self.assertIsInstance(DNS_PYTHON_AVAILABLE, bool)
        
        # The module should handle both cases (with and without dnspython)
        # This is tested indirectly through other tests


if __name__ == '__main__':
    unittest.main()
