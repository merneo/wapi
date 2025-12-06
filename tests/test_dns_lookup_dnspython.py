"""
Tests for dns_lookup.py DNS Python paths

These tests require dnspython to be installed or use mocking.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import socket
import sys

from wapi.utils.dns_lookup import (
    get_ipv6_from_ipv4,
    get_ipv6_from_nameserver,
)


class TestDNSLookupDNSPythonPaths(unittest.TestCase):
    """Test DNS Python code paths when dnspython is available"""

    def setUp(self):
        """Set up mock dns module"""
        # Create comprehensive mock dns module
        self.mock_dns = MagicMock()
        self.mock_resolver_module = MagicMock()
        self.mock_resolver = Mock()
        self.mock_resolver_class = Mock(return_value=self.mock_resolver)
        self.mock_resolver_module.Resolver = self.mock_resolver_class
        self.mock_dns.resolver = self.mock_resolver_module
        
        # Create mock exceptions
        class MockTimeout(Exception):
            pass
        class MockNoAnswer(Exception):
            pass
        class MockNXDOMAIN(Exception):
            pass
        class MockNoNameservers(Exception):
            pass
        
        self.mock_resolver_module.Timeout = MockTimeout
        self.mock_resolver_module.NoAnswer = MockNoAnswer
        self.mock_resolver_module.NXDOMAIN = MockNXDOMAIN
        self.mock_resolver_module.NoNameservers = MockNoNameservers

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    @patch('wapi.utils.dns_lookup.validate_ipv6')
    def test_get_ipv6_from_ipv4_dns_python_success(self, mock_validate, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 with dnspython success (lines 62-73)"""
        # Mock dns module in sys.modules before importing
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            # Reload module to pick up mocked dns
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                mock_gethostbyaddr.return_value = ('hostname.example.com', [], ['192.0.2.1'])
                
                mock_answer = Mock()
                mock_answer.__str__ = Mock(return_value='2001:db8::1')
                self.mock_resolver.resolve.return_value = [mock_answer]
                mock_validate.return_value = (True, None)
                
                result = wapi.utils.dns_lookup.get_ipv6_from_ipv4('192.0.2.1')
                
                self.assertEqual(result, '2001:db8::1')
                self.mock_resolver.resolve.assert_called_once_with('hostname.example.com', 'AAAA')

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    @patch('wapi.utils.dns_lookup.validate_ipv6')
    def test_get_ipv6_from_ipv4_dns_python_invalid_ipv6(self, mock_validate, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 with dnspython invalid IPv6 (lines 74-76)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                mock_gethostbyaddr.return_value = ('hostname.example.com', [], ['192.0.2.1'])
                
                mock_answer = Mock()
                mock_answer.__str__ = Mock(return_value='invalid-ipv6')
                self.mock_resolver.resolve.return_value = [mock_answer]
                mock_validate.return_value = (False, "Invalid format")
                
                result = wapi.utils.dns_lookup.get_ipv6_from_ipv4('192.0.2.1')
                
                self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_dns_python_timeout(self, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 with dnspython timeout (lines 77-78)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                mock_gethostbyaddr.return_value = ('hostname.example.com', [], ['192.0.2.1'])
                self.mock_resolver.resolve.side_effect = self.mock_resolver_module.Timeout()
                
                result = wapi.utils.dns_lookup.get_ipv6_from_ipv4('192.0.2.1')
                
                self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_dns_python_no_answer(self, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 with dnspython no answer (lines 79-80)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                mock_gethostbyaddr.return_value = ('hostname.example.com', [], ['192.0.2.1'])
                self.mock_resolver.resolve.side_effect = self.mock_resolver_module.NoAnswer()
                
                result = wapi.utils.dns_lookup.get_ipv6_from_ipv4('192.0.2.1')
                
                self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.socket.setdefaulttimeout')
    @patch('wapi.utils.dns_lookup.socket.gethostbyaddr')
    def test_get_ipv6_from_ipv4_dns_python_exception(self, mock_gethostbyaddr, mock_timeout):
        """Test get_ipv6_from_ipv4 with dnspython exception (lines 81-82)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                mock_gethostbyaddr.return_value = ('hostname.example.com', [], ['192.0.2.1'])
                self.mock_resolver.resolve.side_effect = Exception("Unexpected error")
                
                result = wapi.utils.dns_lookup.get_ipv6_from_ipv4('192.0.2.1')
                
                self.assertIsNone(result)

    @patch('wapi.utils.dns_lookup.validate_ipv6')
    def test_get_ipv6_from_nameserver_dns_python_success(self, mock_validate):
        """Test get_ipv6_from_nameserver with dnspython success (lines 130-141)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                mock_answer = Mock()
                mock_answer.__str__ = Mock(return_value='2001:db8::1')
                self.mock_resolver.resolve.return_value = [mock_answer]
                mock_validate.return_value = (True, None)
                
                result = wapi.utils.dns_lookup.get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
                
                self.assertEqual(result, '2001:db8::1')
                self.mock_resolver.resolve.assert_called_once_with('ns1.example.com', 'AAAA')

    @patch('wapi.utils.dns_lookup.validate_ipv6')
    def test_get_ipv6_from_nameserver_dns_python_invalid(self, mock_validate):
        """Test get_ipv6_from_nameserver with dnspython invalid IPv6 (lines 142-144)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                mock_answer = Mock()
                mock_answer.__str__ = Mock(return_value='invalid-ipv6')
                self.mock_resolver.resolve.return_value = [mock_answer]
                mock_validate.return_value = (False, "Invalid format")
                
                result = wapi.utils.dns_lookup.get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
                
                self.assertIsNone(result)

    def test_get_ipv6_from_nameserver_dns_python_timeout(self):
        """Test get_ipv6_from_nameserver with dnspython timeout (lines 145-146)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                self.mock_resolver.resolve.side_effect = self.mock_resolver_module.Timeout()
                
                result = wapi.utils.dns_lookup.get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
                
                self.assertIsNone(result)

    def test_get_ipv6_from_nameserver_dns_python_no_answer(self):
        """Test get_ipv6_from_nameserver with dnspython no answer (lines 147-148)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                self.mock_resolver.resolve.side_effect = self.mock_resolver_module.NoAnswer()
                
                result = wapi.utils.dns_lookup.get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
                
                self.assertIsNone(result)

    def test_get_ipv6_from_nameserver_dns_python_no_nameservers(self):
        """Test get_ipv6_from_nameserver with dnspython no nameservers (line 147)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                self.mock_resolver.resolve.side_effect = self.mock_resolver_module.NoNameservers()
                
                result = wapi.utils.dns_lookup.get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
                
                self.assertIsNone(result)

    def test_get_ipv6_from_nameserver_dns_python_exception(self):
        """Test get_ipv6_from_nameserver with dnspython exception (lines 149-150)"""
        with patch.dict(sys.modules, {'dns': self.mock_dns, 'dns.resolver': self.mock_resolver_module}):
            import importlib
            import wapi.utils.dns_lookup
            importlib.reload(wapi.utils.dns_lookup)
            
            with patch.object(wapi.utils.dns_lookup, 'DNS_PYTHON_AVAILABLE', True):
                self.mock_resolver.resolve.side_effect = Exception("Unexpected error")
                
                result = wapi.utils.dns_lookup.get_ipv6_from_nameserver('ns1.example.com', '192.0.2.1')
                
                self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
