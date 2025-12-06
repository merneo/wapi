import socket
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def poll_success():
    """Return a side-effect function for poll_until_complete that yields success code."""
    def _factory(payload=None):
        payload = payload or {"response": {"code": "1000", "data": {}}}
        return payload
    return _factory


@pytest.fixture
def poll_timeout():
    """Return a side-effect function for poll_until_complete that yields timeout code."""
    def _factory(message="Timeout"):
        return {"response": {"code": "9998", "result": message}}
    return _factory


@pytest.fixture
def poll_warning():
    """Return a side-effect function for poll_until_complete that yields non-timeout warning."""
    def _factory(message="Still processing"):
        return {"response": {"code": "1001", "result": message}}
    return _factory


@pytest.fixture
def mock_whois_socket(monkeypatch):
    """
    Provide a MagicMock socket with configurable send/recv behavior.
    Usage:
        sock = mock_whois_socket
        sock.recv.side_effect = [...]
    """
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b""
    mock_socket_cls = MagicMock(return_value=mock_sock)
    monkeypatch.setattr("wapi.commands.search.socket.socket", mock_socket_cls, raising=True)
    return mock_sock


@pytest.fixture
def mock_dns_socket(monkeypatch):
    """
    Provide a MagicMock socket module for dns_lookup helpers.
    """
    mock_socket_module = MagicMock()
    # Ensure socket() returns a mock instance (not heavily used in tests today)
    mock_socket_instance = MagicMock()
    mock_socket_instance.recv.return_value = b""
    mock_socket_module.socket.return_value = mock_socket_instance

    # Expose constants used by the code under test
    mock_socket_module.AF_INET6 = socket.AF_INET6
    mock_socket_module.SOCK_STREAM = socket.SOCK_STREAM
    mock_socket_module.herror = socket.herror
    mock_socket_module.gaierror = socket.gaierror
    mock_socket_module.timeout = socket.timeout

    # Common DNS helpers patched for tests to control behavior
    mock_socket_module.gethostbyaddr = MagicMock()
    mock_socket_module.getaddrinfo = MagicMock()
    mock_socket_module.setdefaulttimeout = MagicMock()

    monkeypatch.setattr("wapi.utils.dns_lookup.socket", mock_socket_module, raising=True)
    return mock_socket_module
