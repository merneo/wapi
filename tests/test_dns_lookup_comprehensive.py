"""
Comprehensive tests for wapi/utils/dns_lookup.py
"""
import pytest
from unittest.mock import MagicMock, patch, ANY
import socket

from wapi.utils.dns_lookup import (
    get_ipv6_from_ipv4,
    get_ipv6_from_nameserver,
    enhance_nameserver_with_ipv6,
    _timeout_handler
)
from wapi.exceptions import WAPIDNSLookupError

# --- Fixtures and Helpers ---

@pytest.fixture
def mock_socket():
    with patch('wapi.utils.dns_lookup.socket') as mock:
        yield mock

@pytest.fixture
def mock_dns_resolver():
    with patch('dns.resolver.Resolver') as mock:
        yield mock

def setup_dns_available(available=True):
    return patch('wapi.utils.dns_lookup.DNS_PYTHON_AVAILABLE', available)

# --- Tests ---

def test_timeout_handler():
    with pytest.raises(TimeoutError):
        _timeout_handler(None, None)

class TestGetIPv6FromIPv4:
    
    def test_reverse_dns_failure(self, mock_socket):
        mock_socket.gethostbyaddr.side_effect = socket.herror
        with setup_dns_available(True):
            result = get_ipv6_from_ipv4("1.2.3.4")
        assert result is None

    def test_success_dnspython(self, mock_socket, mock_dns_resolver):
        mock_socket.gethostbyaddr.return_value = ("host.example.com", [], [])
        
        resolver_instance = mock_dns_resolver.return_value
        # Ensure str() on the answer element returns the IP
        mock_answer = MagicMock()
        mock_answer.__str__.return_value = "2001:db8::1"
        resolver_instance.resolve.return_value = [mock_answer]
        
        with setup_dns_available(True):
            result = get_ipv6_from_ipv4("1.2.3.4")
            
        assert result == "2001:db8::1"
        resolver_instance.resolve.assert_called_with("host.example.com", 'AAAA')

    def test_invalid_ipv6_dnspython(self, mock_socket, mock_dns_resolver):
        mock_socket.gethostbyaddr.return_value = ("host.example.com", [], [])
        resolver_instance = mock_dns_resolver.return_value
        mock_answer = MagicMock()
        mock_answer.__str__.return_value = "invalid-ipv6"
        resolver_instance.resolve.return_value = [mock_answer]
        
        with setup_dns_available(True):
            result = get_ipv6_from_ipv4("1.2.3.4")
        assert result is None

    def test_no_answer_dnspython(self, mock_socket, mock_dns_resolver):
        import dns.resolver
        mock_socket.gethostbyaddr.return_value = ("host.example.com", [], [])
        resolver_instance = mock_dns_resolver.return_value
        resolver_instance.resolve.side_effect = dns.resolver.NoAnswer
        
        # Ensure fallback also fails
        mock_socket.getaddrinfo.return_value = [] 
        
        with setup_dns_available(True):
            result = get_ipv6_from_ipv4("1.2.3.4")
        assert result is None

    def test_success_socket_fallback(self, mock_socket):
        # Setup no dnspython
        mock_socket.gethostbyaddr.return_value = ("host.example.com", [], [])
        # Mock getaddrinfo response: list of (family, type, proto, canonname, sockaddr)
        # sockaddr for IPv6 is (address, port, flowinfo, scopeid)
        mock_socket.getaddrinfo.return_value = [
            (mock_socket.AF_INET6, mock_socket.SOCK_STREAM, 0, '', ('2001:db8::1', 0, 0, 0))
        ]
        
        with setup_dns_available(False):
            result = get_ipv6_from_ipv4("1.2.3.4")
            
        assert result == "2001:db8::1"
        # Use mock_socket attributes for checking call
        mock_socket.getaddrinfo.assert_called_with("host.example.com", None, mock_socket.AF_INET6, mock_socket.SOCK_STREAM)

    def test_socket_fallback_failure(self, mock_socket):
        mock_socket.gethostbyaddr.return_value = ("host.example.com", [], [])
        mock_socket.getaddrinfo.side_effect = socket.gaierror
        
        with setup_dns_available(False):
            result = get_ipv6_from_ipv4("1.2.3.4")
        assert result is None

    def test_dnspython_timeout_exception(self, mock_socket, mock_dns_resolver):
        import dns.resolver

        mock_socket.gethostbyaddr.return_value = ("host.example.com", [], [])
        mock_socket.getaddrinfo.return_value = []
        mock_dns_resolver.return_value.resolve.side_effect = dns.resolver.Timeout()

        with setup_dns_available(True):
            result = get_ipv6_from_ipv4("1.2.3.4")

        assert result is None

    def test_dnspython_unexpected_exception(self, mock_socket, mock_dns_resolver):
        mock_socket.gethostbyaddr.return_value = ("host.example.com", [], [])
        mock_socket.getaddrinfo.return_value = []
        mock_dns_resolver.return_value.resolve.side_effect = RuntimeError("boom")

        with setup_dns_available(True):
            result = get_ipv6_from_ipv4("1.2.3.4")

        assert result is None


