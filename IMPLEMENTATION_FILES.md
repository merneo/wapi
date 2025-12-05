# Implementation Files List - WAPI CLI

**Document Version:** 1.0  
**Date:** 2025-01-05  
**Language:** US English

## Overview

This document lists all Python files that need to be created for the WAPI CLI implementation. The structure follows the design specification in `CLI_DESIGN_AUDIT.md`.

## File Structure

```
wapi/
├── __init__.py
├── __main__.py
├── cli.py
├── config.py
├── api/
│   ├── __init__.py
│   ├── client.py
│   └── auth.py
├── commands/
│   ├── __init__.py
│   ├── domain.py
│   ├── nsset.py
│   ├── contact.py
│   ├── dns.py
│   ├── auth.py
│   └── config.py
└── utils/
    ├── __init__.py
    ├── formatters.py
    └── validators.py

tests/
├── __init__.py
├── test_domain.py
├── test_nsset.py
├── test_contact.py
├── test_auth.py
├── test_config.py
└── test_cli.py

setup.py
requirements.txt
```

## Detailed File List

### Core Package Files (4 files)

#### 1. `wapi/__init__.py`
**Purpose:** Package initialization  
**Contents:**
- Package metadata
- Version information
- Main class exports
- `__version__` constant

**Key Exports:**
```python
from wapi.api.client import WedosAPIClient
from wapi.cli import main

__version__ = "1.0.0"
__all__ = ['WedosAPIClient', 'main']
```

#### 2. `wapi/__main__.py`
**Purpose:** Allow `python -m wapi` execution  
**Contents:**
- Entry point for module execution
- Calls CLI main function

**Code:**
```python
from wapi.cli import main

if __name__ == '__main__':
    main()
```

#### 3. `wapi/cli.py`
**Purpose:** Main CLI parser and command router  
**Contents:**
- CLI framework setup (argparse or click)
- Global option parsing
- Command routing to modules
- Error handling
- Output formatting coordination

**Key Functions:**
- `main()` - Entry point
- `parse_args()` - Argument parsing
- `handle_command()` - Command routing
- `format_output()` - Output formatting

#### 4. `wapi/config.py`
**Purpose:** Configuration management  
**Contents:**
- Load configuration from `config.env`
- Environment variable support
- Configuration validation
- Default value management
- Configuration file reading/writing

**Key Functions:**
- `load_config()` - Load from file/env
- `validate_config()` - Validate settings
- `get_config()` - Get configuration value
- `set_config()` - Set configuration value

### API Client Files (3 files)

#### 5. `wapi/api/__init__.py`
**Purpose:** API package exports  
**Contents:**
- Export main API client class
- Export authentication utilities

#### 6. `wapi/api/client.py`
**Purpose:** WEDOS API client implementation  
**Contents:**
- `WedosAPIClient` class
- HTTP request handling (requests library)
- XML/JSON format support
- Response parsing
- Error handling
- Async operation polling

**Key Methods:**
- `__init__(username, password, base_url, use_json)`
- `call(command, data)` - Generic API call
- `domain_info(domain)` - Get domain info
- `domain_update_ns(domain, nsset_name, nameservers)` - Update nameservers
- `nsset_create(name, nameservers, tld, tech_c)` - Create NSSET
- `nsset_info(name)` - Get NSSET info
- `poll_until_complete(command, identifier)` - Poll async operations

#### 7. `wapi/api/auth.py`
**Purpose:** Authentication utilities  
**Contents:**
- SHA1 hash calculation
- Timezone handling (Europe/Prague)
- Authentication string generation
- Credential validation

**Key Functions:**
- `calculate_auth(username, password)` - Calculate auth hash
- `get_prague_hour()` - Get current hour in Prague timezone
- `validate_credentials(username, password)` - Validate format

### Command Module Files (6 files)

#### 8. `wapi/commands/__init__.py`
**Purpose:** Command package exports  
**Contents:**
- Export command handlers
- Command registration

