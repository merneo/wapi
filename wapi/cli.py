"""
Main CLI parser and command router for WAPI CLI

Handles command-line argument parsing and routes to appropriate command modules.
"""

import argparse
import sys
from typing import Optional

from .api.client import WedosAPIClient
from .config import get_config, load_config, validate_config
from .constants import (
    EXIT_ERROR,
    EXIT_SUCCESS,
    EXIT_CONFIG_ERROR,
    EXIT_AUTH_ERROR,
    EXIT_CONNECTION_ERROR,
    EXIT_TIMEOUT_ERROR,
)
from .exceptions import (
    WAPIConfigurationError,
    WAPIAuthenticationError,
    WAPIConnectionError,
    WAPITimeoutError,
    WAPIRequestError,
    WAPIError,
)
from .utils.formatters import format_output
from .utils.logger import get_logger, setup_logging
from .utils.aliases import expand_alias, list_aliases
from .utils.interactive import start_interactive_mode
from .utils.config_wizard import run_config_wizard
from .commands.search import cmd_search


def get_client(config_file: str = "config.env") -> Optional[WedosAPIClient]:
    """
    Get configured API client.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        WedosAPIClient instance or None if configuration invalid
    """
    logger = get_logger('cli')
    
    try:
        is_valid, error = validate_config(config_file)
        if not is_valid:
            logger.error(f"Configuration validation failed: {error}")
            print(f"Error: {error}", file=sys.stderr)
            return None
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: Configuration error - {e}", file=sys.stderr)
        return None
    
    username = get_config('WAPI_USERNAME', config_file=config_file)
    password = get_config('WAPI_PASSWORD', config_file=config_file)
    
    if not username or not password:
        logger.error("Missing WAPI credentials")
        print("Error: WAPI_USERNAME and WAPI_PASSWORD must be set", file=sys.stderr)
        return None
    
    logger.debug("API client credentials loaded successfully")
    return WedosAPIClient(username, password, use_json=False)


def cmd_ping(args, client: WedosAPIClient):
    """Handle ping command"""
    logger = get_logger('commands.auth')
    logger.info("Testing API connection (ping)")
    
    result = client.ping()
    response = result.get('response', {})
    code = response.get('code')
    
    if code == '1000' or code == 1000:
        logger.info("API connection successful")
        output_data = {
            "status": "OK",
            "code": code,
            "result": response.get('result', 'OK')
        }
        print(format_output(output_data, args.format))
        return EXIT_SUCCESS
    else:
        error_msg = response.get('result', 'Unknown error')
        logger.error(f"API connection failed: {error_msg}")
        print(f"Error: {error_msg}", file=sys.stderr)
        return EXIT_ERROR


# Import auth command handlers
from .commands.auth import cmd_auth_login, cmd_auth_logout, cmd_auth_status


