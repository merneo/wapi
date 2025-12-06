"""
NSSET management commands for WAPI CLI

Handles all NSSET-related operations.
"""

import sys
from typing import Any, Dict, List, Optional

from ..api.client import WedosAPIClient
from ..constants import EXIT_SUCCESS, EXIT_ERROR, EXIT_VALIDATION_ERROR
from ..exceptions import (
    WAPIValidationError,
    WAPIRequestError,
    WAPITimeoutError,
)
from ..utils.dns_lookup import enhance_nameserver_with_ipv6
from ..utils.formatters import format_output
from ..utils.logger import get_logger
from ..utils.validators import validate_nameserver


def cmd_nsset_create(args, client: WedosAPIClient) -> int:
    """Handle nsset create command"""
    logger = get_logger('commands.nsset')
    logger.info(f"Creating NSSET: {args.name}")
    
    # Validate nameservers
    if not args.nameserver:
        logger.error("No nameservers provided")
        print("Error: At least one nameserver required (--nameserver)", file=sys.stderr)
        raise WAPIValidationError("At least one nameserver required (--nameserver)")
    
    nameservers = []
    ipv6_discovery_warnings = []
    ipv6_discovery_success = []
    
    for ns_string in args.nameserver:
        is_valid, parsed, error = validate_nameserver(ns_string)
        if not is_valid:
            logger.warning(f"Invalid nameserver format: {ns_string} - {error}")
            print(f"Error: Invalid nameserver format - {error}", file=sys.stderr)
            raise WAPIValidationError(f"Invalid nameserver format: {error}")
        
        # Enhance with IPv6 if missing and discovery is enabled
        if not args.no_ipv6_discovery and parsed.get('addr_ipv4') and not parsed.get('addr_ipv6'):
            logger.info(f"Attempting to find IPv6 for nameserver {parsed.get('name')}")
            enhanced, found, warning = enhance_nameserver_with_ipv6(parsed)
            if found:
                logger.info(f"Found IPv6 {enhanced.get('addr_ipv6')} for {enhanced.get('name')}")
                ipv6_discovery_success.append(f"{enhanced.get('name')}: {enhanced.get('addr_ipv6')}")
                parsed = enhanced
            elif warning:
                ipv6_discovery_warnings.append(warning)
                logger.debug(warning)
        elif args.no_ipv6_discovery and parsed.get('addr_ipv4') and not parsed.get('addr_ipv6'):
            logger.debug(f"IPv6 discovery disabled, skipping lookup for {parsed.get('name')}")
        
        nameservers.append(parsed)
    
    # Print informative messages
    if ipv6_discovery_success:
        print(f"ℹ️  IPv6 addresses discovered: {', '.join(ipv6_discovery_success)}", file=sys.stderr)
    if ipv6_discovery_warnings:
        for warning in ipv6_discovery_warnings:
            print(f"⚠️  {warning}", file=sys.stderr)
    
    # Build NSSET data
    nsset_data = {
        "tld": args.tld or "cz",
        "name": args.name,
        "dns": {
            "server": nameservers
        }
    }
    
    if args.tech_c:
        nsset_data["tech_c"] = args.tech_c
    
    # Call API
    result = client.call("nsset-create", nsset_data)
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        logger.info("NSSET created successfully")
        print("✅ NSSET created successfully")
        print(format_output(response.get('data', {}), args.format))
        return EXIT_SUCCESS
    elif code == '1001' or code == 1001:
        logger.info("NSSET creation started (asynchronous)")
        print("⚠️  Operation started (asynchronous)")
        if args.wait:
            print("Waiting for completion...")
            # Poll nsset-info until NSSET is created
            def check_nsset_created(poll_result: Dict[str, Any]) -> bool:
                """Check if NSSET has been created"""
                poll_response = poll_result.get('response', {})
                poll_code = poll_response.get('code')
                # If we can get NSSET info successfully, it's created
                return poll_code in ['1000', 1000]
            
            # Determine TLD for polling
            tld = args.tld or "cz"
            
            # Poll nsset-info
            final_result = client.poll_until_complete(
                "nsset-info",
                {"name": args.name, "tld": tld},
                is_complete=check_nsset_created,
                max_attempts=60,
                interval=10,
                verbose=not (hasattr(args, 'quiet') and args.quiet)
            )
            
            final_response = final_result.get('response', {})
            final_code = final_response.get('code')
            
            if final_code in ['1000', 1000]:
                logger.info("NSSET created successfully (after polling)")
                print("✅ NSSET created successfully")
                print(format_output(final_response, args.format))
                return EXIT_SUCCESS
            else:
                error_msg = final_response.get('result', 'Timeout or error')
                logger.warning(f"NSSET creation polling completed with warning: {error_msg}")
                print(f"⚠️  {error_msg}", file=sys.stderr)
                print(format_output(response, args.format))
                if 'timeout' in error_msg.lower() or final_code == '9998':
                    raise WAPITimeoutError(f"Polling timeout: {error_msg}")
                return EXIT_SUCCESS
        else:
            print(format_output(response, args.format))
            return EXIT_SUCCESS
    else:
        error_msg = response.get('result', 'Unknown error')
        logger.error(f"Failed to create NSSET: {error_msg} (code: {code})")
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        raise WAPIRequestError(f"Failed to create NSSET: {error_msg} (code: {code})")


