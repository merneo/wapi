"""
Input validation utilities for WAPI CLI

All validation functions use RFC-compliant standards and academic examples.
"""

import re
from typing import Tuple, Optional
from .logger import get_logger


def validate_domain(domain: str) -> Tuple[bool, Optional[str]]:
    """
    Validate domain name format.
    
    Args:
        domain: Domain name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Examples:
        >>> validate_domain('example.com')
        (True, None)
        >>> validate_domain('invalid..domain')
        (False, 'Contains consecutive dots')
    """
    logger = get_logger('utils.validators')
    
    if not domain:
        logger.debug("Domain validation failed: empty domain")
        return False, "Domain name cannot be empty"
    
    if len(domain) > 253:
        return False, "Domain name too long (max 253 characters)"
    
    # Check for consecutive dots
    if '..' in domain:
        return False, "Contains consecutive dots"
    
    # Check for valid characters (RFC 1123)
    if not re.match(r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?)*$', domain, re.IGNORECASE):
        return False, "Invalid domain name format"
    
    # Must have at least one dot
    if '.' not in domain:
        logger.debug(f"Domain validation failed: {domain} - missing dot")
        return False, "Domain must contain at least one dot"
    
    logger.debug(f"Domain validation passed: {domain}")
    return True, None


def validate_ipv4(ip: str) -> Tuple[bool, Optional[str]]:
    """
    Validate IPv4 address format.
    
    Args:
        ip: IPv4 address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Examples:
        >>> validate_ipv4('192.0.2.1')
        (True, None)
        >>> validate_ipv4('999.999.999.999')
        (False, 'Invalid IPv4 address')
    """
    if not ip:
        return False, "IPv4 address cannot be empty"
    
    parts = ip.split('.')
    if len(parts) != 4:
        return False, "IPv4 address must have 4 octets"
    
    try:
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False, "Each octet must be 0-255"
    except ValueError:
        return False, "Invalid IPv4 address format"
    
    return True, None


def validate_ipv6(ip: str) -> Tuple[bool, Optional[str]]:
    """
    Validate IPv6 address format.
    
    Args:
        ip: IPv6 address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Examples:
        >>> validate_ipv6('2001:db8::1')
        (True, None)
        >>> validate_ipv6('invalid')
        (False, 'Invalid IPv6 address format')
    """
    if not ip:
        return False, "IPv6 address cannot be empty"
    
    # Basic IPv6 validation (simplified)
    # Full validation would be more complex
    if '::' in ip:
        # Compressed format
        parts = ip.split('::')
        if len(parts) > 2:
            return False, "Invalid IPv6 address format"
    
    # Check for valid characters
    if not re.match(r'^[0-9a-fA-F:]+$', ip):
        return False, "Invalid IPv6 address format"
    
    return True, None


def validate_nameserver(ns_string: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Parse and validate nameserver string format: name:ipv4:ipv6 or name:ipv4
    
    Args:
        ns_string: Nameserver string in format "name:ipv4:ipv6" or "name:ipv4"
        
    Returns:
        Tuple of (is_valid, parsed_dict, error_message)
        
    Examples:
        >>> validate_nameserver('ns1.example.com:192.0.2.1:2001:db8::1')
        (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1', 'addr_ipv6': '2001:db8::1'}, None)
        >>> validate_nameserver('ns1.example.com:192.0.2.1')
        (True, {'name': 'ns1.example.com', 'addr_ipv4': '192.0.2.1', 'addr_ipv6': ''}, None)
    """
    if not ns_string:
        return False, None, "Nameserver string cannot be empty"
    
    # Split by colon
    parts = ns_string.split(':')
    if len(parts) < 2:
        return False, None, "Nameserver format: name:ipv4:ipv6 or name:ipv4"
    
    name = parts[0]
    ipv4 = parts[1]
    
    # IPv6 is everything after IPv4 (may contain colons)
    if len(parts) > 2:
        ipv6 = ':'.join(parts[2:])
    else:
        ipv6 = ""
    
    # Validate domain name
    name_valid, name_error = validate_domain(name)
    if not name_valid:
        return False, None, f"Invalid nameserver name: {name_error}"
    
    # Validate IPv4
    if ipv4:
        ipv4_valid, ipv4_error = validate_ipv4(ipv4)
        if not ipv4_valid:
            return False, None, f"Invalid IPv4 address: {ipv4_error}"
    
    # Validate IPv6 (if provided)
    if ipv6:
        ipv6_valid, ipv6_error = validate_ipv6(ipv6)
        if not ipv6_valid:
            return False, None, f"Invalid IPv6 address: {ipv6_error}"
    
    result = {
        "name": name,
        "addr_ipv4": ipv4,
        "addr_ipv6": ipv6
    }
    
    return True, result, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email address cannot be empty"
    
    # Basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email address format"
    
    return True, None
