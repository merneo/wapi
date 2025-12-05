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
            # Poll dns-rows-list until record appears
            record_name = args.name or "@"
            record_type = args.type.upper()
            record_value = args.value
            
            def check_record_added(poll_result: Dict[str, Any]) -> bool:
                """Check if DNS record has been added"""
                poll_response = poll_result.get('response', {})
                poll_code = poll_response.get('code')
                if poll_code not in ['1000', 1000]:
                    return False
                
                # Check if record exists in list
                data = poll_response.get('data', {})
                rows = data.get('row', [])
                if not isinstance(rows, list):
                    rows = [rows]
                
                for row in rows:
                    if isinstance(row, dict):
                        if (row.get('name', '') == record_name and
                            row.get('rdtype', '').upper() == record_type and
                            row.get('rdata', '') == record_value):
                            return True
                return False
            
            # Poll dns-rows-list
            final_result = client.poll_until_complete(
                "dns-rows-list",
                {"domain": args.domain},
                is_complete=check_record_added,
                max_attempts=60,
                interval=10,
                verbose=not (hasattr(args, 'quiet') and args.quiet)
            )
            
            final_response = final_result.get('response', {})
            final_code = final_response.get('code')
            
            if final_code in ['1000', 1000]:
                print("✅ DNS record added successfully")
                print(format_output(final_response, args.format))
                return 0
            else:
                error_msg = final_response.get('result', 'Timeout or error')
                print(f"⚠️  {error_msg}", file=sys.stderr)
                print(format_output(response, args.format))
                return 0
        else:
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
            # Poll dns-rows-list until record is deleted
            record_id = args.id
            
            def check_record_deleted(poll_result: Dict[str, Any]) -> bool:
                """Check if DNS record has been deleted"""
                poll_response = poll_result.get('response', {})
                poll_code = poll_response.get('code')
                if poll_code not in ['1000', 1000]:
                    return False
                
                # Check if record no longer exists in list
                data = poll_response.get('data', {})
                rows = data.get('row', [])
                if not isinstance(rows, list):
                    rows = [rows]
                
                for row in rows:
                    if isinstance(row, dict):
                        if str(row.get('ID', '')) == str(record_id):
                            return False  # Still exists
                return True  # Record not found, deleted
            
            # Poll dns-rows-list
            final_result = client.poll_until_complete(
                "dns-rows-list",
                {"domain": args.domain},
                is_complete=check_record_deleted,
                max_attempts=60,
                interval=10,
                verbose=not (hasattr(args, 'quiet') and args.quiet)
            )
            
            final_response = final_result.get('response', {})
            final_code = final_response.get('code')
            
            if final_code in ['1000', 1000]:
                print("✅ DNS record deleted successfully")
                return 0
            else:
                error_msg = final_response.get('result', 'Timeout or error')
                print(f"⚠️  {error_msg}", file=sys.stderr)
                return 0
        else:
            return 0
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1
