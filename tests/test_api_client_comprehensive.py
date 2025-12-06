"""
Comprehensive tests for wapi/api/client.py
"""
import pytest
import json
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, Mock, patch, ANY
from datetime import datetime

from wapi.api.client import WedosAPIClient
from wapi.exceptions import WAPITimeoutError, WAPIConnectionError, WAPIRequestError
import requests

# --- Fixtures ---

@pytest.fixture
def client():
    return WedosAPIClient("user@test.com", "pass", use_json=True)

@pytest.fixture
def client_xml():
    return WedosAPIClient("user@test.com", "pass", use_json=False)

@pytest.fixture(autouse=True)
def mock_auth():
    with patch('wapi.api.client.calculate_auth', return_value="mock_auth_hash"):
        yield

# --- Tests ---

class TestInitialization:
    def test_init_json(self):
        c = WedosAPIClient("u", "p", use_json=True)
        assert c.base_url.endswith("/json")
        assert c.use_json is True

    def test_init_xml(self):
        c = WedosAPIClient("u", "p", use_json=False)
        assert c.base_url.endswith("/xml")
        assert c.use_json is False

class TestRequestBuilding:
    def test_build_json_request(self, client):
        with patch('wapi.api.client.datetime') as mock_dt:
            mock_dt.now.return_value.timestamp.return_value = 123456
            
            req_str = client._build_json_request("ping", {"foo": "bar"})
            req = json.loads(req_str)
            
            assert req['user'] == "user@test.com"
            assert req['auth'] == "mock_auth_hash"
            assert req['command'] == "ping"
            assert req['clTRID'] == "wapi-123456"
            assert req['data']['foo'] == "bar"

    def test_build_xml_request(self, client_xml):
        with patch('wapi.api.client.datetime') as mock_dt:
            mock_dt.now.return_value.timestamp.return_value = 123456
            
            req_str = client_xml._build_xml_request("ping", {"foo": "bar", "list": [1, 2]})
            
            root = ET.fromstring(req_str)
            assert root.find("user").text == "user@test.com"
            assert root.find("command").text == "ping"
            
            data = root.find("data")
            assert data is not None
            assert data.find("foo").text == "bar"
            # Check list handling
            assert len(data.findall("list")) == 2

class TestCallMethod:
    def test_call_json_success(self, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"code": "1000", "result": "OK"}}
        client.session.post = Mock(return_value=mock_response)
        
        result = client.call("ping")
        
        assert result['response']['code'] == "1000"
        client.session.post.assert_called_once()
        args, kwargs = client.session.post.call_args
        assert "request" in kwargs['data']
        assert "application/x-www-form-urlencoded" in kwargs['headers']['Content-Type']

    def test_call_xml_success(self, client_xml):
        mock_response = MagicMock()
        mock_response.status_code = 200
        xml_resp = """
        <response>
            <code>1000</code>
            <result>OK</result>
        </response>
        """
        mock_response.text = xml_resp
        mock_response.raise_for_status = Mock()
        client_xml.session.post = Mock(return_value=mock_response)
        
        result = client_xml.call("ping")
        
        assert result['response']['code'] == 1000 # XML parser converts digits to int
        assert result['response']['result'] == "OK"

    def test_network_errors(self, client):
        client.session.post = Mock(side_effect=requests.exceptions.ConnectionError("Fail"))
        with pytest.raises(WAPIConnectionError):
            client.call("ping")

        client.session.post = Mock(side_effect=requests.exceptions.Timeout("Time"))
        with pytest.raises(WAPITimeoutError):
            client.call("ping")

        client.session.post = Mock(side_effect=requests.exceptions.RequestException("Generic"))
        with pytest.raises(WAPIRequestError):
            client.call("ping")

