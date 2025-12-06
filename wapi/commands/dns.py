"""
DNS management commands for WAPI CLI

Handles DNS record operations.
"""

import sys
from typing import Any, Dict, List

from ..api.client import WedosAPIClient
from ..constants import EXIT_SUCCESS, EXIT_ERROR, EXIT_VALIDATION_ERROR
from ..exceptions import (
    WAPIValidationError,
    WAPIRequestError,
    WAPITimeoutError,
)
from ..utils.formatters import format_output
from ..utils.logger import get_logger
from ..utils.validators import validate_domain


def cmd_dns_list(args, client: WedosAPIClient) -> int:
    """Handle dns list command"""
    logger = get_logger('commands.dns')
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        logger.warning(f"Invalid domain name: {args.domain} - {error}")
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        raise WAPIValidationError(f"Invalid domain name: {error}")
    
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
            
            logger.info(f"Listed {len(dns_data)} nameserver(s) for {args.domain}")
            print(format_output(dns_data, args.format, headers=['name', 'ipv4', 'ipv6']))
            return EXIT_SUCCESS
        else:
            logger.warning(f"No DNS information available for {args.domain}")
            print("No DNS information available", file=sys.stderr)
            raise WAPIRequestError(f"No DNS information available for {args.domain}")
    else:
        error_msg = response.get('result', 'Unknown error')
        logger.error(f"Failed to list nameservers: {error_msg} (code: {code})")
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        raise WAPIRequestError(f"Failed to list nameservers: {error_msg} (code: {code})")


def cmd_dns_record_list(args, client: WedosAPIClient) -> int:
    """Handle dns record list command"""
    logger = get_logger('commands.dns')
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        logger.warning(f"Invalid domain name: {args.domain} - {error}")
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        raise WAPIValidationError(f"Invalid domain name: {error}")
    
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
        
        logger.info(f"Listed {len(records)} DNS record(s) for {args.domain}")
        print(format_output(records, args.format, headers=['id', 'name', 'ttl', 'type', 'rdata']))
        return EXIT_SUCCESS
    else:
        error_msg = response.get('result', 'Unknown error')
        logger.error(f"Failed to list DNS records: {error_msg} (code: {code})")
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        raise WAPIRequestError(f"Failed to list DNS records: {error_msg} (code: {code})")


def cmd_dns_record_add(args, client: WedosAPIClient) -> int:
    """Handle dns record add command"""
    logger = get_logger('commands.dns')
    logger.info(f"Adding DNS record for {args.domain}: {args.type} {args.name or '@'} = {args.value}")
    
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        logger.warning(f"Invalid domain name: {args.domain} - {error}")
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        raise WAPIValidationError(f"Invalid domain name: {error}")
    
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
        logger.info("DNS record added successfully")
        print("✅ DNS record added successfully")
        print(format_output(response.get('data', {}), args.format))
        return EXIT_SUCCESS
    elif code == '1001' or code == 1001:
        logger.info("DNS record add started (asynchronous)")
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
                logger.info("DNS record added successfully (after polling)")
                print("✅ DNS record added successfully")
                print(format_output(final_response, args.format))
                return EXIT_SUCCESS
            else:
                error_msg = final_response.get('result', 'Timeout or error')
                logger.warning(f"DNS add polling completed with warning: {error_msg}")
                print(f"⚠️  {error_msg}", file=sys.stderr)
                print(format_output(response, args.format))
                if 'timeout' in error_msg.lower() or final_code == '9998':
                    raise WAPITimeoutError(f"Polling timeout: {error_msg}")
                return EXIT_SUCCESS
        else:
            print(format_output(response, args.format))
            return EXIT_SUCCESS
    else:
        error_msg = response.get('result', 'Unknown error')
        logger.error(f"Failed to add DNS record: {error_msg} (code: {code})")
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        raise WAPIRequestError(f"Failed to add DNS record: {error_msg} (code: {code})")


