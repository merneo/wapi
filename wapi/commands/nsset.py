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
    result = client.call("nsset-info", {"name": args.name})
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        nsset = response.get('data', {}).get('nsset', {})
        print(format_output(nsset, args.format))
        return 0
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1


def cmd_nsset_list(args, client: WedosAPIClient) -> int:
    """Handle nsset list command"""
    # WAPI may not have direct nsset-list command
    # This might need to be implemented differently
    print("Error: NSSET list command not yet implemented", file=sys.stderr)
    print("WAPI may require a different command for listing NSSETs", file=sys.stderr)
    return 1
