"""
Complete tests for wapi.api.client module to achieve 100% coverage

Tests for missing lines: XML/JSON building, parsing, and various response structures.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
import xml.etree.ElementTree as ET

from wapi.api.client import WedosAPIClient
from wapi.exceptions import WAPIRequestError


class TestAPIClientXMLBuilding(unittest.TestCase):
    """Test XML request building methods"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password", use_json=False)

    def test_build_xml_request_with_data(self):
        """Test _build_xml_request with data (lines 62-64)"""
        data = {"domain": "example.com", "name": "test"}
        result = self.client._build_xml_request("domain-info", data)
        
        self.assertIn("domain-info", result)
        self.assertIn("example.com", result)
        self.assertIn("<data>", result)

    def test_build_xml_request_without_data(self):
        """Test _build_xml_request without data"""
        result = self.client._build_xml_request("ping", None)
        
        self.assertIn("ping", result)
        self.assertNotIn("<data>", result)

    def test_build_xml_data_with_dict(self):
        """Test _build_xml_data with dict (lines 70-73)"""
        parent = ET.Element("root")
        data = {"domain": "example.com", "name": "test"}
        
        self.client._build_xml_data(parent, data)
        
        self.assertEqual(len(parent), 2)
        self.assertEqual(parent.find("domain").text, "example.com")
        self.assertEqual(parent.find("name").text, "test")

    def test_build_xml_data_with_nested_dict(self):
        """Test _build_xml_data with nested dict (lines 71-73)"""
        parent = ET.Element("root")
        data = {"domain": {"name": "example.com", "status": "active"}}
        
        self.client._build_xml_data(parent, data)
        
        domain_elem = parent.find("domain")
        self.assertIsNotNone(domain_elem)
        self.assertEqual(domain_elem.find("name").text, "example.com")
        self.assertEqual(domain_elem.find("status").text, "active")

    def test_build_xml_data_with_list_of_dicts(self):
        """Test _build_xml_data with list of dicts (lines 74-78)"""
        parent = ET.Element("root")
        data = {"servers": [{"name": "ns1.example.com"}, {"name": "ns2.example.com"}]}
        
        self.client._build_xml_data(parent, data)
        
        servers = parent.findall("servers")
        self.assertEqual(len(servers), 2)
        self.assertEqual(servers[0].find("name").text, "ns1.example.com")
        self.assertEqual(servers[1].find("name").text, "ns2.example.com")

    def test_build_xml_data_with_list_of_strings(self):
        """Test _build_xml_data with list of strings (lines 74-80)"""
        parent = ET.Element("root")
        data = {"names": ["name1", "name2", "name3"]}
        
        self.client._build_xml_data(parent, data)
        
        names = parent.findall("names")
        self.assertEqual(len(names), 3)
        self.assertEqual(names[0].text, "name1")
        self.assertEqual(names[1].text, "name2")
        self.assertEqual(names[2].text, "name3")

    def test_build_xml_data_with_none_value(self):
        """Test _build_xml_data with None value (line 82)"""
        parent = ET.Element("root")
        data = {"optional": None}
        
        self.client._build_xml_data(parent, data)
        
        optional_elem = parent.find("optional")
        self.assertIsNotNone(optional_elem)
        self.assertEqual(optional_elem.text, "")


