"""
Domain availability search and WHOIS lookup command.

Provides a single `wapi search <domain>` entry point that:
1) Tries to check availability via WAPI (`domains-availability`).
2) If registered or undetermined, fetches WHOIS data.
"""

import socket
import sys
from typing import Any, Dict, Iterable, Optional

from ..api.client import WedosAPIClient
from ..constants import EXIT_SUCCESS
from ..exceptions import WAPIRequestError, WAPIValidationError
from ..utils.formatters import format_output
from ..utils.logger import get_logger
from ..utils.validators import validate_domain
from ..config import get_config

# Common WHOIS servers by TLD for faster lookups
DEFAULT_WHOIS_SERVERS = {
    "com": "whois.verisign-grs.com",
    "net": "whois.verisign-grs.com",
    "org": "whois.pir.org",
    "io": "whois.nic.io",
    "cz": "whois.nic.cz",
    "sk": "whois.sk-nic.sk",
    "info": "whois.afilias.net",
}

# Phrases indicating availability in WHOIS responses (case-insensitive)
AVAILABLE_PATTERNS = (
    "no match",
    "not found",
    "no entries found",
    "available",
    "status: free",
    "status: available",
    "status: unassigned",
)

# Phrases indicating the domain is registered
REGISTERED_PATTERNS = (
    "domain name:",
    "domain:",  # CZ.NIC format
    "registrar:",
    "creation date",
    "registered:",  # CZ.NIC format
    "expire:",  # CZ.NIC format
    "expiry date",
    "status:",
    "name server",
    "nsset:",  # CZ.NIC format
    "admin-c:",  # CZ.NIC format
)


