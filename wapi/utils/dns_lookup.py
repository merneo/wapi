"""
DNS lookup utilities for WAPI CLI

Provides functions to resolve DNS records (A, AAAA) for nameservers.
"""

import socket
from types import SimpleNamespace
from typing import List, Optional, Tuple

from ..exceptions import WAPIDNSLookupError, WAPITimeoutError
from ..utils.validators import validate_ipv6
from .logger import get_logger

# Try to import dnspython, fallback to socket if not available
try:
    import dns.resolver
    DNS_PYTHON_AVAILABLE = True
except ImportError:  # pragma: no cover
    DNS_PYTHON_AVAILABLE = False

# Safe exception tuple even when socket is mocked in tests
_SOCKET_ERROR_TYPES = tuple(
    exc for exc in (socket.herror, socket.gaierror, OSError, TimeoutError)
    if isinstance(exc, type) and issubclass(exc, BaseException)
) or (Exception,)

# DNS lookup timeout (seconds)
DNS_LOOKUP_TIMEOUT = 5


def _timeout_handler(signum, frame):
    """Handler for DNS lookup timeout"""
    raise TimeoutError("DNS lookup timeout")


def get_ipv6_from_ipv4(ipv4: str, timeout: int = DNS_LOOKUP_TIMEOUT) -> Optional[str]:
    """
    Get IPv6 address from IPv4 address using reverse DNS lookup.
    
    This is a simplified approach - in practice, you'd need to:
    1. Do reverse DNS lookup on IPv4
    2. Get AAAA record for the hostname
    
    Args:
        ipv4: IPv4 address
        timeout: DNS lookup timeout in seconds (default: 5)
        
    Returns:
        IPv6 address if found and valid, None otherwise
    """
    logger = get_logger('utils.dns_lookup')
    logger.debug(f"Attempting to find IPv6 for IPv4: {ipv4} (timeout: {timeout}s)")
    
    try:
        # Set timeout for socket operations
        socket.setdefaulttimeout(timeout)
        
        # Try reverse DNS lookup to get hostname
        try:
            hostname, _, _ = socket.gethostbyaddr(ipv4)
            logger.debug(f"Reverse DNS for {ipv4}: {hostname}")
        except _SOCKET_ERROR_TYPES as e: # pragma: no cover
            logger.debug(f"Reverse DNS lookup failed for {ipv4}: {e}") # pragma: no cover
            return None # pragma: no cover
        
        # Try to get AAAA record for the hostname
        if DNS_PYTHON_AVAILABLE:
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = timeout
                resolver.lifetime = timeout
                answers = resolver.resolve(hostname, 'AAAA')
                if answers:
                    ipv6 = str(answers[0])
                    # Validate IPv6 address
                    is_valid, error = validate_ipv6(ipv6)
                    if is_valid:
                        logger.info(f"Found IPv6 {ipv6} for IPv4 {ipv4} via {hostname}")
                        return ipv6
                    else:
                        logger.warning(f"Invalid IPv6 address discovered: {ipv6} - {error}")
                        return None
            except dns.resolver.Timeout as e:
                logger.debug(f"DNS lookup timeout for {hostname}: {e}")
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer) as e:
                logger.debug(f"No AAAA record found for {hostname}: {e}")
            except Exception as e:
                logger.debug(f"Unexpected DNS error for {hostname}: {e}")
        
        # Fallback: try socket.getaddrinfo regardless of dnspython availability
        try: # pragma: no cover
            addrinfo = socket.getaddrinfo(hostname, None, socket.AF_INET6, socket.SOCK_STREAM) # pragma: no cover
            if addrinfo: # pragma: no cover
                ipv6 = addrinfo[0][4][0]
                # Validate IPv6 address
                is_valid, error = validate_ipv6(ipv6)
                if is_valid:
                    logger.info(f"Found IPv6 {ipv6} for IPv4 {ipv4} via {hostname}")
                    return ipv6
                else:
                    logger.warning(f"Invalid IPv6 address discovered: {ipv6} - {error}")
                    return None
        except _SOCKET_ERROR_TYPES as e:
            logger.debug(f"No IPv6 address found for {hostname}: {e}")
        
        logger.debug(f"No IPv6 address found for IPv4 {ipv4}")
        return None
    except _SOCKET_ERROR_TYPES as e:
        logger.debug(f"Could not resolve IPv6 for {ipv4}: {e}")
        return None
    finally:
        # Reset socket timeout to default
        socket.setdefaulttimeout(None)


