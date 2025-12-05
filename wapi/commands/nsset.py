"""
NSSET management commands for WAPI CLI

Handles all NSSET-related operations.
"""

import sys
from typing import List, Dict, Any, Optional
from ..api.client import WedosAPIClient
from ..utils.formatters import format_output
from ..utils.validators import validate_nameserver


def cmd_nsset_create(args, client: WedosAPIClient) -> int:
    """Handle nsset create command"""
    # Validate nameservers
    if not args.nameserver:
        print("Error: At least one nameserver required (--nameserver)", file=sys.stderr)
        return 1
    
    nameservers = []
    for ns_string in args.nameserver:
        is_valid, parsed, error = validate_nameserver(ns_string)
        if not is_valid:
            print(f"Error: Invalid nameserver format - {error}", file=sys.stderr)
            return 1
        nameservers.append(parsed)
    
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
        print("✅ NSSET created successfully")
        print(format_output(response.get('data', {}), args.format))
        return 0
    elif code == '1001' or code == 1001:
        print("⚠️  Operation started (asynchronous)")
        if args.wait:
            print("Waiting for completion...")
            # TODO: Implement polling
        print(format_output(response, args.format))
        return 0
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1


def cmd_nsset_info(args, client: WedosAPIClient) -> int:
    """Handle nsset info command"""
    # Try nsset-info command first
    result = client.call("nsset-info", {"nsset": args.name})
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        nsset = response.get('data', {}).get('nsset', {})
        print(format_output(nsset, args.format))
        return 0
    
    # If direct nsset-info fails, try alternative: get info from domain using this NSSET
    # This is a workaround since nsset-info may have access restrictions
    error_msg = response.get('result', 'Unknown error')
    
    # Try to find a domain using this NSSET (if domain name provided as alternative)
    if hasattr(args, 'domain') and args.domain:
        domain_result = client.domain_info(args.domain)
        domain_code = domain_result.get('response', {}).get('code')
        if domain_code == '1000' or domain_code == 1000:
            domain = domain_result.get('response', {}).get('data', {}).get('domain', {})
            domain_nsset = domain.get('nsset')
            if domain_nsset == args.name:
                # Found domain using this NSSET - extract NSSET info from domain response
                dns = domain.get('dns', {})
                nsset_data = {
                    'name': domain_nsset,
                    'dns': dns
                }
                print(format_output(nsset_data, args.format))
                print("\nNote: NSSET information retrieved via domain-info (nsset-info may have access restrictions).", file=sys.stderr)
                return 0
    
    # If all fails, show error
    print(f"Error ({code}): {error_msg}", file=sys.stderr)
    print("\nNote: nsset-info may require the NSSET to be accessible to your account.", file=sys.stderr)
    print("Alternative: Use 'wapi domain info <domain>' to get NSSET information for domains using this NSSET.", file=sys.stderr)
    return 1


def cmd_nsset_list(args, client: WedosAPIClient) -> int:
    """Handle nsset list command"""
    # WAPI may not have direct nsset-list command
    # This might need to be implemented differently
    print("Error: NSSET list command not yet implemented", file=sys.stderr)
    print("WAPI may require a different command for listing NSSETs", file=sys.stderr)
    return 1
