"""
WEDOS WAPI Client

Core API client for communicating with WEDOS WAPI.
Supports both XML and JSON formats.
"""

import requests
import hashlib
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from .auth import calculate_auth


class WedosAPIClient:
    """WEDOS WAPI client supporting XML and JSON formats"""
    
    def __init__(self, username: str, password: str, base_url: str = "https://api.wedos.com/wapi", use_json: bool = False):
        """
        Initialize WEDOS API client
        
        Args:
            username: WEDOS username (email)
            password: WAPI password
            base_url: Base URL for API (default: https://api.wedos.com/wapi)
            use_json: Use JSON format instead of XML (default: False)
        """
        self.username = username
        self.password = password
        self.use_json = use_json
        self.base_url = f"{base_url}/json" if use_json else f"{base_url}/xml"
    
    def _calculate_auth(self) -> str:
        """Calculate authentication hash based on current hour in Europe/Prague timezone"""
        return calculate_auth(self.username, self.password)
    
    def _build_xml_request(self, command: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Build XML request body"""
        auth = self._calculate_auth()
        cl_trid = f"wapi-{int(datetime.now().timestamp())}"
        
        root = ET.Element("request")
        ET.SubElement(root, "user").text = self.username
        ET.SubElement(root, "auth").text = auth
        ET.SubElement(root, "command").text = command
        ET.SubElement(root, "clTRID").text = cl_trid
        
        if data:
            data_elem = ET.SubElement(root, "data")
            self._build_xml_data(data_elem, data)
        
        return ET.tostring(root, encoding='unicode')
    
    def _build_xml_data(self, parent: ET.Element, data: Dict[str, Any]):
        """Recursively build XML data structure"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._build_xml_data(child, value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        child = ET.SubElement(parent, key)
                        self._build_xml_data(child, item)
                    else:
                        ET.SubElement(parent, key).text = str(item)
            else:
                ET.SubElement(parent, key).text = str(value) if value is not None else ""
    
    def _build_json_request(self, command: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Build JSON request body"""
        auth = self._calculate_auth()
        cl_trid = f"wapi-{int(datetime.now().timestamp())}"
        
        request = {
            "user": self.username,
            "auth": auth,
            "command": command,
            "clTRID": cl_trid
        }
        
        if data:
            request["data"] = data
        
        return json.dumps(request)
    
    def _parse_xml_response(self, response_text: str) -> Dict[str, Any]:
        """Parse XML response to dictionary"""
        try:
            root = ET.fromstring(response_text)
            result = {}
            
            # WAPI XML response structure: <response> is the root or a child
            if root.tag == "response":
                result["response"] = self._parse_xml_element(root)
            else:
                # Look for response element
                response_elem = root.find("response")
                if response_elem is not None:
                    result["response"] = self._parse_xml_element(response_elem)
                else:
                    # Parse root as response
                    result["response"] = self._parse_xml_element(root)
            
            return result
        except ET.ParseError as e:
            return {
                "response": {
                    "code": "9999",
                    "result": f"XML Parse Error: {str(e)}"
                }
            }
    
    def _parse_xml_element(self, element: ET.Element) -> Any:
        """Recursively parse XML element to Python structure"""
        if len(element) == 0:
            # Leaf node - return text content
            text = element.text.strip() if element.text else ""
            # Try to convert to int if it's a number
            if text.isdigit():
                return int(text)
            return text
        
        # Has children
        result = {}
        for child in element:
            child_value = self._parse_xml_element(child)
            
            if child.tag in result:
                # Multiple children with same tag - convert to list
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_value)
            else:
                result[child.tag] = child_value
        
        return result
    
    def call(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call WEDOS WAPI command
        
        Args:
            command: API command name (e.g., "ping", "domain-info", "nsset-create")
            data: Optional dictionary with command data
            
        Returns:
            Dictionary with API response
        """
        if self.use_json:
            request_body = self._build_json_request(command, data)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(
                self.base_url,
                data={"request": request_body},
                headers=headers
            )
            return response.json()
        else:
            request_body = self._build_xml_request(command, data)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(
                self.base_url,
                data={"request": request_body},
                headers=headers
            )
            return self._parse_xml_response(response.text)
    
    def domain_info(self, domain_name: str) -> Dict[str, Any]:
        """
        Get domain information
        
        Args:
            domain_name: Domain name
            
        Returns:
            Dictionary with domain information
        """
        return self.call("domain-info", {"name": domain_name})
    
    def ping(self) -> Dict[str, Any]:
        """
        Test API connection
        
        Returns:
            Dictionary with ping response
        """
        return self.call("ping", {})
