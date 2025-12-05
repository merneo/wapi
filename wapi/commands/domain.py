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
    # Validate domain name
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        return 1
    
    # This will be implemented in Phase 4
    # For now, return not implemented
    print("Error: Domain update-ns command not yet implemented", file=sys.stderr)
    return 1