def interpret_status_value(value: Any) -> Optional[bool]:
    """
    Normalize availability indicators to boolean.

    Returns:
        True if clearly available, False if clearly registered, None if unknown.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if not text: # pragma: no cover
        return None

    available_values = {"available", "free", "volna", "true", "1", "yes"}
    registered_values = {"registered", "taken", "obsazena", "false", "0", "no"}

    if text in available_values:
        return True
    if text in registered_values:
        return False

    # Some APIs may return numeric flags (1 = available)
    if text.isdigit():
        return text == "1"

    return None


def interpret_api_availability(api_result: Dict[str, Any], domain: str) -> Optional[bool]:
    """
    Extract availability information from a WAPI response.
    """
    response = api_result.get("response", {})
    code = response.get("code")
    if code not in ["1000", 1000]:
        return None

    data = response.get("data", {}) or {}
    candidates: Iterable[Any] = ()

    # Common shapes: {"domain": {...}} or {"domains": [{...}]}
    if "domain" in data:
        domain_data = data.get("domain")
        if isinstance(domain_data, list):
            candidates = domain_data
        else:
            candidates = [domain_data]
    elif "domains" in data:
        domains_data = data.get("domains")
        if isinstance(domains_data, list):
            candidates = domains_data
        else:
            candidates = [domains_data]
    elif "availability" in data: # pragma: no cover
        candidates = [data.get("availability")]

    for entry in candidates:
        if not isinstance(entry, dict):
            continue

        name = (
            entry.get("name")
            or entry.get("domain")
            or entry.get("fqdn")
            or entry.get("id")
        )
        if name and name.lower() != domain.lower():
            continue

        status_value = (
            entry.get("status")
            or entry.get("state")
            or entry.get("available")
            or entry.get("avail")
        )
        interpreted = interpret_status_value(status_value)
        if interpreted is not None:
            return interpreted

    # Fallback to top-level flags
    for key in ("available", "status", "state"):
        interpreted = interpret_status_value(data.get(key))
        if interpreted is not None:
            return interpreted

    return None


def get_client(config_file: Optional[str] = None) -> Optional[WedosAPIClient]:
    """
    Small helper so tests can patch ``wapi.commands.search.get_client`` safely.
    """
    username = get_config('WAPI_USERNAME', config_file=config_file)
    password = get_config('WAPI_PASSWORD', config_file=config_file)
    if not (username and password):
        return None
    try:
        return WedosAPIClient(username, password, use_json=False)
    except Exception:
        return None


def _discover_whois_server(domain: str, timeout: int) -> Optional[str]:
    """
    Ask IANA for the authoritative WHOIS server for the domain's TLD.
    
    Uses a shorter timeout for discovery to avoid long waits.
    """
    logger = get_logger("commands.search")
    # Use shorter timeout for discovery (max 5 seconds)
    discovery_timeout = min(timeout, 5)
    try:
        tld = domain.rsplit(".", 1)[-1].lower()
        response = _query_whois("whois.iana.org", tld, discovery_timeout)
        for line in response.splitlines():
            if line.lower().startswith("whois:"):
                server = line.split(":", 1)[1].strip()
                if server:
                    logger.debug(f"Discovered WHOIS server for {tld}: {server}")
                    return server
    except Exception as exc: # pragma: no cover
        logger.debug(f"WHOIS server discovery failed: {exc}")
    return None


def _query_whois(server: str, domain: str, timeout: int) -> str:
    """
    Query a WHOIS server directly via TCP.
    
    Args:
        server: WHOIS server hostname
        domain: Domain name to query
        timeout: Socket timeout in seconds
        
    Returns:
        WHOIS response text
    """
    # Set socket timeout explicitly to prevent hangs
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        sock.connect((server, 43))
        sock.sendall(f"{domain}\r\n".encode("utf-8"))
        
        chunks = []
        max_size = 1024 * 1024  # 1MB limit to prevent memory issues
        total_size = 0
        
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
                total_size += len(data)
                if total_size > max_size:
                    # Truncate if response is too large
                    break
            except socket.timeout:
                # Timeout during read - return what we have
                break
    finally:
        sock.close()
    
    return b"".join(chunks).decode("utf-8", errors="replace")


def perform_whois_lookup(domain: str, server: Optional[str] = None, timeout: int = 10) -> str:
    """
    Perform a WHOIS lookup with sensible fallbacks.
    """
    logger = get_logger("commands.search")
    target_server = server or DEFAULT_WHOIS_SERVERS.get(domain.rsplit(".", 1)[-1].lower())
    if not target_server:
        target_server = _discover_whois_server(domain, timeout) or "whois.iana.org"

    try:
        return _query_whois(target_server, domain, timeout)
    except Exception as exc: # pragma: no cover
        logger.error(f"WHOIS lookup failed at {target_server}: {exc}")
        raise WAPIRequestError(f"WHOIS lookup failed: {exc}") from exc


def infer_availability_from_whois(whois_text: str) -> Optional[bool]:
    """
    Infer availability based on WHOIS response content.
    
    Checks registered patterns first (higher priority), then available patterns.
    """
    if not whois_text:
        return None

    text = whois_text.lower()
    # Check registered patterns first (higher priority)
    if any(pattern.lower() in text for pattern in REGISTERED_PATTERNS):
        return False
    # Then check available patterns
    if any(pattern.lower() in text for pattern in AVAILABLE_PATTERNS):
        return True
    return None


def cmd_search(args, client: Optional[WedosAPIClient] = None) -> int:
    """
    Handle `wapi search` command.
    """
    logger = get_logger("commands.search")
    logger.info(f"Searching domain availability for: {args.domain}")

    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        logger.warning(f"Invalid domain name: {args.domain} - {error}")
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        raise WAPIValidationError(f"Invalid domain name: {error}")

    availability: Optional[bool] = None
    availability_source = None
    whois_text: Optional[str] = None
    whois_error: Optional[str] = None

    if client is None:
        client = get_client(getattr(args, "config", None))

    # First attempt: WAPI availability endpoint
    if client:
        try:
            api_result = client.domain_availability(args.domain)
            availability = interpret_api_availability(api_result, args.domain)
            if availability is not None:
                availability_source = "wapi"
            else:
                # If the XML endpoint is not available (e.g., code 2010 Unknown command),
                # retry once using the JSON endpoint which some deployments enable instead.
                response = api_result.get("response", {}) if isinstance(api_result, dict) else {}
                code = response.get("code")
                if str(code) == "2010":
                    logger.info("Retrying availability via JSON endpoint after 2010 Unknown command")
                    try:
                        json_client = WedosAPIClient(
                            client.username, client.password, use_json=True
                        )
                        api_result_json = json_client.domain_availability(args.domain)
                        availability = interpret_api_availability(api_result_json, args.domain)
                        if availability is not None:
                            availability_source = "wapi"
                        else:
                            # Fall back to domain-info heuristic: 1000 => registered, 2303 => available
                            info_result = client.domain_info(args.domain)
                            info_resp = info_result.get("response", {}) if isinstance(info_result, dict) else {}
                            info_code = str(info_resp.get("code"))
                            if info_code == "1000":
                                availability = False
                                availability_source = "wapi"
                            elif info_code == "2303":  # object does not exist
                                availability = True
                                availability_source = "wapi"
                    except Exception as json_exc:  # pragma: no cover - best-effort fallback
                        logger.warning(f"JSON availability fallback failed: {json_exc}")
        except Exception as exc:
            logger.warning(f"WAPI availability lookup failed: {exc}")

    # WHOIS lookup if registered or undetermined
    if availability is False or availability is None:
        try:
            whois_text = perform_whois_lookup(
                args.domain,
                server=getattr(args, "whois_server", None),
                timeout=getattr(args, "whois_timeout", 10),
            )
            inferred = infer_availability_from_whois(whois_text)
            if availability is None and inferred is not None:
                availability = inferred
                availability_source = availability_source or "whois"
        except Exception as exc:
            whois_error = str(exc)
            logger.error(f"WHOIS lookup failed for {args.domain}: {exc}")

    if availability is None:
        logger.error("Could not determine domain availability")
        print("Error: Could not determine domain availability (WAPI/WHOIS failed)", file=sys.stderr)
        raise WAPIRequestError("Could not determine domain availability")

    result_payload: Dict[str, Any] = {
        "domain": args.domain,
        "available": availability,
        "source": availability_source or "whois",
    }

    if whois_text and not availability:
        # Only include WHOIS output when domain appears registered
        result_payload["whois"] = whois_text.strip()
    if whois_error:
        result_payload["whois_error"] = whois_error

    print(format_output(result_payload, args.format))
    return EXIT_SUCCESS