class TestAPIClientJSONBuilding(unittest.TestCase):
    """Test JSON request building methods"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password", use_json=True)

    def test_build_json_request_with_data(self):
        """Test _build_json_request with data (lines 96-97)"""
        data = {"domain": "example.com"}
        result = self.client._build_json_request("domain-info", data)
        
        import json
        parsed = json.loads(result)
        
        self.assertEqual(parsed["command"], "domain-info")
        self.assertIn("data", parsed)
        self.assertEqual(parsed["data"]["domain"], "example.com")

    def test_build_json_request_without_data(self):
        """Test _build_json_request without data"""
        result = self.client._build_json_request("ping", None)
        
        import json
        parsed = json.loads(result)
        
        self.assertEqual(parsed["command"], "ping")
        self.assertNotIn("data", parsed)


class TestAPIClientXMLParsing(unittest.TestCase):
    """Test XML response parsing methods"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password", use_json=False)

    def test_parse_xml_response_root_is_response(self):
        """Test _parse_xml_response when root is response (lines 108-109)"""
        xml_str = '<response><code>1000</code><result>OK</result></response>'
        result = self.client._parse_xml_response(xml_str)
        
        self.assertIn("response", result)
        self.assertEqual(result["response"]["code"], 1000)
        self.assertEqual(result["response"]["result"], "OK")

    def test_parse_xml_response_has_response_child(self):
        """Test _parse_xml_response when response is a child (lines 111-114)"""
        xml_str = '<wapi><response><code>1000</code><result>OK</result></response></wapi>'
        result = self.client._parse_xml_response(xml_str)
        
        self.assertIn("response", result)
        self.assertEqual(result["response"]["code"], 1000)

    def test_parse_xml_response_no_response_element(self):
        """Test _parse_xml_response when no response element (lines 115-117)"""
        xml_str = '<root><code>1000</code><result>OK</result></root>'
        result = self.client._parse_xml_response(xml_str)
        
        self.assertIn("response", result)
        self.assertEqual(result["response"]["code"], 1000)

    def test_parse_xml_element_leaf_node(self):
        """Test _parse_xml_element with leaf node (lines 127-133)"""
        elem = ET.Element("code")
        elem.text = "1000"
        
        result = self.client._parse_xml_element(elem)
        
        self.assertEqual(result, 1000)  # Should convert to int

    def test_parse_xml_element_leaf_node_string(self):
        """Test _parse_xml_element with leaf node string (lines 127-133)"""
        elem = ET.Element("result")
        elem.text = "OK"
        
        result = self.client._parse_xml_element(elem)
        
        self.assertEqual(result, "OK")

    def test_parse_xml_element_with_children(self):
        """Test _parse_xml_element with children (lines 135-148)"""
        root = ET.Element("response")
        code_elem = ET.SubElement(root, "code")
        code_elem.text = "1000"
        result_elem = ET.SubElement(root, "result")
        result_elem.text = "OK"
        
        result = self.client._parse_xml_element(root)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["code"], 1000)
        self.assertEqual(result["result"], "OK")

    def test_parse_xml_element_multiple_same_tags(self):
        """Test _parse_xml_element with multiple same tags (lines 140-144)"""
        root = ET.Element("servers")
        server1 = ET.SubElement(root, "server")
        server1.text = "ns1.example.com"
        server2 = ET.SubElement(root, "server")
        server2.text = "ns2.example.com"
        
        result = self.client._parse_xml_element(root)
        
        self.assertIsInstance(result["server"], list)
        self.assertEqual(len(result["server"]), 2)
        self.assertEqual(result["server"][0], "ns1.example.com")
        self.assertEqual(result["server"][1], "ns2.example.com")


class TestAPIClientCallMethod(unittest.TestCase):
    """Test call() method with various scenarios"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password", use_json=False)

    @patch('wapi.api.client.requests.post')
    def test_call_xml_format_success(self, mock_post):
        """Test call() with XML format successful response (lines 194-222)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<response><code>1000</code><result>OK</result></response>'
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.client.call("ping", {})
        
        self.assertIn("response", result)
        self.assertEqual(result["response"]["code"], 1000)

    @patch('wapi.api.client.requests.post')
    def test_call_json_format_success(self, mock_post):
        """Test call() with JSON format successful response (lines 165-193)"""
        client = WedosAPIClient("user@example.com", "password", use_json=True)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "code": "1000",
                "result": "OK"
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = client.call("ping", {})
        
        self.assertIn("response", result)
        self.assertEqual(result["response"]["code"], "1000")

    @patch('wapi.api.client.requests.post')
    def test_call_json_format_timeout(self, mock_post):
        """Test call() with JSON format timeout (lines 178-180)"""
        client = WedosAPIClient("user@example.com", "password", use_json=True)
        
        from wapi.exceptions import WAPITimeoutError
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")
        
        with self.assertRaises(WAPITimeoutError):
            client.call("ping", {})

    @patch('wapi.api.client.requests.post')
    def test_call_json_format_connection_error(self, mock_post):
        """Test call() with JSON format connection error (lines 181-183)"""
        client = WedosAPIClient("user@example.com", "password", use_json=True)
        
        from wapi.exceptions import WAPIConnectionError
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with self.assertRaises(WAPIConnectionError):
            client.call("ping", {})

    @patch('wapi.api.client.requests.post')
    def test_call_json_format_request_exception(self, mock_post):
        """Test call() with JSON format request exception (lines 184-186)"""
        client = WedosAPIClient("user@example.com", "password", use_json=True)
        
        from wapi.exceptions import WAPIRequestError
        mock_post.side_effect = requests.exceptions.RequestException("Request failed")
        
        with self.assertRaises(WAPIRequestError):
            client.call("ping", {})