def cmd_dns_record_update(args, client: WedosAPIClient) -> int:
    """Handle dns record update command"""
    logger = get_logger('commands.dns')
    update_fields = [k for k in ['name', 'type', 'value', 'ttl'] if getattr(args, k, None)]
    logger.info(f"Updating DNS record {args.id} for {args.domain}: {', '.join(update_fields)}")
    
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        logger.warning(f"Invalid domain name: {args.domain} - {error}")
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        raise WAPIValidationError(f"Invalid domain name: {error}")
    
    if not args.id:
        logger.error("Record ID required")
        print("Error: Record ID required (--id)", file=sys.stderr)
        raise WAPIValidationError("Record ID required (--id)")
    
    # Check that at least one field is being updated
    if not any([args.name, args.type, args.value, args.ttl]):
        logger.error("At least one field must be specified for update")
        print("Error: At least one field must be specified for update (--name, --type, --value, or --ttl)", file=sys.stderr)
        raise WAPIValidationError("At least one field must be specified for update")
    
    # Build update data - WAPI uses dns-row-update command
    update_data = {
        "domain": args.domain,
        "row_id": args.id
    }
    
    # Add optional fields if provided
    if args.name:
        update_data["name"] = args.name
    if args.type:
        update_data["rdtype"] = args.type.upper()
    if args.value:
        update_data["rdata"] = args.value
    if args.ttl:
        update_data["ttl"] = args.ttl
    
    # Call API
    result = client.call("dns-row-update", update_data)
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        logger.info("DNS record updated successfully")
        print("✅ DNS record updated successfully")
        print(format_output(response.get('data', {}), args.format))
        return EXIT_SUCCESS
    elif code == '1001' or code == 1001:
        logger.info("DNS record update started (asynchronous)")
        print("⚠️  Operation started (asynchronous)")
        if args.wait:
            print("Waiting for completion...")
            # Poll dns-rows-list until record is updated
            record_id = args.id
            expected_name = args.name
            expected_type = args.type.upper() if args.type else None
            expected_value = args.value
            
            def check_record_updated(poll_result: Dict[str, Any]) -> bool:
                """Check if DNS record has been updated"""
                poll_response = poll_result.get('response', {})
                poll_code = poll_response.get('code')
                if poll_code not in ['1000', 1000]:
                    return False
                
                # Check if record exists with updated values
                data = poll_response.get('data', {})
                rows = data.get('row', [])
                if not isinstance(rows, list):
                    rows = [rows]
                
                for row in rows:
                    if isinstance(row, dict) and str(row.get('ID', '')) == str(record_id):
                        # Found the record, check if values match
                        if expected_name and row.get('name', '') != expected_name:
                            return False
                        if expected_type and row.get('rdtype', '').upper() != expected_type:
                            return False
                        if expected_value and row.get('rdata', '') != expected_value:
                            return False
                        return True  # Record found and matches
                return False  # Record not found
            
            # Poll dns-rows-list
            final_result = client.poll_until_complete(
                "dns-rows-list",
                {"domain": args.domain},
                is_complete=check_record_updated,
                max_attempts=60,
                interval=10,
                verbose=not (hasattr(args, 'quiet') and args.quiet)
            )
            
            final_response = final_result.get('response', {})
            final_code = final_response.get('code')
            
            if final_code in ['1000', 1000]:
                logger.info("DNS record updated successfully (after polling)")
                print("✅ DNS record updated successfully")
                print(format_output(final_response, args.format))
                return EXIT_SUCCESS
            else:
                error_msg = final_response.get('result', 'Timeout or error')
                logger.warning(f"DNS update polling completed with warning: {error_msg}")
                print(f"⚠️  {error_msg}", file=sys.stderr)
                print(format_output(response, args.format))
                if 'timeout' in error_msg.lower() or final_code == '9998':
                    raise WAPITimeoutError(f"Polling timeout: {error_msg}")
                return EXIT_SUCCESS
        else:
            print(format_output(response, args.format))
            return EXIT_SUCCESS
    else:
        error_msg = response.get('result', 'Unknown error')
        logger.error(f"Failed to update DNS record: {error_msg} (code: {code})")
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        raise WAPIRequestError(f"Failed to update DNS record: {error_msg} (code: {code})")


def cmd_dns_record_delete(args, client: WedosAPIClient) -> int:
    """Handle dns record delete command"""
    logger = get_logger('commands.dns')
    logger.info(f"Deleting DNS record {args.id} for {args.domain}")
    
    # Validate domain
    is_valid, error = validate_domain(args.domain)
    if not is_valid:
        logger.warning(f"Invalid domain name: {args.domain} - {error}")
        print(f"Error: Invalid domain name - {error}", file=sys.stderr)
        raise WAPIValidationError(f"Invalid domain name: {error}")
    
    if not args.id:
        logger.error("Record ID required")
        print("Error: Record ID required (--id)", file=sys.stderr)
        raise WAPIValidationError("Record ID required (--id)")
    
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
        logger.info("DNS record deleted successfully")
        print("✅ DNS record deleted successfully")
        return EXIT_SUCCESS
    elif code == '1001' or code == 1001:
        logger.info("DNS record delete started (asynchronous)")
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
                logger.info("DNS record deleted successfully (after polling)")
                print("✅ DNS record deleted successfully")
                return EXIT_SUCCESS
            else:
                error_msg = final_response.get('result', 'Timeout or error')
                logger.warning(f"DNS delete polling completed with warning: {error_msg}")
                print(f"⚠️  {error_msg}", file=sys.stderr)
                if 'timeout' in error_msg.lower() or final_code == '9998':
                    raise WAPITimeoutError(f"Polling timeout: {error_msg}")
                return EXIT_SUCCESS
        else:
            return EXIT_SUCCESS
    else:
        error_msg = response.get('result', 'Unknown error')
        logger.error(f"Failed to delete DNS record: {error_msg} (code: {code})")
        print(f"Error ({code}): {error_msg}", file=sys.stderr)
        raise WAPIRequestError(f"Failed to delete DNS record: {error_msg} (code: {code})")
