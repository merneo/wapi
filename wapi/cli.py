"""
Main CLI parser and command router for WAPI CLI

Handles command-line argument parsing and routes to appropriate command modules.
"""

import sys
import argparse
from typing import Optional
from .config import load_config, validate_config, get_config
from .api.client import WedosAPIClient
from .utils.formatters import format_output


def get_client(config_file: str = "config.env") -> Optional[WedosAPIClient]:
    """
    Get configured API client.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        WedosAPIClient instance or None if configuration invalid
    """
    is_valid, error = validate_config(config_file)
    if not is_valid:
        print(f"Error: {error}", file=sys.stderr)
        return None
    
    username = get_config('WAPI_USERNAME', config_file=config_file)
    password = get_config('WAPI_PASSWORD', config_file=config_file)
    
    if not username or not password:
        print("Error: WAPI_USERNAME and WAPI_PASSWORD must be set", file=sys.stderr)
        return None
    
    return WedosAPIClient(username, password, use_json=False)


def cmd_ping(args, client: WedosAPIClient):
    """Handle ping command"""
    result = client.ping()
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        output_data = {
            "status": "OK",
            "code": code,
            "result": response.get('result', 'OK')
        }
        print(format_output(output_data, args.format))
        return 0
    else:
        print(f"Error: {response.get('result', 'Unknown error')}", file=sys.stderr)
        return 1


# Import command handlers
from .commands.domain import cmd_domain_info, cmd_domain_list, cmd_domain_update_ns


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='wapi',
        description='WEDOS WAPI Command-Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument('--config', default='config.env', help='Configuration file')
    parser.add_argument('--format', choices=['table', 'json', 'xml', 'yaml'], 
                       default='table', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='module', help='Module')
    
    # Auth module
    auth_parser = subparsers.add_parser('auth', help='Authentication commands')
    auth_subparsers = auth_parser.add_subparsers(dest='command', help='Command')
    
    ping_parser = auth_subparsers.add_parser('ping', help='Test API connection')
    ping_parser.set_defaults(func=cmd_ping)
    
    # Domain module
    domain_parser = subparsers.add_parser('domain', help='Domain management')
    domain_subparsers = domain_parser.add_subparsers(dest='command', help='Command')
    
    info_parser = domain_subparsers.add_parser('info', help='Get domain information')
    info_parser.add_argument('domain', help='Domain name')
    info_parser.set_defaults(func=cmd_domain_info)
    
    list_parser = domain_subparsers.add_parser('list', aliases=['-l'], help='List domains')
    list_parser.set_defaults(func=cmd_domain_list)
    
    update_ns_parser = domain_subparsers.add_parser('update-ns', help='Update domain nameservers')
    update_ns_parser.add_argument('domain', help='Domain name')
    update_ns_parser.add_argument('--nsset', help='Use existing NSSET')
    update_ns_parser.add_argument('--nameserver', action='append', help='Nameserver (name:ipv4:ipv6)')
    update_ns_parser.add_argument('--source-domain', help='Copy nameservers from another domain')
    update_ns_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    update_ns_parser.set_defaults(func=cmd_domain_update_ns)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command
    if not args.module:
        parser.print_help()
        return 1
    
    # Ensure format is available in args (for commands that need it)
    if not hasattr(args, 'format'):
        args.format = 'table'
    
    # Get API client
    client = get_client(args.config)
    if not client:
        return 1
    
    # Execute command
    if hasattr(args, 'func'):
        return args.func(args, client)
    else:
        print(f"Error: Command not implemented yet", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
