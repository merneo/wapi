"""
DNS management commands for WAPI CLI

Handles DNS record operations.
"""

import sys
from typing import List, Dict, Any
from ..api.client import WedosAPIClient
from ..utils.formatters import format_output
from ..utils.validators import validate_domain


def cmd_dns_list(args, client: WedosAPIClient) -> int:
    """Handle dns list command"""
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        return 1
    
    # Get domain info which contains DNS information
    result = client.domain_info(args.domain)
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        domain = response.get('data', {}).get('domain', {})
        dns = domain.get('dns', {})
        
        if isinstance(dns, dict):
            servers = dns.get('server', [])
            if not isinstance(servers, list):
                servers = [servers]
            
            # Format as table
            dns_data = []
            for server in servers:
                if isinstance(server, dict):
                    dns_data.append({
                        'name': server.get('name', ''),
                        'ipv4': server.get('addr_ipv4', ''),
                        'ipv6': server.get('addr_ipv6', '')
                    })
            
            print(format_output(dns_data, args.format, headers=['name', 'ipv4', 'ipv6']))
            return 0
        else:
            print("No DNS information available", file=sys.stderr)
            return 1
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1


def cmd_dns_record_list(args, client: WedosAPIClient) -> int:
    """Handle dns record list command"""
    # This would require dns-rows-list or similar WAPI command
    print("Error: DNS record list command not yet implemented", file=sys.stderr)
    print("WAPI may require dns-rows-list or similar command", file=sys.stderr)
    return 1


def cmd_dns_record_add(args, client: WedosAPIClient) -> int:
    """Handle dns record add command"""
    print("Error: DNS record add command not yet implemented", file=sys.stderr)
    return 1


def cmd_dns_record_delete(args, client: WedosAPIClient) -> int:
    """Handle dns record delete command"""
    print("Error: DNS record delete command not yet implemented", file=sys.stderr)
    return 1
