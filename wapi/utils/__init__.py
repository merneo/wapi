"""
WAPI Utility Functions

This package contains utility functions for formatting, validation, and other helper operations.
"""

from .formatters import format_output, format_table, format_json, format_xml, format_yaml
from .validators import (
    validate_domain,
    validate_ipv4,
    validate_ipv6,
    validate_nameserver,
    validate_email,
)
from .logger import setup_logging, get_logger
from .dns_lookup import (
    enhance_nameserver_with_ipv6,
    get_ipv6_from_nameserver,
    get_ipv6_from_ipv4,
)
from .aliases import expand_alias, get_aliases, list_aliases
from .interactive import start_interactive_mode, WAPIInteractiveShell
from .batch import (
    batch_domain_operation,
    batch_dns_operation,
    read_domains_from_file,
    write_results_to_file,
)
from .config_wizard import run_config_wizard

__all__ = [
    # Formatters
    'format_output',
    'format_table',
    'format_json',
    'format_xml',
    'format_yaml',
    # Validators
    'validate_domain',
    'validate_ipv4',
    'validate_ipv6',
    'validate_nameserver',
    'validate_email',
    # Logger
    'setup_logging',
    'get_logger',
    # DNS Lookup
    'enhance_nameserver_with_ipv6',
    'get_ipv6_from_nameserver',
    'get_ipv6_from_ipv4',
    # Aliases
    'expand_alias',
    'get_aliases',
    'list_aliases',
    # Interactive
    'start_interactive_mode',
    'WAPIInteractiveShell',
    # Batch
    'batch_domain_operation',
    'batch_dns_operation',
    'read_domains_from_file',
    'write_results_to_file',
    # Config Wizard
    'run_config_wizard',
]
    'enhance_nameserver_with_ipv6',
    'get_ipv6_from_nameserver',
    'get_ipv6_from_ipv4',
]