class TestHelperMethods:
    def test_domain_methods(self, client):
        with patch.object(client, 'call') as mock_call:
            mock_call.return_value = {}
            
            client.domain_info("d.com")
            mock_call.assert_called_with("domain-info", {"name": "d.com"})
            
            client.domain_availability("d.com")
            mock_call.assert_called_with("domains-availability", {"name": "d.com"})
            
            client.domain_create("d.com", period=2, owner_c="me")
            mock_call.assert_called_with("domain-create", {"name": "d.com", "period": 2, "owner_c": "me"})

            client.domain_renew("d.com", 3)
            mock_call.assert_called_with("domain-renew", {"name": "d.com", "period": 3})
            
            client.domain_transfer("d.com", "auth", 1)
            mock_call.assert_called_with("domain-transfer", {"name": "d.com", "auth_info": "auth", "period": 1})
            
            client.domain_delete("d.com", "2025-01-01")
            mock_call.assert_called_with("domain-delete", {"name": "d.com", "delete_after": "2025-01-01"})
            
            client.domain_update("d.com", owner_c="new")
            mock_call.assert_called_with("domain-update", {"name": "d.com", "owner_c": "new"})

class TestDomainUpdateNSLogic:
    def test_update_ns_existing_set(self, client):
        with patch.object(client, 'call') as mock_call:
            client.domain_update_ns("d.com", nsset_name="NS-SET")
            mock_call.assert_called_with("domain-update-ns", {"name": "d.com", "nsset": "NS-SET"})

    def test_update_ns_create_new(self, client):
        # This involves multiple calls: domain-info -> nsset-create -> domain-update-ns
        with patch.object(client, 'call') as mock_call:
            # Setup responses
            def side_effect(cmd, data=None):
                if cmd == "domain-info":
                    return {"response": {"code": "1000", "data": {"domain": {"owner_c": "TECH1"}}}}
                if cmd == "nsset-create":
                    return {"response": {"code": "1000", "data": {"nsset": "NEW-NS-SET"}}}
                if cmd == "domain-update-ns":
                    return {"response": {"code": "1000"}}
                return {}
            
            mock_call.side_effect = side_effect
            
            nameservers = [{"name": "ns1", "addr_ipv4": "1.1.1.1"}]
            client.domain_update_ns("d.com", nameservers=nameservers)
            
            # Verify flow
            assert mock_call.call_count == 3
            # Check nsset-create call data
            create_call = mock_call.call_args_list[1]
            assert create_call[0][0] == "nsset-create"
            assert create_call[0][1]['tech_c'] == "TECH1"
            assert create_call[0][1]['dns']['server'] == nameservers

    def test_update_ns_create_fail(self, client):
        with patch.object(client, 'call') as mock_call:
            mock_call.return_value = {"response": {"code": "2000", "result": "Fail"}}
            
            res = client.domain_update_ns("d.com", nameservers=[{}])
            
            # Should return the failure response from first/second call and not proceed to update-ns
            assert res['response']['code'] == "2000"
            # domain-update-ns should NOT be called if nsset-create fails (or domain-info)
            # Actually if domain-info fails, tech_c is None, so it proceeds to create without tech_c
            # If nsset-create fails, it returns result immediately

    def test_update_ns_invalid_args(self, client):
        res = client.domain_update_ns("d.com")
        assert res['response']['code'] == "2100"
        assert "must be provided" in res['response']['result']

class TestPolling:
    def test_poll_success_immediate(self, client):
        with patch.object(client, 'call') as mock_call:
            mock_call.return_value = {"response": {"code": "1000"}}
            
            res = client.poll_until_complete("cmd", {}, max_attempts=1)
            assert res['response']['code'] == "1000"

    def test_poll_success_eventually(self, client):
        with patch.object(client, 'call') as mock_call:
            # Pending then Success
            mock_call.side_effect = [
                {"response": {"code": "1001"}}, # Temp error/pending
                {"response": {"code": "1000"}}
            ]
            
            # Use custom is_complete to accept 1000
            res = client.poll_until_complete("cmd", {}, max_attempts=2, interval=0)
            assert res['response']['code'] == "1000"
            assert mock_call.call_count == 2

    def test_poll_timeout(self, client):
        with patch.object(client, 'call') as mock_call:
            mock_call.return_value = {"response": {"code": "1001"}} # Always pending
            
            with pytest.raises(WAPITimeoutError):
                client.poll_until_complete("cmd", {}, max_attempts=2, interval=0)

    def test_poll_error(self, client):
        with patch.object(client, 'call') as mock_call:
            mock_call.return_value = {"response": {"code": "2201", "result": "Fatal"}}
            
            res = client.poll_until_complete("cmd", {}, max_attempts=1)
            # Should return the error result, not raise timeout
            assert res['response']['code'] == "2201"