# Import command handlers
from .commands.domain import (
    cmd_domain_info, cmd_domain_list, cmd_domain_update_ns,
    cmd_domain_create, cmd_domain_transfer, cmd_domain_renew,
    cmd_domain_delete, cmd_domain_update
)
from .commands.config import cmd_config_show, cmd_config_validate, cmd_config_set
from .commands.dns import cmd_dns_list, cmd_dns_record_list, cmd_dns_record_add, cmd_dns_record_update, cmd_dns_record_delete


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
    parser.add_argument('--log-file', help='Log file path (optional)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Log level (overrides --verbose/--quiet)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive mode (REPL)')
    parser.add_argument('--aliases', action='store_true',
                       help='Show available command aliases')
    parser.add_argument('--wizard', action='store_true',
                       help='Run configuration wizard for first-time setup')
    parser.add_argument('-s', '--search', dest='search_domain',
                       help='Check domain availability (alias for search command)')
    parser.add_argument('--search-whois-server', help='Override WHOIS server for --search alias')
    parser.add_argument('--search-whois-timeout', type=int, default=10,
                       help='WHOIS timeout (seconds) for --search alias')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='module', help='Module')
    
    # Auth module
    auth_parser = subparsers.add_parser('auth', help='Authentication commands')
    auth_subparsers = auth_parser.add_subparsers(dest='command', help='Command')
    
    ping_parser = auth_subparsers.add_parser('ping', help='Test API connection')
    ping_parser.set_defaults(func=cmd_ping)
    
    login_parser = auth_subparsers.add_parser('login', help='Interactive login (save credentials)')
    login_parser.add_argument('--username', help='Username (email) - if not provided, will prompt')
    login_parser.add_argument('--password', help='Password - if not provided, will prompt securely')
    login_parser.set_defaults(func=cmd_auth_login)
    
    logout_parser = auth_subparsers.add_parser('logout', help='Remove saved credentials')
    logout_parser.set_defaults(func=cmd_auth_logout)
    
    status_parser = auth_subparsers.add_parser('status', help='Show authentication status')
    status_parser.set_defaults(func=cmd_auth_status)
    
    # Domain module
    domain_parser = subparsers.add_parser('domain', help='Domain management')
    domain_subparsers = domain_parser.add_subparsers(dest='command', help='Command')
    
    info_parser = domain_subparsers.add_parser('info', help='Get domain information')
    info_parser.add_argument('domain', help='Domain name')
    info_parser.set_defaults(func=cmd_domain_info)
    
    list_parser = domain_subparsers.add_parser('list', aliases=['-l'], help='List domains')
    list_parser.add_argument('--tld', help='Filter by TLD (e.g., cz, com)')
    list_parser.add_argument('--status', help='Filter by status (e.g., ok, expired)')
    list_parser.set_defaults(func=cmd_domain_list)
    
    update_ns_parser = domain_subparsers.add_parser('update-ns', help='Update domain nameservers')
    update_ns_parser.add_argument('domain', help='Domain name')
    update_ns_parser.add_argument('--nsset', help='Use existing NSSET')
    update_ns_parser.add_argument('--nameserver', action='append', help='Nameserver (name:ipv4:ipv6 or name:ipv4)')
    update_ns_parser.add_argument('--source-domain', help='Copy nameservers from another domain')
    update_ns_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    update_ns_parser.add_argument('--no-ipv6-discovery', action='store_true', 
                                 help='Disable automatic IPv6 address discovery for nameservers')
    update_ns_parser.set_defaults(func=cmd_domain_update_ns)
    
    create_parser = domain_subparsers.add_parser('create', help='Register new domain')
    create_parser.add_argument('domain', help='Domain name to register')
    create_parser.add_argument('--period', type=int, default=1, help='Registration period in years (default: 1)')
    create_parser.add_argument('--owner-c', dest='owner_c', help='Owner contact handle')
    create_parser.add_argument('--admin-c', dest='admin_c', help='Admin contact handle')
    create_parser.add_argument('--nsset', help='NSSET name to assign')
    create_parser.add_argument('--keyset', help='KEYSET name to assign (for DNSSEC)')
    create_parser.add_argument('--auth-info', dest='auth_info', help='Authorization code (for some TLDs)')
    create_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    create_parser.set_defaults(func=cmd_domain_create)
    
    transfer_parser = domain_subparsers.add_parser('transfer', help='Transfer domain from another registrar')
    transfer_parser.add_argument('domain', help='Domain name to transfer')
    transfer_parser.add_argument('--auth-info', dest='auth_info', required=True, 
                                help='Authorization code (EPP code) - required')
    transfer_parser.add_argument('--period', type=int, default=1, help='Registration period in years (default: 1)')
    transfer_parser.set_defaults(func=cmd_domain_transfer)
    
    renew_parser = domain_subparsers.add_parser('renew', help='Renew domain registration')
    renew_parser.add_argument('domain', help='Domain name to renew')
    renew_parser.add_argument('--period', type=int, default=1, help='Renewal period in years (default: 1)')
    renew_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    renew_parser.set_defaults(func=cmd_domain_renew)
    
    delete_parser = domain_subparsers.add_parser('delete', help='Delete domain registration')
    delete_parser.add_argument('domain', help='Domain name to delete')
    delete_parser.add_argument('--force', action='store_true', 
                              help='Force deletion without confirmation (required)')
    delete_parser.add_argument('--delete-after', dest='delete_after', 
                              help='Delete after date (YYYY-MM-DD format)')
    delete_parser.set_defaults(func=cmd_domain_delete)
    
    update_parser = domain_subparsers.add_parser('update', help='Update domain information')
    update_parser.add_argument('domain', help='Domain name')
    update_parser.add_argument('--owner-c', dest='owner_c', help='Owner contact handle')
    update_parser.add_argument('--admin-c', dest='admin_c', help='Admin contact handle')
    update_parser.add_argument('--tech-c', dest='tech_c', help='Technical contact handle')
    update_parser.add_argument('--nsset', help='NSSET name to assign')
    update_parser.add_argument('--keyset', help='KEYSET name to assign (for DNSSEC)')
    update_parser.add_argument('--auth-info', dest='auth_info', help='Authorization code')
    update_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    update_parser.set_defaults(func=cmd_domain_update)

    # Search module (single command)
    search_parser = subparsers.add_parser('search', help='Search domain availability and WHOIS')
    search_parser.add_argument('domain', help='Domain name to search')
    search_parser.add_argument('--whois-server', help='Override WHOIS server (optional)')
    search_parser.add_argument('--whois-timeout', type=int, default=10, help='WHOIS socket timeout in seconds')
    search_parser.set_defaults(func=cmd_search)
    
    # NSSET module
    from .commands.nsset import cmd_nsset_create, cmd_nsset_info, cmd_nsset_list
    
    nsset_parser = subparsers.add_parser('nsset', help='NSSET management')
    nsset_subparsers = nsset_parser.add_subparsers(dest='command', help='Command')
    
    create_parser = nsset_subparsers.add_parser('create', help='Create new NSSET')
    create_parser.add_argument('name', help='NSSET name')
    create_parser.add_argument('--nameserver', action='append', required=True,
                              help='Nameserver (name:ipv4:ipv6 or name:ipv4) - can be used multiple times')
    create_parser.add_argument('--tld', default='cz', help='Top-level domain (default: cz)')
    create_parser.add_argument('--tech-c', dest='tech_c', help='Technical contact handle')
    create_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    create_parser.add_argument('--no-ipv6-discovery', action='store_true',
                              help='Disable automatic IPv6 address discovery for nameservers')
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
    from .commands.dns import cmd_dns_list, cmd_dns_record_list, cmd_dns_record_add, cmd_dns_record_update, cmd_dns_record_delete
    
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
    
    dns_record_update_parser = dns_subparsers.add_parser('update', help='Update DNS record')
    dns_record_update_parser.add_argument('domain', help='Domain name')
    dns_record_update_parser.add_argument('--id', required=True, help='Record ID (from dns records list)')
    dns_record_update_parser.add_argument('--name', help='Record name (e.g., @, www)')
    dns_record_update_parser.add_argument('--type', help='Record type (A, AAAA, MX, CNAME, TXT, etc.)')
    dns_record_update_parser.add_argument('--value', help='Record value/data')
    dns_record_update_parser.add_argument('--ttl', type=int, help='TTL in seconds')
    dns_record_update_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    dns_record_update_parser.set_defaults(func=cmd_dns_record_update)
    
    dns_record_delete_parser = dns_subparsers.add_parser('delete', help='Delete DNS record')
    dns_record_delete_parser.add_argument('domain', help='Domain name')
    dns_record_delete_parser.add_argument('--id', required=True, help='Record ID (from dns records list)')
    dns_record_delete_parser.add_argument('--wait', action='store_true', help='Wait for async completion')
    dns_record_delete_parser.set_defaults(func=cmd_dns_record_delete)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging first (before any other operations)
    logger = setup_logging(
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=getattr(args, 'log_file', None),
        log_level=getattr(args, 'log_level', None)
    )
    
    logger.debug("WAPI CLI started")
    logger.debug(f"Arguments: {vars(args)}")
    
    # Handle wizard option
    if args.wizard:
        success = run_config_wizard(args.config)
        return EXIT_SUCCESS if success else EXIT_CONFIG_ERROR
    
    # Handle top-level search alias (-s/--search)
    if getattr(args, 'search_domain', None):
        if not hasattr(args, 'format'):
            args.format = 'table'
        args.domain = args.search_domain
        args.whois_server = getattr(args, 'search_whois_server', None)
        args.whois_timeout = getattr(args, 'search_whois_timeout', 10)
        args.module = 'search'
        args.command = 'search'
        args.func = cmd_search
    
    # Handle aliases option
    if args.aliases:
        print(list_aliases())
        return EXIT_SUCCESS
    
    # Handle interactive mode
    if args.interactive:
        try:
            client = get_client(args.config)
            if not client:
                return EXIT_CONFIG_ERROR
            return start_interactive_mode(client)
        except WAPIConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_CONFIG_ERROR
    
    # Handle no command
    if not args.module:
        parser.print_help()
        return EXIT_ERROR
    
    # Ensure format is available in args (for commands that need it)
    if not hasattr(args, 'format'):
        args.format = 'table'
    
    # Execute command
    if hasattr(args, 'func'):
        # Config commands do not require a client; handle them early.
        if args.func in [cmd_config_show, cmd_config_validate, cmd_config_set]:
            return args.func(args)

        # Get API client for other commands
        try:
            client = get_client(args.config)
            if not client:
                return EXIT_CONFIG_ERROR
        except WAPIConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_CONFIG_ERROR

        try:
            return args.func(args, client)
        except WAPIConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_CONFIG_ERROR
        except WAPIAuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_AUTH_ERROR
        except WAPIConnectionError as e:
            logger.error(f"Connection error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_CONNECTION_ERROR
        except WAPITimeoutError as e:
            logger.error(f"Timeout error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_TIMEOUT_ERROR
        except WAPIRequestError as e:
            logger.error(f"API request error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_ERROR
        except WAPIError as e:
            logger.error(f"WAPI error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return EXIT_ERROR
        except KeyboardInterrupt:
            logger.info("Operation cancelled by user")
            print("\nOperation cancelled", file=sys.stderr)
            return EXIT_ERROR
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            print(f"Unexpected error: {e}", file=sys.stderr)
            return EXIT_ERROR
    else:
        print(f"Error: Command not implemented yet", file=sys.stderr)
        return EXIT_ERROR


if __name__ == '__main__':
    sys.exit(main())
