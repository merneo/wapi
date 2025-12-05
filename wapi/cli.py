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
from .commands.config import cmd_config_show, cmd_config_validate, cmd_config_set


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
    
    # NSSET module
    from .commands.nsset import cmd_nsset_create, cmd_nsset_info, cmd_nsset_list
    
    nsset_parser = subparsers.add_parser('nsset', help='NSSET management')
    nsset_subparsers = nsset_parser.add_subparsers(dest='command', help='Command')
    
    create_parser = nsset_subparsers.add_parser('create', help='Create new NSSET')
    create_parser.add_argument('name', help='NSSET name')
    create_parser.add_argument('--nameserver', action='append', required=True,
                              help='Nameserver (name:ipv4:ipv6) - can be used multiple times')
    create_parser.add_argument('--tld', default='cz', help='Top-level domain (default: cz)')
    create_parser.add_argument('--tech-c', dest='tech_c', help='Technical contact handle')
    create_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    create_parser.set_defaults(func=cmd_nsset_create)
    
    nsset_info_parser = nsset_subparsers.add_parser('info', help='Get NSSET information')
    nsset_info_parser.add_argument('name', help='NSSET name')
    nsset_info_parser.add_argument('--tld', help='Top-level domain (auto-detected if not specified)')
    nsset_info_parser.add_argument('--domain', help='Optional: Domain using this NSSET (workaround if direct access fails)')
    nsset_info_parser.set_defaults(func=cmd_nsset_info)
    
    nsset_list_parser = nsset_subparsers.add_parser('list', aliases=['-l'], help='List NSSETs')
    nsset_list_parser.set_defaults(func=cmd_nsset_list)
    
    # Contact module
    from .commands.contact import cmd_contact_info, cmd_contact_list
    
    contact_parser = subparsers.add_parser('contact', help='Contact management')
    contact_subparsers = contact_parser.add_subparsers(dest='command', help='Command')
    
    contact_info_parser = contact_subparsers.add_parser('info', help='Get contact information')
    contact_info_parser.add_argument('handle', help='Contact handle')
    contact_info_parser.add_argument('--tld', default='cz', help='Top-level domain (default: cz)')
    contact_info_parser.set_defaults(func=cmd_contact_info)
    
    contact_list_parser = contact_subparsers.add_parser('list', aliases=['-l'], help='List contacts')
    contact_list_parser.set_defaults(func=cmd_contact_list)
    
    # Config module
    from .commands.config import cmd_config_show, cmd_config_validate, cmd_config_set
    
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='command', help='Command')
    
    config_show_parser = config_subparsers.add_parser('show', help='Show configuration')
    config_show_parser.set_defaults(func=cmd_config_show)
    
    config_validate_parser = config_subparsers.add_parser('validate', help='Validate configuration')
    config_validate_parser.set_defaults(func=cmd_config_validate)
    
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument('key', help='Configuration key')
    config_set_parser.add_argument('value', help='Configuration value')
    config_set_parser.set_defaults(func=cmd_config_set)
    
    # DNS module
    from .commands.dns import cmd_dns_list, cmd_dns_record_list, cmd_dns_record_add, cmd_dns_record_delete
    
    dns_parser = subparsers.add_parser('dns', help='DNS management')
    dns_subparsers = dns_parser.add_subparsers(dest='command', help='Command')
    
    dns_list_parser = dns_subparsers.add_parser('list', aliases=['-l'], help='List nameservers for domain')
    dns_list_parser.add_argument('domain', help='Domain name')
    dns_list_parser.set_defaults(func=cmd_dns_list)
    
    dns_record_list_parser = dns_subparsers.add_parser('records', help='List DNS records')
    dns_record_list_parser.add_argument('domain', help='Domain name')
    dns_record_list_parser.set_defaults(func=cmd_dns_record_list)
    
    dns_record_list_alias = dns_subparsers.add_parser('list-records', help='List DNS records (alias)')
    dns_record_list_alias.add_argument('domain', help='Domain name')
    dns_record_list_alias.set_defaults(func=cmd_dns_record_list)
    
    dns_record_add_parser = dns_subparsers.add_parser('add', help='Add DNS record')
    dns_record_add_parser.add_argument('domain', help='Domain name')
    dns_record_add_parser.add_argument('--name', default='@', help='Record name (default: @)')
    dns_record_add_parser.add_argument('--type', required=True, help='Record type (A, AAAA, MX, CNAME, TXT, etc.)')
    dns_record_add_parser.add_argument('--value', required=True, help='Record value/data')
    dns_record_add_parser.add_argument('--ttl', type=int, default=3600, help='TTL in seconds (default: 3600)')
    dns_record_add_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    dns_record_add_parser.set_defaults(func=cmd_dns_record_add)
    
    dns_record_delete_parser = dns_subparsers.add_parser('delete', help='Delete DNS record')
    dns_record_delete_parser.add_argument('domain', help='Domain name')
    dns_record_delete_parser.add_argument('--id', required=True, help='Record ID (from dns records list)')
    dns_record_delete_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    dns_record_delete_parser.set_defaults(func=cmd_dns_record_delete)
    
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
        # Some commands don't need client (config commands)
        if args.func in [cmd_config_show, cmd_config_validate, cmd_config_set]:
            return args.func(args)
        else:
            return args.func(args, client)
    else:
        print(f"Error: Command not implemented yet", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
