"""
Comprehensive tests for wapi/commands/dns.py
"""
import pytest
from unittest.mock import MagicMock, patch
from argparse import Namespace
from wapi.commands.dns import (
    cmd_dns_list, cmd_dns_record_list, cmd_dns_record_add,
    cmd_dns_record_update, cmd_dns_record_delete
)
from wapi.exceptions import WAPIValidationError, WAPIRequestError

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.call.return_value = {"response": {"code": "1000", "result": "OK"}}
    return client

@pytest.fixture
def base_args():
    return Namespace(format='table', verbose=False, quiet=False)

class TestDNSList:
    def test_success(self, mock_client, base_args, capsys):
        args = base_args
        args.domain = "example.com"
        mock_client.domain_info.return_value = {
            "response": {
                "code": "1000",
                "data": {"domain": {"dns": {"server": [{"name": "ns1", "addr_ipv4": "1.1.1.1"}]}}}
            }
        }
        
        cmd_dns_list(args, mock_client)
        captured = capsys.readouterr()
        assert "ns1" in captured.out
        assert "1.1.1.1" in captured.out

    def test_no_dns_info(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        mock_client.domain_info.return_value = {
            "response": {
                "code": "1000",
                "data": {"domain": {}} # Missing dns
            }
        }
        with pytest.raises(WAPIRequestError):
            cmd_dns_list(args, mock_client)

class TestDNSRecordList:
    def test_success(self, mock_client, base_args, capsys):
        args = base_args
        args.domain = "example.com"
        mock_client.call.return_value = {
            "response": {
                "code": "1000",
                "data": {"row": [{"ID": "1", "name": "www", "rdtype": "A", "rdata": "1.2.3.4"}]}
            }
        }
        cmd_dns_record_list(args, mock_client)
        captured = capsys.readouterr()
        assert "www" in captured.out
        assert "1.2.3.4" in captured.out

class TestDNSRecordAdd:
    def test_success(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        args.name = "www"
        args.type = "A"
        args.value = "1.2.3.4"
        args.ttl = 3600
        args.wait = False
        
        cmd_dns_record_add(args, mock_client)
        mock_client.call.assert_called_with("dns-row-add", {
            "domain": "example.com", "name": "www", "ttl": 3600, "rdtype": "A", "rdata": "1.2.3.4"
        })

    def test_async_wait(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        args.name = "www"
        args.type = "A"
        args.value = "1.2.3.4"
        args.ttl = 3600
        args.wait = True
        
        mock_client.call.return_value = {"response": {"code": "1001"}}
        mock_client.poll_until_complete.return_value = {"response": {"code": "1000"}}
        
        cmd_dns_record_add(args, mock_client)
        mock_client.poll_until_complete.assert_called()

class TestDNSRecordUpdate:
    def test_update_success(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        args.id = "123"
        args.name = "new"
        args.type = None
        args.value = None
        args.ttl = None
        args.wait = False
        
        cmd_dns_record_update(args, mock_client)
        mock_client.call.assert_called_with("dns-row-update", {
            "domain": "example.com", "row_id": "123", "name": "new"
        })

    def test_missing_id(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        args.id = None
        with pytest.raises(WAPIValidationError):
            cmd_dns_record_update(args, mock_client)

    def test_no_updates(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        args.id = "123"
        args.name = None
        args.type = None
        args.value = None
        args.ttl = None
        with pytest.raises(WAPIValidationError):
            cmd_dns_record_update(args, mock_client)

class TestDNSRecordDelete:
    def test_delete_success(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        args.id = "123"
        args.wait = False
        
        cmd_dns_record_delete(args, mock_client)
        mock_client.call.assert_called_with("dns-row-delete", {
            "domain": "example.com", "row_id": "123"
        })

    def test_missing_id(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        args.id = None
        with pytest.raises(WAPIValidationError):
            cmd_dns_record_delete(args, mock_client)
