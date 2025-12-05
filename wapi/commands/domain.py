"""
Domain management commands for WAPI CLI

Handles all domain-related operations.
"""

import sys
from typing import List, Dict, Any, Optional
from ..api.client import WedosAPIClient
from ..utils.formatters import format_output
from ..utils.validators import validate_domain


def filter_sensitive_domain_data(domain: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter out sensitive data from domain information.
    
    Args:
        domain: Domain data dictionary
        
    Returns:
        Filtered domain data without sensitive information
    """
    # Fields to hide or sanitize
    sensitive_fields = [
        'own_email', 'own_email2', 'own_phone', 'own_fax', 
        'own_dic', 'own_ic', 'own_other', 'own_addr_street',
        'own_addr_city', 'own_addr_zip', 'own_name', 'own_fname', 'own_lname'
    ]
    
    filtered = domain.copy()
    for field in sensitive_fields:
        if field in filtered:
            filtered[field] = '[HIDDEN]'
    
    return filtered


def cmd_domain_list(args, client: WedosAPIClient) -> int:
    """
    Handle domain list command.
    
    Note: WAPI may not have a direct 'domain-list' command.
    This would need to be implemented based on available WAPI commands.
    """
    # TODO: Implement domain list when WAPI command is available
    print("Error: Domain list command not yet implemented", file=sys.stderr)
    print("WAPI may require a different command for listing domains", file=sys.stderr)
    return 1


def cmd_domain_info(args, client: WedosAPIClient) -> int:
    """Handle domain info command"""
    # Validate domain name
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        return 1
    
    # Get domain information
    result = client.domain_info(args.domain)
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        domain = response.get('data', {}).get('domain', {})
        
        # Filter sensitive data
        filtered_domain = filter_sensitive_domain_data(domain)
        
        # Format output
        print(format_output(filtered_domain, args.format))
        return 0
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1


def cmd_domain_update_ns(args, client: WedosAPIClient) -> int:
    """Handle domain update-ns command"""
    from ..utils.validators import validate_nameserver
    
    # Validate domain name
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        return 1
    
    # Handle different options
    if args.nsset:
        # Use existing NSSET
        result = client.domain_update_ns(args.domain, nsset_name=args.nsset)
    elif args.nameserver:
        # Parse nameservers
        nameservers = []
        for ns_string in args.nameserver:
            is_valid_ns, parsed, error = validate_nameserver(ns_string)
            if not is_valid_ns:
                print(f"Error: Invalid nameserver format - {error}", file=sys.stderr)
                return 1
            nameservers.append(parsed)
        
        result = client.domain_update_ns(args.domain, nameservers=nameservers)
    elif args.source_domain:
        # Get nameservers from source domain
        source_result = client.domain_info(args.source_domain)
        source_code = source_result.get('response', {}).get('code')
        
        if source_code != '1000' and source_code != 1000:
            print(f"Error: Could not get information for {args.source_domain}", file=sys.stderr)
            return 1
        
        source_domain = source_result.get('response', {}).get('data', {}).get('domain', {})
        dns = source_domain.get('dns', {})
        
        if not isinstance(dns, dict):
            print(f"Error: No nameservers found for {args.source_domain}", file=sys.stderr)
            return 1
        
        servers = dns.get('server', [])
        if not isinstance(servers, list):
            servers = [servers]
        
        if not servers:
            print(f"Error: No nameservers found for {args.source_domain}", file=sys.stderr)
            return 1
        
        # Extract nameservers and replace domain in nameserver names
        nameservers = []
        target_tld = args.domain.split('.')[-1] if '.' in args.domain else args.domain
        source_tld = args.source_domain.split('.')[-1] if '.' in args.source_domain else args.source_domain
        
        for server in servers:
            if isinstance(server, dict):
                ns_name = server.get('name', '')
                # Replace source domain with target domain if same TLD
                if source_tld == target_tld:
                    new_ns_name = ns_name.replace(args.source_domain, args.domain)
                else:
                    new_ns_name = ns_name
                
                nameservers.append({
                    'name': new_ns_name,
                    'addr_ipv4': server.get('addr_ipv4', ''),
                    'addr_ipv6': server.get('addr_ipv6', '')
                })
        
        result = client.domain_update_ns(args.domain, nameservers=nameservers)
    else:
        print("Error: Must specify --nsset, --nameserver, or --source-domain", file=sys.stderr)
        return 1
    
    # Check result
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        print("✅ Nameservers updated successfully")
        print(format_output(response, args.format))
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
