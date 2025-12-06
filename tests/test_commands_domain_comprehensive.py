"""
Comprehensive tests for wapi/commands/domain.py
"""
import pytest
from unittest.mock import MagicMock, patch
from argparse import Namespace
import sys

from wapi.commands.domain import (
    cmd_domain_list,
    cmd_domain_info,
    cmd_domain_update_ns,
    cmd_domain_create,
    cmd_domain_transfer,
    cmd_domain_renew,
    cmd_domain_delete,
    cmd_domain_update,
    filter_sensitive_domain_data
)
from wapi.exceptions import WAPIValidationError, WAPIRequestError, WAPITimeoutError

@pytest.fixture
def mock_client():
    client = MagicMock()
    # Default successful response
    client.call.return_value = {"response": {"code": "1000", "result": "OK"}}
    client.domain_info.return_value = {"response": {"code": "1000", "data": {"domain": {}}}}
    client.domain_create.return_value = {"response": {"code": "1000"}}
    client.domain_transfer.return_value = {"response": {"code": "1000"}}
    client.domain_renew.return_value = {"response": {"code": "1000"}}
    client.domain_delete.return_value = {"response": {"code": "1000"}}
    client.domain_update.return_value = {"response": {"code": "1000"}}
    client.domain_update_ns.return_value = {"response": {"code": "1000"}}
    return client

@pytest.fixture
def base_args():
    return Namespace(format='table', verbose=False, quiet=False)

class TestFilterSensitiveData:
    def test_filter(self):
        data = {
            "name": "d.com",
            "own_email": "secret@email.com",
            "own_name": "John Doe",
            "public": "value"
        }
        filtered = filter_sensitive_domain_data(data)
        assert filtered['name'] == "d.com"
        assert filtered['public'] == "value"
        assert filtered['own_email'] == "[HIDDEN]"
        assert filtered['own_name'] == "[HIDDEN]"

class TestDomainList:
    def test_success(self, mock_client, base_args, capsys):
        args = base_args
        mock_client.call.return_value = {
            "response": {
                "code": "1000", 
                "data": {"domain": [{"name": "d1.cz", "status": "ok"}, {"name": "d2.com", "status": "exp"}]}
            }
        }
        
        ret = cmd_domain_list(args, mock_client)
        assert ret == 0
        captured = capsys.readouterr()
        assert "d1.cz" in captured.out
        assert "d2.com" in captured.out

    def test_filter_tld(self, mock_client, base_args, capsys):
        args = base_args
        args.tld = "cz"
        mock_client.call.return_value = {
            "response": {
                "code": "1000", 
                "data": {"domain": [{"name": "d1.cz"}, {"name": "d2.com"}]}
            }
        }
        cmd_domain_list(args, mock_client)
        captured = capsys.readouterr()
        assert "d1.cz" in captured.out
        assert "d2.com" not in captured.out

    def test_filter_status(self, mock_client, base_args, capsys):
        args = base_args
        args.status = "ok"
        mock_client.call.return_value = {
            "response": {
                "code": "1000", 
                "data": {"domain": [{"name": "d1.cz", "status": "ok"}, {"name": "d2.com", "status": "fail"}]}
            }
        }
        cmd_domain_list(args, mock_client)
        captured = capsys.readouterr()
        assert "d1.cz" in captured.out
        assert "d2.com" not in captured.out

    def test_failure(self, mock_client, base_args):
        mock_client.call.return_value = {"response": {"code": "2000", "result": "Error"}}
        with pytest.raises(WAPIRequestError):
            cmd_domain_list(base_args, mock_client)

class TestDomainInfo:
    def test_success(self, mock_client, base_args, capsys):
        args = base_args
        args.domain = "example.com"
        mock_client.domain_info.return_value = {
            "response": {"code": "1000", "data": {"domain": {"name": "example.com"}}}
        }
        cmd_domain_info(args, mock_client)
        captured = capsys.readouterr()
        assert "example.com" in captured.out

    def test_invalid_domain(self, mock_client, base_args):
        args = base_args
        args.domain = "-invalid-"
        with pytest.raises(WAPIValidationError):
            cmd_domain_info(args, mock_client)

    def test_failure(self, mock_client, base_args):
        args = base_args
        args.domain = "example.com"
        mock_client.domain_info.return_value = {"response": {"code": "2000", "result": "Fail"}}
        with pytest.raises(WAPIRequestError):
            cmd_domain_info(args, mock_client)

