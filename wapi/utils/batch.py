"""
Batch operations for WAPI CLI

Provides utilities for performing operations on multiple domains or resources.
"""

import sys
from typing import List, Dict, Any, Callable, Optional

from ..api.client import WedosAPIClient
from ..utils.logger import get_logger


def batch_domain_operation(
    client: WedosAPIClient,
    domains: List[str],
    operation: Callable,
    operation_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Perform an operation on multiple domains.
    
    Args:
        client: WEDOS API client
        domains: List of domain names
        operation: Function to call for each domain
        operation_name: Name of operation (for logging)
        **kwargs: Additional arguments to pass to operation
        
    Returns:
        Dictionary with results for each domain
    """
    logger = get_logger('batch')
    results = {
        'success': [],
        'failed': [],
        'total': len(domains)
    }
    
    logger.info(f"Starting batch {operation_name} for {len(domains)} domains")
    
    for i, domain in enumerate(domains, 1):
        try:
            logger.info(f"Processing domain {i}/{len(domains)}: {domain}")
            result = operation(client, domain, **kwargs)
            results['success'].append({
                'domain': domain,
                'result': result
            })
            print(f"✓ {domain}: Success")
        except Exception as e:
            logger.error(f"Failed to process {domain}: {e}")
            results['failed'].append({
                'domain': domain,
                'error': str(e)
            })
            print(f"✗ {domain}: {e}", file=sys.stderr)
    
    logger.info(f"Batch operation completed: {len(results['success'])} success, {len(results['failed'])} failed")
    
    return results


def batch_dns_operation(
    client: WedosAPIClient,
    domain: str,
    records: List[Dict[str, Any]],
    operation: Callable,
    operation_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Perform an operation on multiple DNS records.
    
    Args:
        client: WEDOS API client
        domain: Domain name
        records: List of DNS record dictionaries
        operation: Function to call for each record
        operation_name: Name of operation (for logging)
        **kwargs: Additional arguments to pass to operation
        
    Returns:
        Dictionary with results for each record
    """
    logger = get_logger('batch')
    results = {
        'success': [],
        'failed': [],
        'total': len(records)
    }
    
    logger.info(f"Starting batch {operation_name} for {len(records)} DNS records on {domain}")
    
    for i, record in enumerate(records, 1):
        try:
            record_info = f"{record.get('name', 'N/A')} {record.get('type', 'N/A')}"
            logger.info(f"Processing record {i}/{len(records)}: {record_info}")
            result = operation(client, domain, record, **kwargs)
            results['success'].append({
                'record': record,
                'result': result
            })
            print(f"✓ {record_info}: Success")
        except Exception as e:
            logger.error(f"Failed to process record {record_info}: {e}")
            results['failed'].append({
                'record': record,
                'error': str(e)
            })
            print(f"✗ {record_info}: {e}", file=sys.stderr)
    
    logger.info(f"Batch operation completed: {len(results['success'])} success, {len(results['failed'])} failed")
    
    return results


def read_domains_from_file(filepath: str) -> List[str]:
    """
    Read domain names from a file (one per line).
    
    Args:
        filepath: Path to file containing domain names
        
    Returns:
        List of domain names
    """
    logger = get_logger('batch')
    domains = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                domain = line.strip()
                if domain and not domain.startswith('#'):
                    domains.append(domain)
        logger.info(f"Read {len(domains)} domains from {filepath}")
    except Exception as e:
        logger.error(f"Failed to read domains from {filepath}: {e}")
        raise
    
    return domains


def write_results_to_file(results: Dict[str, Any], filepath: str, format: str = 'json'):
    """
    Write batch operation results to a file.
    
    Args:
        results: Results dictionary from batch operation
        filepath: Path to output file
        format: Output format ('json', 'yaml', 'csv')
    """
    import json
    import yaml
    
    logger = get_logger('batch')
    
    try:
        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        elif format == 'yaml':
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(results, f, default_flow_style=False)
        elif format == 'csv':
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Domain', 'Status', 'Result/Error'])
                for item in results.get('success', []):
                    writer.writerow([item['domain'], 'Success', str(item.get('result', ''))])
                for item in results.get('failed', []):
                    writer.writerow([item['domain'], 'Failed', item.get('error', '')])
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Results written to {filepath}")
    except Exception as e:
        logger.error(f"Failed to write results to {filepath}: {e}")
        raise