def cmd_nsset_info(args, client: WedosAPIClient) -> int:
    """Handle nsset info command"""
    logger = get_logger('commands.nsset')
    logger.info(f"Getting NSSET information for: {args.name}")
    
    # Determine TLD - from argument, domain, or default to 'cz'
    tld = 'cz'  # Default
    
    if hasattr(args, 'tld') and args.tld:
        tld = args.tld
    elif hasattr(args, 'domain') and args.domain:
        # Extract TLD from domain name
        domain_parts = args.domain.split('.')
        if len(domain_parts) > 1:
            tld = domain_parts[-1]
    else:
        # Try to extract from NSSET name (e.g., NS-SPRAVUJU-CZ-...)
        if '-CZ-' in args.name.upper():
            tld = 'cz'
        elif '-COM-' in args.name.upper():
            tld = 'com'
        # Add more TLD detection as needed
    
    # WAPI nsset-info requires 'name' and 'tld' parameters (not 'nsset')
    result = client.call("nsset-info", {"name": args.name, "tld": tld})
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        logger.info(f"NSSET information retrieved successfully for: {args.name}")
        nsset = response.get('data', {}).get('nsset', {})
        print(format_output(nsset, args.format))
        return EXIT_SUCCESS
    
    # If direct call fails, try workaround via domain-info
    error_msg = response.get('result', 'Unknown error')
    
    if hasattr(args, 'domain') and args.domain:
        domain_result = client.domain_info(args.domain)
        domain_code = domain_result.get('response', {}).get('code')
        if domain_code == '1000' or domain_code == 1000:
            domain = domain_result.get('response', {}).get('data', {}).get('domain', {})
            domain_nsset = domain.get('nsset')
            if domain_nsset == args.name:
                # Extract NSSET info from domain response
                dns = domain.get('dns', {})
                nsset_data = {
                    'name': domain_nsset,
                    'dns': dns
                }
                print(format_output(nsset_data, args.format))
                print("\nNote: NSSET information retrieved via domain-info (nsset-info direct call failed).", file=sys.stderr)
                return EXIT_SUCCESS
    
    # If all fails, show error
    logger.error(f"Failed to get NSSET information: {error_msg} (code: {code})")
    print(f"Error ({code}): {error_msg}", file=sys.stderr)
    if hasattr(args, 'domain') and args.domain:
        print(f"\nTip: Try with --domain {args.domain} to use domain-info workaround.", file=sys.stderr)
    else:
        print("\nTip: Use --domain <domain> option to get NSSET info via domain-info.", file=sys.stderr)
    raise WAPIRequestError(f"Failed to get NSSET information: {error_msg} (code: {code})")


def cmd_nsset_list(args, client: WedosAPIClient) -> int:
    """Handle nsset list command"""
    logger = get_logger('commands.nsset')
    # WAPI may not have direct nsset-list command
    # This might need to be implemented differently
    logger.warning("NSSET list command not yet implemented")
    print("Error: NSSET list command not yet implemented", file=sys.stderr)
    print("WAPI may require a different command for listing NSSETs", file=sys.stderr)
    raise WAPIRequestError("NSSET list command not yet implemented")