class TestGetIPv6FromNameserver:
    
    def test_direct_aaaa_success(self, mock_dns_resolver):
        resolver_instance = mock_dns_resolver.return_value
        mock_answer = MagicMock()
        mock_answer.__str__.return_value = "2001:db8::1"
        resolver_instance.resolve.return_value = [mock_answer]
        
        with setup_dns_available(True):
            result = get_ipv6_from_nameserver("ns1.example.com", "1.2.3.4")
            
        assert result == "2001:db8::1"
        resolver_instance.resolve.assert_called_with("ns1.example.com", 'AAAA')

    def test_direct_aaaa_fail_fallback_success(self, mock_dns_resolver, mock_socket):
        # First call (direct AAAA) fails
        import dns.resolver
        resolver_instance = mock_dns_resolver.return_value
        
        # resolve is called twice: 
        # 1. direct resolve("ns1.example.com", 'AAAA') -> NoAnswer
        # 2. inside get_ipv6_from_ipv4 -> resolve("other.host.com", 'AAAA') -> Success
        
        mock_answer = MagicMock()
        mock_answer.__str__.return_value = "2001:db8::2"
        
        resolver_instance.resolve.side_effect = [
            dns.resolver.NoAnswer, # Fail direct
            [mock_answer] # Succeed via reverse DNS logic
        ]
        
        # Mock reverse DNS lookup for the fallback path
        mock_socket.gethostbyaddr.return_value = ("other.host.com", [], [])
        # Fallback socket check for direct name also fails
        mock_socket.getaddrinfo.return_value = []

        with setup_dns_available(True):
            result = get_ipv6_from_nameserver("ns1.example.com", "1.2.3.4")
            
        assert result == "2001:db8::2"

    def test_socket_direct_success(self, mock_socket):
        mock_socket.getaddrinfo.return_value = [
            (mock_socket.AF_INET6, mock_socket.SOCK_STREAM, 0, '', ('2001:db8::1', 0, 0, 0))
        ]
        
        with setup_dns_available(False):
            result = get_ipv6_from_nameserver("ns1.example.com", "1.2.3.4")
            
        assert result == "2001:db8::1"

    @patch('wapi.utils.dns_lookup.validate_ipv6', return_value=(False, "Invalid"))
    def test_direct_aaaa_invalid_ipv6(self, mock_validate, mock_dns_resolver, mock_socket):
        mock_answer = MagicMock()
        mock_answer.__str__.return_value = "invalid-ipv6"
        mock_dns_resolver.return_value.resolve.return_value = [mock_answer]
        mock_socket.getaddrinfo.return_value = []

        with setup_dns_available(True):
            result = get_ipv6_from_nameserver("ns1.example.com", "1.2.3.4")

        assert result is None
        mock_validate.assert_called_once()

    @patch('wapi.utils.dns_lookup.get_ipv6_from_ipv4', return_value=None)
    def test_direct_aaaa_timeout_exception(self, mock_get_ipv6, mock_dns_resolver, mock_socket):
        import dns.resolver

        mock_dns_resolver.return_value.resolve.side_effect = dns.resolver.Timeout()
        mock_socket.getaddrinfo.return_value = []

        with setup_dns_available(True):
            result = get_ipv6_from_nameserver("ns1.example.com", "1.2.3.4")

        assert result is None

    @patch('wapi.utils.dns_lookup.get_ipv6_from_ipv4', return_value=None)
    def test_direct_aaaa_unexpected_exception(self, mock_get_ipv6, mock_dns_resolver, mock_socket):
        mock_dns_resolver.return_value.resolve.side_effect = RuntimeError("boom")
        mock_socket.getaddrinfo.return_value = []

        with setup_dns_available(True):
            result = get_ipv6_from_nameserver("ns1.example.com", "1.2.3.4")

        assert result is None


class TestEnhanceNameserver:
    
    def test_already_has_ipv6(self):
        ns = {'name': 'ns1', 'addr_ipv4': '1.1.1.1', 'addr_ipv6': '::1'}
        res, found, warn = enhance_nameserver_with_ipv6(ns)
        assert found is False
        assert warn is None
        assert res == ns

    def test_no_ipv4(self):
        ns = {'name': 'ns1'}
        res, found, warn = enhance_nameserver_with_ipv6(ns)
        assert found is False
        assert warn is None

    def test_found_ipv6(self):
        ns = {'name': 'ns1', 'addr_ipv4': '1.1.1.1'}
        with patch('wapi.utils.dns_lookup.get_ipv6_from_nameserver', return_value="2001:db8::1"):
            res, found, warn = enhance_nameserver_with_ipv6(ns)
        
        assert found is True
        assert res['addr_ipv6'] == "2001:db8::1"
        assert warn is None

    def test_not_found_warning(self):
        ns = {'name': 'ns1', 'addr_ipv4': '1.1.1.1'}
        with patch('wapi.utils.dns_lookup.get_ipv6_from_nameserver', return_value=None):
            res, found, warn = enhance_nameserver_with_ipv6(ns)
        
        assert found is False
        assert "IPv6 address not found" in warn

    def test_exception_warning(self):
        ns = {'name': 'ns1', 'addr_ipv4': '1.1.1.1'}
        with patch('wapi.utils.dns_lookup.get_ipv6_from_nameserver', side_effect=Exception("Boom")):
            res, found, warn = enhance_nameserver_with_ipv6(ns)
        
        assert found is False
        assert "Unexpected error" in warn