#### 9. `wapi/commands/domain.py`
**Purpose:** Domain management commands  
**Contents:**
- `cmd_list()` - List domains command handler
- `cmd_info()` - Domain info command handler
- `cmd_update_ns()` - Update nameservers command handler
- `cmd_create()` - Create domain command handler (if supported)
- `cmd_transfer()` - Domain transfer command handler (if supported)
- `cmd_renew()` - Renew domain command handler (if supported)

**Commands Implemented:**
- `wapi domain list`
- `wapi domain info <domain>`
- `wapi domain update-ns <domain>`
- `wapi domain create <domain>` (if supported)
- `wapi domain transfer <domain>` (if supported)
- `wapi domain renew <domain>` (if supported)

#### 10. `wapi/commands/nsset.py`
**Purpose:** NSSET management commands  
**Contents:**
- `cmd_list()` - List NSSETs command handler
- `cmd_info()` - NSSET info command handler
- `cmd_create()` - Create NSSET command handler
- `cmd_update()` - Update NSSET command handler (if supported)
- `cmd_delete()` - Delete NSSET command handler (if supported)

**Commands Implemented:**
- `wapi nsset list`
- `wapi nsset info <nsset>`
- `wapi nsset create <name>`
- `wapi nsset update <nsset>` (if supported)
- `wapi nsset delete <nsset>` (if supported)

#### 11. `wapi/commands/contact.py`
**Purpose:** Contact handle management commands  
**Contents:**
- `cmd_list()` - List contacts command handler
- `cmd_info()` - Contact info command handler
- `cmd_create()` - Create contact command handler (if supported)
- `cmd_update()` - Update contact command handler (if supported)

**Commands Implemented:**
- `wapi contact list`
- `wapi contact info <contact>`
- `wapi contact create` (if supported)
- `wapi contact update <contact>` (if supported)

#### 12. `wapi/commands/dns.py`
**Purpose:** DNS record management commands (if supported)  
**Contents:**
- `cmd_list()` - List DNS records command handler
- `cmd_add()` - Add DNS record command handler
- `cmd_update()` - Update DNS record command handler
- `cmd_delete()` - Delete DNS record command handler

**Commands Implemented:**
- `wapi dns list <domain>`
- `wapi dns add <domain>`
- `wapi dns update <domain>`
- `wapi dns delete <domain>`

#### 13. `wapi/commands/auth.py`
**Purpose:** Authentication and connection testing commands  
**Contents:**
- `cmd_ping()` - Ping command handler
- `cmd_test()` - Test credentials command handler
- `cmd_status()` - API status command handler

**Commands Implemented:**
- `wapi auth ping`
- `wapi auth test`
- `wapi auth status`

#### 14. `wapi/commands/config.py`
**Purpose:** Configuration management commands  
**Contents:**
- `cmd_show()` - Show configuration command handler
- `cmd_set()` - Set configuration value command handler
- `cmd_unset()` - Remove configuration value command handler
- `cmd_validate()` - Validate configuration command handler

**Commands Implemented:**
- `wapi config show`
- `wapi config set <key> <value>`
- `wapi config unset <key>`
- `wapi config validate`

### Utility Files (3 files)

#### 15. `wapi/utils/__init__.py`
**Purpose:** Utility package exports  
**Contents:**
- Export formatter functions
- Export validator functions

#### 16. `wapi/utils/formatters.py`
**Purpose:** Output formatting utilities  
**Contents:**
- `format_table(data)` - Format as table
- `format_json(data)` - Format as JSON
- `format_xml(data)` - Format as XML
- `format_yaml(data)` - Format as YAML
- `format_output(data, format_type)` - Main formatter router

**Key Functions:**
- Table formatting (using tabulate library)
- JSON pretty printing
- XML formatting
- YAML formatting

#### 17. `wapi/utils/validators.py`
**Purpose:** Input validation utilities  
**Contents:**
- `validate_domain(domain)` - Validate domain name
- `validate_ipv4(ip)` - Validate IPv4 address
- `validate_ipv6(ip)` - Validate IPv6 address
- `validate_nameserver(ns_string)` - Validate nameserver format
- `validate_email(email)` - Validate email address