class TestDomainUpdateNS:
    @pytest.fixture
    def ns_args(self, base_args):
        args = base_args
        args.domain = "example.com"
        args.nsset = None
        args.nameserver = None
        args.source_domain = None
        args.wait = False
        args.no_ipv6_discovery = True # Disable for simple tests
        return args

    def test_update_with_nsset(self, mock_client, ns_args):
        ns_args.nsset = "NS-SET"
        cmd_domain_update_ns(ns_args, mock_client)
        mock_client.domain_update_ns.assert_called_with("example.com", nsset_name="NS-SET")

    def test_update_with_nameservers(self, mock_client, ns_args):
        ns_args.nameserver = ["ns1.com:1.1.1.1"]
        cmd_domain_update_ns(ns_args, mock_client)
        expected_ns = [{'name': 'ns1.com', 'addr_ipv4': '1.1.1.1', 'addr_ipv6': ''}]
        mock_client.domain_update_ns.assert_called_with("example.com", nameservers=expected_ns)

    def test_update_with_source_domain(self, mock_client, ns_args):
        ns_args.source_domain = "src.com"
        # Mock source info
        mock_client.domain_info.return_value = {
            "response": {
                "code": "1000",
                "data": {"domain": {"dns": {"server": [{"name": "ns.src.com", "addr_ipv4": "1.2.3.4"}]}}}
            }
        }
        
        cmd_domain_update_ns(ns_args, mock_client)
        
        # Should rename ns.src.com to ns.example.com because TLDs match (com -> com)
        expected_ns = [{'name': 'ns.example.com', 'addr_ipv4': '1.2.3.4', 'addr_ipv6': ''}]
        mock_client.domain_update_ns.assert_called_with("example.com", nameservers=expected_ns)

    def test_update_async_wait(self, mock_client, ns_args):
        ns_args.nsset = "NS-SET"
        ns_args.wait = True
        
        mock_client.domain_update_ns.return_value = {"response": {"code": "1001"}}
        mock_client.poll_until_complete.return_value = {"response": {"code": "1000"}}
        
        cmd_domain_update_ns(ns_args, mock_client)
        
        mock_client.poll_until_complete.assert_called_once()

    def test_update_missing_args(self, mock_client, ns_args):
        with pytest.raises(WAPIValidationError):
            cmd_domain_update_ns(ns_args, mock_client)

    def test_ipv6_discovery(self, mock_client, ns_args):
        ns_args.nameserver = ["ns1.com:1.1.1.1"]
        ns_args.no_ipv6_discovery = False
        
        with patch('wapi.commands.domain.enhance_nameserver_with_ipv6') as mock_enhance:
            mock_enhance.return_value = (
                {'name': 'ns1.com', 'addr_ipv4': '1.1.1.1', 'addr_ipv6': '::1'},
                True,
                None
            )
            cmd_domain_update_ns(ns_args, mock_client)
            
            mock_enhance.assert_called()
            # Check if client called with enhanced data
            args, kwargs = mock_client.domain_update_ns.call_args
            assert kwargs['nameservers'][0]['addr_ipv6'] == '::1'

class TestDomainCreate:
    def test_create_simple(self, mock_client, base_args):
        args = base_args
        args.domain = "new.com"
        args.period = 1
        cmd_domain_create(args, mock_client)
        mock_client.domain_create.assert_called_with(
            "new.com", period=1, owner_c=None, admin_c=None, 
            nsset=None, keyset=None, auth_info=None
        )

    def test_create_async_wait(self, mock_client, base_args):
        args = base_args
        args.domain = "new.com"
        args.period = 1
        args.wait = True
        
        mock_client.domain_create.return_value = {"response": {"code": "1001"}}
        mock_client.poll_until_complete.return_value = {"response": {"code": "1000"}}
        
        cmd_domain_create(args, mock_client)
        mock_client.poll_until_complete.assert_called()

class TestDomainTransfer:
    def test_transfer_success(self, mock_client, base_args):
        args = base_args
        args.domain = "trans.com"
        args.auth_info = "AUTH123"
        args.period = 1
        cmd_domain_transfer(args, mock_client)
        mock_client.domain_transfer.assert_called_with("trans.com", "AUTH123", period=1)

    def test_transfer_missing_auth(self, mock_client, base_args):
        args = base_args
        args.domain = "trans.com"
        # No auth_info attr or None
        args.auth_info = None
        with pytest.raises(WAPIValidationError):
            cmd_domain_transfer(args, mock_client)

class TestDomainDelete:
    def test_delete_force(self, mock_client, base_args):
        args = base_args
        args.domain = "del.com"
        args.force = True
        args.delete_after = None
        
        cmd_domain_delete(args, mock_client)
        mock_client.domain_delete.assert_called_with("del.com", delete_after=None)

    def test_delete_no_force(self, mock_client, base_args):
        args = base_args
        args.domain = "del.com"
        args.force = False
        with pytest.raises(WAPIValidationError):
            cmd_domain_delete(args, mock_client)

class TestDomainUpdate:
    def test_update_params(self, mock_client, base_args):
        args = base_args
        args.domain = "up.com"
        args.owner_c = "NEW"
        args.admin_c = None
        args.tech_c = None
        args.nsset = None
        args.keyset = None
        args.auth_info = None
        args.wait = False
        
        cmd_domain_update(args, mock_client)
        mock_client.domain_update.assert_called_with(
            "up.com", owner_c="NEW", admin_c=None, tech_c=None,
            nsset=None, keyset=None, auth_info=None
        )

    def test_update_no_params(self, mock_client, base_args):
        args = base_args
        args.domain = "up.com"
        args.owner_c = None
        args.admin_c = None
        args.tech_c = None
        args.nsset = None
        args.keyset = None
        args.auth_info = None
        
        with pytest.raises(WAPIValidationError):
            cmd_domain_update(args, mock_client)
