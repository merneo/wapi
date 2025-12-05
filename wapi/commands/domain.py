"""
Domain management commands for WAPI CLI

Handles all domain-related operations.
"""

import sys
from typing import List, Dict, Any, Optional
from ..api.client import WedosAPIClient
from ..utils.formatters import format_output
from ..utils.validators import validate_domain
from ..utils.logger import get_logger


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
    """Handle domain list command"""
    logger = get_logger('commands.domain')
    logger.info("Listing domains")
    
    # WAPI uses 'domains-list' command
    result = client.call("domains-list", {})
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        data = response.get('data', {})
        domains = data.get('domain', [])
        
        if not isinstance(domains, list):
            domains = [domains]
        
        # Format domains
        domain_list = []
        for domain in domains:
            if isinstance(domain, dict):
                domain_list.append({
                    'name': domain.get('name', ''),
                    'status': domain.get('status', ''),
                    'expiration': domain.get('expiration', ''),
                    'nsset': domain.get('nsset', '')
                })
        
        # Filter by TLD if specified
        if hasattr(args, 'tld') and args.tld:
            domain_list = [d for d in domain_list if d['name'].endswith(f'.{args.tld}')]
        
        # Filter by status if specified
        if hasattr(args, 'status') and args.status:
            domain_list = [d for d in domain_list if d['status'] == args.status]
        
        print(format_output(domain_list, args.format, headers=['name', 'status', 'expiration', 'nsset']))
        return 0
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1


def cmd_domain_info(args, client: WedosAPIClient) -> int:
    """Handle domain info command"""
    logger = get_logger('commands.domain')
    logger.info(f"Getting domain information for: {args.domain}")
    
    # Validate domain name
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        logger.warning(f"Invalid domain name: {args.domain} - {error}")
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
    from ..utils.logger import log_operation_start, log_operation_complete
    
    logger = get_logger('commands.domain')
    logger.info(f"Updating nameservers for domain: {args.domain}")
    
    # Validate domain name
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        logger.warning(f"Invalid domain name: {args.domain} - {error}")
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        return 1
    
    # Store options for polling
    nsset_name = None
    nameservers = None
    source_domain = None
    
    # Handle different options
    if args.nsset:
        # Use existing NSSET
        nsset_name = args.nsset
        result = client.domain_update_ns(args.domain, nsset_name=nsset_name)
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
        
        source_domain = args.source_domain
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
            # Poll domain-info until nameservers are updated
            def check_domain_updated(poll_result: Dict[str, Any]) -> bool:
                """Check if domain nameservers have been updated"""
                poll_response = poll_result.get('response', {})
                poll_code = poll_response.get('code')
                if poll_code not in ['1000', 1000]:
                    return False
                
                # Get current domain info
                domain_data = poll_response.get('data', {}).get('domain', {})
                current_nsset = domain_data.get('nsset', '')
                
                # Check if NSSET matches what we tried to set
                if nsset_name:
                    return current_nsset == nsset_name
                elif nameservers:
                    # For new nameservers, check if domain has any NSSET assigned
                    return bool(current_nsset)
                elif source_domain:
                    # For source domain copy, check if nameservers match
                    source_result = client.domain_info(source_domain)
                    if source_result.get('response', {}).get('code') in ['1000', 1000]:
                        source_domain_data = source_result.get('response', {}).get('data', {}).get('domain', {})
                        source_dns = source_domain_data.get('dns', {})
                        target_dns = domain_data.get('dns', {})
                        if isinstance(source_dns, dict) and isinstance(target_dns, dict):
                            source_servers = source_dns.get('server', [])
                            target_servers = target_dns.get('server', [])
                            if isinstance(source_servers, list) and isinstance(target_servers, list):
                                # Compare server names
                                source_names = {s.get('name') for s in source_servers if isinstance(s, dict)}
                                target_names = {s.get('name') for s in target_servers if isinstance(s, dict)}
                                return source_names == target_names
                return False
            
            # Poll domain-info
            final_result = client.poll_until_complete(
                "domain-info",
                {"name": args.domain},
                is_complete=check_domain_updated,
                max_attempts=60,
                interval=10,
                verbose=not (hasattr(args, 'quiet') and args.quiet)
            )
            
            final_response = final_result.get('response', {})
            final_code = final_response.get('code')
            
            if final_code in ['1000', 1000]:
                print("✅ Nameservers updated successfully")
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
