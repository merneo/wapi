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
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        return 1
    
    # Use dns-rows-list WAPI command
    result = client.call("dns-rows-list", {"domain": args.domain})
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        data = response.get('data', {})
        rows = data.get('row', [])
        
        if not isinstance(rows, list):
            rows = [rows]
        
        # Format DNS records
        records = []
        for row in rows:
            if isinstance(row, dict):
                records.append({
                    'id': row.get('ID', ''),
                    'name': row.get('name', ''),
                    'ttl': row.get('ttl', ''),
                    'type': row.get('rdtype', ''),
                    'rdata': row.get('rdata', '')
                })
        
        print(format_output(records, args.format, headers=['id', 'name', 'ttl', 'type', 'rdata']))
        return 0
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1


def cmd_dns_record_add(args, client: WedosAPIClient) -> int:
    """Handle dns record add command"""
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        return 1
    
    # Build DNS record data
    record_data = {
        "domain": args.domain,
        "name": args.name or "@",
        "ttl": args.ttl or 3600,
        "rdtype": args.type.upper(),
        "rdata": args.value
    }
    
    # Call API
    result = client.call("dns-row-add", record_data)
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        print("✅ DNS record added successfully")
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


def cmd_dns_record_delete(args, client: WedosAPIClient) -> int:
    """Handle dns record delete command"""
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        return 1
    
    if not args.id:
        print("Error: Record ID required (--id)", file=sys.stderr)
        return 1
    
    # Build delete data
    delete_data = {
        "domain": args.domain,
        "row_id": args.id
    }
    
    # Call API
    result = client.call("dns-row-delete", delete_data)
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        print("✅ DNS record deleted successfully")
        return 0
    elif code == '1001' or code == 1001:
        print("⚠️  Operation started (asynchronous)")
        if args.wait:
            print("Waiting for completion...")
            # TODO: Implement polling
        return 0
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1