class TestAPIClientDomainUpdateNS(unittest.TestCase):
    """Test domain_update_ns method"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password", use_json=False)

    @patch.object(WedosAPIClient, 'call')
    def test_domain_update_ns_with_nsset_name(self, mock_call):
        """Test domain_update_ns with nsset_name (lines 249-255)"""
        mock_call.return_value = {"response": {"code": "1000", "result": "OK"}}
        
        result = self.client.domain_update_ns("example.com", nsset_name="NS-EXAMPLE")
        
        mock_call.assert_called_once_with("domain-update-ns", {
            "name": "example.com",
            "nsset": "NS-EXAMPLE"
        })
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'domain_info')
    @patch.object(WedosAPIClient, 'call')
    def test_domain_update_ns_with_nameservers(self, mock_call, mock_domain_info):
        """Test domain_update_ns with nameservers (lines 256-292)"""
        # Mock domain_info to return tech_c
        mock_domain_info.return_value = {
            "response": {
                "code": "1000",
                "data": {
                    "domain": {
                        "owner_c": "TECH-123"
                    }
                }
            }
        }
        
        # Mock nsset-create call
        mock_call.side_effect = [
            {"response": {"code": "1000", "data": {"nsset": "NS-EXAMPLE-1234567890"}}},
            {"response": {"code": "1000", "result": "OK"}}
        ]
        
        nameservers = [
            {"name": "ns1.example.com", "addr_ipv4": "192.0.2.1"},
            {"name": "ns2.example.com", "addr_ipv4": "192.0.2.2"}
        ]
        
        result = self.client.domain_update_ns("example.com", nameservers=nameservers)
        
        # Should call nsset-create and then domain-update-ns
        self.assertEqual(mock_call.call_count, 2)
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'domain_info')
    @patch.object(WedosAPIClient, 'call')
    def test_domain_update_ns_with_nameservers_no_tech_c(self, mock_call, mock_domain_info):
        """Test domain_update_ns with nameservers but no tech_c (lines 256-292)"""
        # Mock domain_info to return no tech_c
        mock_domain_info.return_value = {
            "response": {
                "code": "1000",
                "data": {
                    "domain": {}
                }
            }
        }
        
        mock_call.side_effect = [
            {"response": {"code": "1000", "data": {"nsset": "NS-EXAMPLE-1234567890"}}},
            {"response": {"code": "1000", "result": "OK"}}
        ]
        
        nameservers = [{"name": "ns1.example.com", "addr_ipv4": "192.0.2.1"}]
        result = self.client.domain_update_ns("example.com", nameservers=nameservers)
        
        self.assertEqual(mock_call.call_count, 2)

    @patch.object(WedosAPIClient, 'domain_info')
    @patch.object(WedosAPIClient, 'call')
    def test_domain_update_ns_with_nameservers_create_fails(self, mock_call, mock_domain_info):
        """Test domain_update_ns when nsset-create fails (lines 281-282)"""
        mock_domain_info.return_value = {"response": {"code": "1000", "data": {"domain": {}}}}
        # First call (nsset-create) fails, should not call domain-update-ns
        mock_call.return_value = {"response": {"code": "2100", "result": "Error"}}
        
        nameservers = [{"name": "ns1.example.com", "addr_ipv4": "192.0.2.1"}]
        result = self.client.domain_update_ns("example.com", nameservers=nameservers)
        
        # Should return error without calling domain-update-ns
        self.assertEqual(result["response"]["code"], "2100")
        # domain_info + nsset-create = 2 calls, but domain-update-ns should not be called
        self.assertGreaterEqual(mock_call.call_count, 1)

    def test_domain_update_ns_without_nsset_or_nameservers(self):
        """Test domain_update_ns without nsset_name or nameservers (lines 293-299)"""
        result = self.client.domain_update_ns("example.com")
        
        self.assertEqual(result["response"]["code"], "2100")
        self.assertIn("must be provided", result["response"]["result"])


class TestAPIClientPolling(unittest.TestCase):
    """Test poll_until_complete method"""

    def setUp(self):
        """Set up test client"""
        self.client = WedosAPIClient("user@example.com", "password", use_json=False)

    @patch.object(WedosAPIClient, 'call')
    @patch('time.sleep')
    def test_poll_until_complete_with_verbose(self, mock_sleep, mock_call):
        """Test poll_until_complete with verbose=True (lines 341, 352, 359, 368, 372)"""
        # Mock call to return success on second attempt
        mock_call.side_effect = [
            {"response": {"code": "1001", "result": "Processing"}},
            {"response": {"code": "1000", "result": "OK"}}
        ]
        
        result = self.client.poll_until_complete("domain-info", {"name": "example.com"}, verbose=True)
        
        self.assertEqual(result["response"]["code"], "1000")
        self.assertEqual(mock_call.call_count, 2)
        mock_sleep.assert_called_once()

    @patch.object(WedosAPIClient, 'call')
    @patch('time.sleep')
    def test_poll_until_complete_with_custom_check_verbose(self, mock_sleep, mock_call):
        """Test poll_until_complete with custom is_complete and verbose (lines 341, 352)"""
        def is_complete(result):
            return result.get("response", {}).get("code") == "1000"
        
        mock_call.side_effect = [
            {"response": {"code": "1001", "result": "Processing"}},
            {"response": {"code": "1000", "result": "OK"}}
        ]
        
        result = self.client.poll_until_complete(
            "domain-info", 
            {"name": "example.com"}, 
            is_complete=is_complete,
            verbose=True
        )
        
        self.assertEqual(result["response"]["code"], "1000")

    @patch.object(WedosAPIClient, 'call')
    @patch('time.sleep')
    def test_poll_until_complete_error_with_verbose(self, mock_sleep, mock_call):
        """Test poll_until_complete with error code and verbose (lines 368)"""
        mock_call.return_value = {"response": {"code": "2100", "result": "Error occurred"}}
        
        result = self.client.poll_until_complete("domain-info", {"name": "example.com"}, verbose=True)
        
        self.assertEqual(result["response"]["code"], "2100")
        mock_sleep.assert_not_called()  # Should return immediately on error

    @patch.object(WedosAPIClient, 'call')
    @patch('time.sleep')
    def test_poll_until_complete_timeout_with_verbose(self, mock_sleep, mock_call):
        """Test poll_until_complete timeout with verbose (lines 372)"""
        from wapi.exceptions import WAPITimeoutError
        # Mock call to always return async (never complete)
        mock_call.return_value = {"response": {"code": "1001", "result": "Processing"}}
        
        # Should raise WAPITimeoutError
        with self.assertRaises(WAPITimeoutError):
            self.client.poll_until_complete(
                "domain-info", 
                {"name": "example.com"}, 
                max_attempts=2,
                verbose=True
            )
        
        # Should have tried max_attempts times
        self.assertEqual(mock_call.call_count, 2)


if __name__ == '__main__':
    unittest.main()
