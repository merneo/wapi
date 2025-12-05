"""
Contact management commands for WAPI CLI

Handles all contact-related operations.
"""

import sys
from typing import Dict, Any
from ..api.client import WedosAPIClient
from ..utils.formatters import format_output


def filter_sensitive_contact_data(contact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter out sensitive data from contact information.
    
    Args:
        contact: Contact data dictionary
        
    Returns:
        Filtered contact data without sensitive information
    """
    sensitive_fields = [
        'email', 'email2', 'phone', 'fax', 'ident', 'ident_type',
        'addr_street', 'addr_city', 'addr_zip', 'notify_email'
    ]
    
    filtered = contact.copy()
    for field in sensitive_fields:
        if field in filtered:
            filtered[field] = '[HIDDEN]'
    
    return filtered


def cmd_contact_info(args, client: WedosAPIClient) -> int:
    """Handle contact info command"""
    # Try different parameter formats
    result = client.call("contact-info", {"contact": args.handle})
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        contact = response.get('data', {}).get('contact', {})
        
        # Filter sensitive data
        filtered_contact = filter_sensitive_contact_data(contact)
        
        print(format_output(filtered_contact, args.format))
        return 0
    else:
        error_msg = response.get('result', 'Unknown error')
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        return 1


def cmd_contact_list(args, client: WedosAPIClient) -> int:
    """Handle contact list command"""
    # WAPI may not have direct contact-list command
    print("Error: Contact list command not yet implemented", file=sys.stderr)
    print("WAPI may require a different command for listing contacts", file=sys.stderr)
    return 1
