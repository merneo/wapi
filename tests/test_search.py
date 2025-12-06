"""
Tests for the `wapi search` command.
"""

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from wapi.commands.search import (
    _discover_whois_server,
    _query_whois,
    cmd_search,
    infer_availability_from_whois,
    interpret_api_availability,
    interpret_status_value,
    perform_whois_lookup,
)
from wapi.api.client import WedosAPIClient
from wapi.constants import EXIT_SUCCESS
from wapi.exceptions import WAPIRequestError, WAPIValidationError
from wapi import cli


class TestSearchHelpers(unittest.TestCase):
    """Unit tests for helper functions used by the search command."""

    def test_interpret_status_value_handles_strings_and_bools(self):
        self.assertTrue(interpret_status_value("available"))
        self.assertTrue(interpret_status_value("1"))
        self.assertFalse(interpret_status_value("taken"))
        self.assertFalse(interpret_status_value(False))
        self.assertIsNone(interpret_status_value("unknown"))

    def test_interpret_api_availability_parses_domain_entries(self):
        api_response = {
            "response": {
                "code": "1000",
                "data": {
                    "domain": {"name": "example.com", "status": "available"},
                },
            }
        }
        self.assertTrue(interpret_api_availability(api_response, "example.com"))

        api_response["response"]["data"]["domain"]["status"] = "registered"
        self.assertFalse(interpret_api_availability(api_response, "example.com"))

        # Fallback to top-level flag
        api_response["response"]["data"] = {"available": True}
        self.assertTrue(interpret_api_availability(api_response, "example.com"))

    def test_infer_availability_from_whois_patterns(self):
        available_text = "No match for domain example.com"
        registered_text = "Domain Name: EXAMPLE.COM\nRegistrar: Example Registrar"
        # CZ.NIC format
        cz_registered_text = "domain: example.cz\nregistrar: REG-EXAMPLE\nregistered: 01.01.2000"

        self.assertTrue(infer_availability_from_whois(available_text))
        self.assertFalse(infer_availability_from_whois(registered_text))
        self.assertFalse(infer_availability_from_whois(cz_registered_text))
        self.assertIsNone(infer_availability_from_whois("nondescriptive output"))


class TestCmdSearch(unittest.TestCase):
    """End-to-end tests for the search command with mocks to avoid network calls."""

    def setUp(self):
        self.client = WedosAPIClient("user@example.com", "password")

    @patch("wapi.commands.search.perform_whois_lookup")
    @patch.object(WedosAPIClient, "domain_availability")
    def test_cmd_search_available_skips_whois(self, mock_availability, mock_whois_lookup):
        mock_availability.return_value = {
            "response": {
                "code": "1000",
                "data": {"domain": {"name": "example.com", "status": "available"}},
            }
        }
        args = SimpleNamespace(
            domain="example.com", format="json", whois_server=None, whois_timeout=5
        )

        with patch("builtins.print") as mock_print:
            exit_code = cmd_search(args, self.client)

        self.assertEqual(exit_code, EXIT_SUCCESS)
        mock_whois_lookup.assert_not_called()
        self.assertTrue(mock_print.called)

    @patch("wapi.commands.search.perform_whois_lookup")
    @patch.object(WedosAPIClient, "domain_availability")
    def test_cmd_search_registered_fetches_whois(self, mock_availability, mock_whois_lookup):
        mock_availability.return_value = {
            "response": {
                "code": "1000",
                "data": {"domain": {"name": "example.com", "status": "registered"}},
            }
        }
        mock_whois_lookup.return_value = "Domain Name: EXAMPLE.COM\nRegistrar: Example"

        args = SimpleNamespace(
            domain="example.com", format="json", whois_server=None, whois_timeout=5
        )

        with patch("builtins.print") as mock_print:
            exit_code = cmd_search(args, self.client)

        self.assertEqual(exit_code, EXIT_SUCCESS)
        mock_whois_lookup.assert_called_once()
        # Ensure WHOIS text is present in formatted output
        printed_value = mock_print.call_args[0][0]
        self.assertIn("Registrar", printed_value)

    @patch("wapi.commands.search.perform_whois_lookup")
    @patch.object(WedosAPIClient, "domain_availability")
    def test_cmd_search_falls_back_to_whois_for_availability(self, mock_availability, mock_whois_lookup):
        # API result is inconclusive
        mock_availability.return_value = {"response": {"code": "2001", "result": "error"}}
        mock_whois_lookup.return_value = "No match for domain example.net"

        args = SimpleNamespace(
            domain="example.net", format="json", whois_server=None, whois_timeout=5
        )

        with patch("builtins.print") as mock_print:
            exit_code = cmd_search(args, self.client)

        self.assertEqual(exit_code, EXIT_SUCCESS)
        mock_whois_lookup.assert_called_once()
        printed_value = mock_print.call_args[0][0]
        self.assertIn("true", printed_value.lower())