**Key Functions:**
- Domain name validation (RFC 1123)
- IP address validation
- Nameserver format parsing and validation
- Email validation

### Supporting Files (2 files)

#### 18. `setup.py` or `pyproject.toml`
**Purpose:** Package installation configuration  
**Contents:**
- Package metadata
- Dependencies
- Entry point configuration
- Installation instructions

**Key Configuration:**
```python
entry_points={
    'console_scripts': [
        'wapi=wapi.cli:main',
    ],
}
```

#### 19. `requirements.txt`
**Purpose:** Python dependencies  
**Contents:**
- `requests>=2.25.0` - HTTP client
- `click>=7.0` or use `argparse` (built-in) - CLI framework
- `pyyaml>=5.4.0` - YAML support (optional)
- `tabulate>=0.8.0` - Table formatting (optional)

### Test Files (6 files)

#### 20. `tests/__init__.py`
**Purpose:** Test package initialization

#### 21. `tests/test_domain.py`
**Purpose:** Domain module tests  
**Contents:**
- Test domain list command
- Test domain info command
- Test domain update-ns command
- Test domain validation
- Mock API responses

#### 22. `tests/test_nsset.py`
**Purpose:** NSSET module tests  
**Contents:**
- Test NSSET list command
- Test NSSET info command
- Test NSSET create command
- Test nameserver parsing
- Mock API responses

#### 23. `tests/test_contact.py`
**Purpose:** Contact module tests  
**Contents:**
- Test contact list command
- Test contact info command
- Mock API responses

#### 24. `tests/test_auth.py`
**Purpose:** Authentication tests  
**Contents:**
- Test ping command
- Test authentication calculation
- Test timezone handling
- Mock API responses

#### 25. `tests/test_config.py`
**Purpose:** Configuration tests  
**Contents:**
- Test config loading
- Test config validation
- Test environment variable handling
- Test config file reading/writing

#### 26. `tests/test_cli.py`
**Purpose:** CLI framework tests  
**Contents:**
- Test command parsing
- Test command routing
- Test error handling
- Test output formatting
- Test global options

## Implementation Summary

### Total Files: 26 Python files

**Breakdown:**
- Core files: 4
- API client files: 3
- Command module files: 6
- Utility files: 3
- Supporting files: 2
- Test files: 6
- Package structure files: 2 (`__init__.py` files in packages)

### Estimated Lines of Code

- Core files: ~800 lines
- API client: ~600 lines
- Command modules: ~1200 lines
- Utilities: ~400 lines
- Tests: ~1000 lines
- **Total: ~4000 lines of Python code**

## Implementation Order

### Phase 1: Foundation (Week 1)
1. Package structure setup
2. Configuration management
3. API client core
4. Authentication

### Phase 2: Essential Commands (Week 2)
1. CLI framework
2. Domain module (list, info, update-ns)
3. Auth module (ping, test)

### Phase 3: NSSET Operations (Week 3)
1. NSSET module (list, info, create)
2. Enhanced domain operations

### Phase 4: Additional Features (Week 4)
1. Contact module
2. DNS module (if supported)
3. Config module
4. Advanced formatting

### Phase 5: Testing & Documentation (Week 5)
1. Unit tests
2. Integration tests
3. Documentation updates
4. Examples and tutorials

## Standards Compliance

All files must follow:
- **PEP 8** - Python style guide
- **PEP 484** - Type hints
- **US English** - All strings and documentation
- **RFC Standards** - Test data only (example.com, 192.0.2.0/24)
- **Academic Quality** - Comprehensive docstrings, error handling

## References

- See `CLI_DESIGN_AUDIT.md` for detailed command specifications
- See `WIKI.md` for API reference and examples
- [Python Packaging Guide](https://packaging.python.org/)
- [Click Documentation](https://click.palletsprojects.com/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

---

**Status:** Ready for Implementation  
**Next Step:** Begin Phase 1 - Foundation setup