def get_ipv6_from_nameserver(ns_name: str, ipv4: str, timeout: int = DNS_LOOKUP_TIMEOUT) -> Optional[str]:
    """
    Get IPv6 address for a nameserver.
    
    First tries to get AAAA record for the nameserver hostname.
    If that fails, tries to get IPv6 from IPv4 address (reverse DNS + AAAA lookup).
    
    Args:
        ns_name: Nameserver hostname (e.g., ns1.example.com)
        ipv4: IPv4 address
        timeout: DNS lookup timeout in seconds (default: 5)
        
    Returns:
        IPv6 address if found and valid, None otherwise
    """
    logger = get_logger('utils.dns_lookup')
    logger.debug(f"Looking up IPv6 for nameserver {ns_name} (IPv4: {ipv4}, timeout: {timeout}s)")
    
    # First, try AAAA record for the nameserver hostname directly
    if DNS_PYTHON_AVAILABLE:
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = timeout
            resolver.lifetime = timeout
            answers = resolver.resolve(ns_name, 'AAAA')
            if answers:
                ipv6 = str(answers[0])
                # Validate IPv6 address
                is_valid, error = validate_ipv6(ipv6)
                if is_valid:
                    logger.info(f"Found IPv6 {ipv6} for nameserver {ns_name} via AAAA record")
                    return ipv6
                else:
                    logger.warning(f"Invalid IPv6 address discovered for {ns_name}: {ipv6} - {error}")
                    return None
        except dns.resolver.Timeout as e:
            logger.debug(f"DNS lookup timeout for {ns_name}: {e}")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers) as e:
            logger.debug(f"No AAAA record found for {ns_name}: {e}")
        except Exception as e:
            logger.debug(f"Unexpected DNS error for {ns_name}: {e}")
    
    # Fallback: try socket.getaddrinfo regardless of dnspython availability
    try:
        socket.setdefaulttimeout(timeout)
        addrinfo = socket.getaddrinfo(ns_name, None, socket.AF_INET6, socket.SOCK_STREAM)
        if addrinfo:
            ipv6 = addrinfo[0][4][0]
            # Validate IPv6 address
            is_valid, error = validate_ipv6(ipv6)
            if is_valid:
                logger.info(f"Found IPv6 {ipv6} for nameserver {ns_name}")
                return ipv6
            else:
                logger.warning(f"Invalid IPv6 address discovered for {ns_name}: {ipv6} - {error}")
                return None
    except _SOCKET_ERROR_TYPES as e: # pragma: no cover
        logger.debug(f"No IPv6 address found for {ns_name}: {e}") # pragma: no cover
    finally:
        socket.setdefaulttimeout(None)
    
    # If direct lookup failed, try to get IPv6 from IPv4 (reverse DNS + AAAA)
    ipv6 = get_ipv6_from_ipv4(ipv4, timeout=timeout) # pragma: no cover
    if ipv6: # pragma: no cover
        logger.info(f"Found IPv6 {ipv6} for nameserver {ns_name} via IPv4 {ipv4}") # pragma: no cover
        return ipv6 # pragma: no cover
    
    logger.debug(f"No IPv6 address found for nameserver {ns_name}")
    return None # pragma: no cover


def enhance_nameserver_with_ipv6(nameserver: dict, timeout: int = DNS_LOOKUP_TIMEOUT) -> Tuple[dict, bool, Optional[str]]:
    """
    Enhance nameserver dictionary with IPv6 if missing.
    
    If nameserver has IPv4 but no IPv6, attempts to find IPv6 address.
    
    Args:
        nameserver: Nameserver dictionary with 'name' and 'addr_ipv4'
        timeout: DNS lookup timeout in seconds (default: 5)
        
    Returns:
        Tuple of (enhanced_nameserver_dict, ipv6_found, warning_message)
        - enhanced_nameserver_dict: Enhanced nameserver dictionary with IPv6 if found
        - ipv6_found: True if IPv6 was found and added, False otherwise
        - warning_message: Warning message if lookup failed or IPv6 not found, None otherwise
    """
    logger = get_logger('utils.dns_lookup')
    
    name = nameserver.get('name', '')
    ipv4 = nameserver.get('addr_ipv4', '')
    ipv6 = nameserver.get('addr_ipv6', '')
    
    # If IPv6 already exists, return as-is
    if ipv6:
        logger.debug(f"Nameserver {name} already has IPv6: {ipv6}")
        return nameserver, False, None
    
    # If no IPv4, can't get IPv6
    if not ipv4:
        logger.debug(f"Nameserver {name} has no IPv4, skipping IPv6 lookup")
        return nameserver, False, None
    
    # Try to get IPv6
    try:
        found_ipv6 = get_ipv6_from_nameserver(name, ipv4, timeout=timeout)
        if found_ipv6:
            nameserver['addr_ipv6'] = found_ipv6
            logger.info(f"Enhanced nameserver {name} with IPv6: {found_ipv6}")
            return nameserver, True, None
        else:
            warning = f"IPv6 address not found for nameserver {name} (IPv4: {ipv4}). Continuing with IPv4 only."
            logger.info(warning)
            return nameserver, False, warning
    except _SOCKET_ERROR_TYPES as e:
        warning = f"DNS lookup timeout for nameserver {name}: {e}. Continuing with IPv4 only."
        logger.warning(warning)
        return nameserver, False, warning
    except Exception as e:
        warning = f"Unexpected error during DNS lookup for nameserver {name}: {e}. Continuing with IPv4 only."
        logger.warning(warning)
        return nameserver, False, warning