class TestCliSearchAlias(unittest.TestCase):
    """Verify the top-level -s/--search alias routes correctly."""

    def test_top_level_search_alias_invokes_search(self):
        mock_client = MagicMock()
        mock_client.domain_availability.return_value = {
            "response": {
                "code": "1000",
                "data": {"domain": {"name": "example.com", "status": "available"}},
            }
        }

        with patch.object(sys, "argv", ["wapi", "-s", "example.com", "--format", "json"]), \
             patch("wapi.cli.get_client", return_value=mock_client), \
             patch("wapi.commands.search.perform_whois_lookup") as mock_whois:
            exit_code = cli.main()

        self.assertEqual(exit_code, EXIT_SUCCESS)
        mock_client.domain_availability.assert_called_once_with("example.com")
        mock_whois.assert_not_called()


class TestWhoisNetworking(unittest.TestCase):
    """Low-level WHOIS socket and discovery helpers."""

    def test_query_whois_reads_socket_and_closes(self):
        class FakeSocket:
            def __init__(self):
                self.closed = False
                self.sent = []
                self.timeout = None
                self.recv_calls = 0

            def settimeout(self, timeout):
                self.timeout = timeout

            def connect(self, addr):
                self.addr = addr

            def sendall(self, data):
                self.sent.append(data)

            def recv(self, _):
                self.recv_calls += 1
                return b"response chunk" if self.recv_calls == 1 else b""

            def close(self):
                self.closed = True

        fake_socket = FakeSocket()
        with patch("wapi.commands.search.socket.socket", return_value=fake_socket):
            output = _query_whois("whois.example", "example.com", 3)

        self.assertEqual(output, "response chunk")
        self.assertTrue(fake_socket.closed)
        self.assertEqual(fake_socket.timeout, 3)
        self.assertIn(b"example.com", b"".join(fake_socket.sent))

    def test_discover_whois_server_parses_iana_output(self):
        with patch("wapi.commands.search._query_whois", return_value="whois: whois.nic.cz\n"):
            server = _discover_whois_server("example.cz", timeout=2)
        self.assertEqual(server, "whois.nic.cz")


class TestPerformWhoisLookup(unittest.TestCase):
    """perform_whois_lookup selection and error handling."""

    def test_uses_default_server_for_known_tld(self):
        with patch("wapi.commands.search._query_whois", return_value="OK") as mock_query:
            output = perform_whois_lookup("example.com", timeout=4)

        self.assertEqual(output, "OK")
        mock_query.assert_called_once()
        called_server = mock_query.call_args[0][0]
        self.assertEqual(called_server, "whois.verisign-grs.com")

    def test_discovers_server_for_unknown_tld(self):
        with patch("wapi.commands.search._discover_whois_server", return_value="whois.custom.dev") as mock_discover, \
             patch("wapi.commands.search._query_whois", return_value="RESULT") as mock_query:
            output = perform_whois_lookup("example.dev", timeout=5)

        self.assertEqual(output, "RESULT")
        mock_discover.assert_called_once()
        self.assertEqual(mock_query.call_args[0][0], "whois.custom.dev")

    def test_raises_request_error_on_failure(self):
        with patch("wapi.commands.search._query_whois", side_effect=Exception("boom")):
            with self.assertRaises(WAPIRequestError):
                perform_whois_lookup("example.net", timeout=1)


class TestCmdSearchErrors(unittest.TestCase):
    """Error scenarios for cmd_search."""

    def test_invalid_domain_raises_validation_error(self):
        client = MagicMock(spec=WedosAPIClient)
        args = SimpleNamespace(domain="invalid_domain", format="json", whois_server=None, whois_timeout=5)

        with patch("builtins.print"), self.assertRaises(WAPIValidationError):
            cmd_search(args, client)
        client.domain_availability.assert_not_called()

    def test_both_wapi_and_whois_fail_raise_request_error(self):
        client = MagicMock(spec=WedosAPIClient)
        client.domain_availability.return_value = {"response": {"code": "2000", "result": "Error"}}
        args = SimpleNamespace(domain="example.io", format="json", whois_server=None, whois_timeout=3)

        with patch("wapi.commands.search.perform_whois_lookup", side_effect=WAPIRequestError("fail")), \
             patch("builtins.print"), \
             self.assertRaises(WAPIRequestError):
            cmd_search(args, client)
if __name__ == "__main__":
    unittest.main()
