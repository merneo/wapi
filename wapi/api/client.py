"""
WEDOS WAPI Client

Core API client for communicating with WEDOS WAPI.
Supports both XML and JSON formats.
"""

import requests
import hashlib
import xml.etree.ElementTree as ET
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from .auth import calculate_auth
from ..utils.logger import get_logger


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
        self.logger = get_logger('api.client')
        
        self.logger.debug(f"Initialized WedosAPIClient (format: {'JSON' if use_json else 'XML'})")
    
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
            self.logger.error(f"XML parse error: {e}")
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
        from ..utils.logger import log_api_request, log_api_response
        
        log_api_request(self.logger, command, data)
        
        if self.use_json:
            request_body = self._build_json_request(command, data)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            try:
                response = requests.post(
                    self.base_url,
                    data={"request": request_body},
                    headers=headers,
                    timeout=30
                )
                self.logger.debug(f"HTTP Response status: {response.status_code}")
                response.raise_for_status()
                result = response.json()
            except requests.exceptions.RequestException as e:
                self.logger.error(f"HTTP request failed: {e}")
                raise
            
            # Log response
            resp_code = result.get('response', {}).get('code')
            resp_result = result.get('response', {}).get('result', '')
            log_api_response(self.logger, command, resp_code, resp_result)
            
            return result
        else:
            request_body = self._build_xml_request(command, data)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            try:
                response = requests.post(
                    self.base_url,
                    data={"request": request_body},
                    headers=headers,
                    timeout=30
                )
                self.logger.debug(f"HTTP Response status: {response.status_code}")
                response.raise_for_status()
                result = self._parse_xml_response(response.text)
            except requests.exceptions.RequestException as e:
                self.logger.error(f"HTTP request failed: {e}")
                raise
            
            # Log response
            resp_code = result.get('response', {}).get('code')
            resp_result = result.get('response', {}).get('result', '')
            log_api_response(self.logger, command, resp_code, resp_result)
            
            return result
    
    def domain_info(self, domain_name: str) -> Dict[str, Any]:
        """
        Get domain information
        
        Args:
            domain_name: Domain name
            
        Returns:
            Dictionary with domain information
        """
        return self.call("domain-info", {"name": domain_name})
    
    def domain_update_ns(self, domain_name: str, nsset_name: Optional[str] = None, 
                        nameservers: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Update domain nameservers
        
        Args:
            domain_name: Domain name
            nsset_name: Name of existing NSSET to assign
            nameservers: List of nameserver dictionaries (creates new NSSET if provided)
            
        Returns:
            Dictionary with API response
        """
        if nsset_name:
            # Use existing NSSET
            data = {
                "name": domain_name,
                "nsset": nsset_name
            }
            return self.call("domain-update-ns", data)
        elif nameservers:
            # Create new NSSET and assign it
            import time
            nsset_name = f"NS-{domain_name.replace('.', '-').upper()}-{int(time.time())}"
            
            # Get tech_c from domain info if available
            domain_info = self.domain_info(domain_name)
            tech_c = None
            if domain_info.get("response", {}).get("code") in ["1000", 1000]:
                domain_data = domain_info.get("response", {}).get("data", {}).get("domain", {})
                tech_c = domain_data.get("owner_c")
            
            # Create NSSET
            nsset_data = {
                "tld": domain_name.split('.')[-1] if '.' in domain_name else "cz",
                "name": nsset_name,
                "dns": {
                    "server": nameservers
                }
            }
            if tech_c:
                nsset_data["tech_c"] = tech_c
            
            create_result = self.call("nsset-create", nsset_data)
            
            if create_result.get("response", {}).get("code") not in ["1000", 1000]:
                return create_result
            
            # Get actual NSSET name from response
            created_nsset = create_result.get("response", {}).get("data", {}).get("nsset", nsset_name)
            
            # Assign NSSET to domain
            data = {
                "name": domain_name,
                "nsset": created_nsset
            }
            return self.call("domain-update-ns", data)
        else:
            return {
                "response": {
                    "code": "2100",
                    "result": "Either nsset_name or nameservers must be provided"
                }
            }
    
    def ping(self) -> Dict[str, Any]:
        """
        Test API connection
        
        Returns:
            Dictionary with ping response
        """
        return self.call("ping", {})
    
    def poll_until_complete(
        self,
        check_command: str,
        check_data: Dict[str, Any],
        is_complete: Optional[Callable[[Dict[str, Any]], bool]] = None,
        max_attempts: int = 60,
        interval: int = 10,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Poll API until operation completes
        
        Args:
            check_command: Command to poll (e.g., "domain-info", "nsset-info")
            check_data: Data dictionary for check command
            is_complete: Optional function to check if operation is complete.
                        Takes response dict, returns True if complete.
                        If None, checks for code 1000.
            max_attempts: Maximum polling attempts (default: 60)
            interval: Seconds between attempts (default: 10)
            verbose: Print progress messages (default: False)
            
        Returns:
            Final status response or timeout error
        """
        self.logger.info(f"Starting polling for {check_command} (max {max_attempts} attempts, interval {interval}s)")
        
        for attempt in range(1, max_attempts + 1):
            self.logger.debug(f"Polling attempt {attempt}/{max_attempts} for {check_command}")
            
            if verbose:
                print(f"  Polling attempt {attempt}/{max_attempts}...", end='', flush=True)
            
            result = self.call(check_command, check_data)
            response = result.get('response', {})
            code = response.get('code')
            
            # Check if complete
            if is_complete:
                if is_complete(result):
                    self.logger.info(f"Polling completed successfully after {attempt} attempts")
                    if verbose:
                        print(" ✅ Complete!")
                    return result
            else:
                # Default: check for code 1000 (success)
                if code == '1000' or code == 1000:
                    self.logger.info(f"Polling completed successfully after {attempt} attempts")
                    if verbose:
                        print(" ✅ Complete!")
                    return result
            
            # Check for error (not async, but actual error)
            if code and str(code).startswith('2'):
                # Error code (2xxx), not async
                error_msg = response.get('result', 'Unknown error')
                self.logger.warning(f"Polling encountered error: {error_msg} (code: {code})")
                if verbose:
                    print(f" ❌ Error: {error_msg}")
                return result
            
            if verbose:
                print(" ⏳ Still processing...")
            
            # Wait before next attempt
            if attempt < max_attempts:
                self.logger.debug(f"Waiting {interval}s before next polling attempt")
                time.sleep(interval)
        
        # Timeout
        timeout_msg = f"Polling timeout after {max_attempts} attempts ({max_attempts * interval} seconds)"
        self.logger.error(timeout_msg)
        return {
            "response": {
                "code": "9998",
                "result": timeout_msg
            }
        }
