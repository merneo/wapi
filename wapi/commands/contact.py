"""
Contact management commands for WAPI CLI

Handles all contact-related operations.
"""

import sys
from typing import Dict, Any
from ..api.client import WedosAPIClient
from ..constants import EXIT_SUCCESS, EXIT_ERROR
from ..exceptions import WAPIRequestError
from ..utils.formatters import format_output
from ..utils.logger import get_logger


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
    logger = get_logger('commands.contact')
    logger.info(f"Getting contact information for: {args.handle}")
    
    # Determine TLD - from argument or default to 'cz'
    tld = 'cz'  # Default
    
    if hasattr(args, 'tld') and args.tld:
        tld = args.tld
    else:
        # Try to extract from contact handle (e.g., FORPSI-VVN-S638343)
        # Most CZ contacts don't have TLD in handle, default to cz
        pass
    
    # WAPI contact-info requires 'name' and 'tld' parameters (similar to nsset-info)
    result = client.call("contact-info", {"name": args.handle, "tld": tld})
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        contact = response.get('data', {}).get('contact', {})
        
        # Filter sensitive data
        filtered_contact = filter_sensitive_contact_data(contact)
        
        logger.info(f"Contact information retrieved successfully for: {args.handle}")
        print(format_output(filtered_contact, args.format))
        return EXIT_SUCCESS
    else:
        error_msg = response.get('result', 'Unknown error')
        logger.error(f"Failed to get contact information: {error_msg} (code: {code})")
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        raise WAPIRequestError(f"Failed to get contact information: {error_msg} (code: {code})")


def cmd_contact_list(args, client: WedosAPIClient) -> int:
    """Handle contact list command"""
    logger = get_logger('commands.contact')
    result = client.call("contact-list", {})
    response = result.get('response', {})
    code = response.get('code')
    
    if code in ['1000', 1000]:
        contacts = response.get('data', {}).get('contact', [])
        if not isinstance(contacts, list):
            contacts = [contacts]
        filtered = [filter_sensitive_contact_data(c) for c in contacts if isinstance(c, dict)]
        print(format_output(filtered, args.format))
        logger.info(f"Listed {len(filtered)} contact(s)")
        return EXIT_SUCCESS
    
    error_msg = response.get('result', 'Contact list command not yet implemented')
    logger.warning(f"Failed to list contacts: {error_msg} (code: {code})")
    print(f"Error: Contact list failed - {error_msg}", file=sys.stderr)
    raise WAPIRequestError("Contact list command not yet implemented")
