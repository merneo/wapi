# WAPI CLI Design Audit - Academic Specification

**Document Version:** 1.0  
**Date:** 2025-01-05  
**Language:** US English  
**Standard:** Academic-level technical specification

## Executive Summary

This document provides a comprehensive audit and design specification for a command-line interface (CLI) tool for WEDOS WAPI. The CLI will be implemented as a Python package with a single entry point `wapi` that provides modular subcommands for different WAPI operations.

## 1. CLI Architecture Overview

### 1.1 Command Structure

The CLI follows a modular command structure:

```
wapi [GLOBAL_OPTIONS] <MODULE> <COMMAND> [ARGUMENTS] [OPTIONS]
```

**Example:**
```bash
wapi domain list                    # List all domains
wapi domain info example.com        # Get domain information
wapi domain update-ns example.com   # Update domain nameservers
wapi nsset create                   # Create NSSET
wapi nsset list                     # List NSSETs
```

### 1.2 Design Principles

1. **Modularity**: Each WAPI functional area is a separate module
2. **Consistency**: Uniform command structure across all modules
3. **Discoverability**: Built-in help system and command completion
4. **Usability**: Intuitive command names and clear error messages
5. **Extensibility**: Easy to add new modules and commands

## 2. Module Specification

### 2.1 Core Modules

Based on WEDOS WAPI capabilities documented in the wiki, the following modules are required:

#### Module 1: `domain`
**Purpose:** Domain management operations

**Commands:**
- `list` / `-l` - List all domains
- `info <domain>` - Get domain information
- `update-ns <domain>` - Update domain nameservers
- `create <domain>` - Register new domain (if supported)
- `transfer <domain>` - Initiate domain transfer
- `renew <domain>` - Renew domain registration
- `delete <domain>` - Delete domain (if supported)

**Example Usage:**
```bash
wapi domain list
wapi domain info example.com
wapi domain update-ns example.com --nameserver ns1.example.com:1.2.3.4
```

#### Module 2: `nsset`
**Purpose:** NSSET (Nameserver Set) management

**Commands:**
- `list` / `-l` - List all NSSETs
- `info <nsset>` - Get NSSET information
- `create <name>` - Create new NSSET
- `update <nsset>` - Update existing NSSET
- `delete <nsset>` - Delete NSSET (if supported)

**Example Usage:**
```bash
wapi nsset list
wapi nsset info MY-NSSET
wapi nsset create MY-NSSET --nameserver ns1.example.com:1.2.3.4:2001:db8::1
```

#### Module 3: `contact`
**Purpose:** Contact handle management

**Commands:**
- `list` / `-l` - List all contacts
- `info <contact>` - Get contact information
- `create` - Create new contact
- `update <contact>` - Update contact information

**Example Usage:**
```bash
wapi contact list
wapi contact info MY-CONTACT
```

#### Module 4: `dns`
**Purpose:** DNS record management (if supported by WAPI)

**Commands:**
- `list <domain>` - List DNS records for domain
- `add <domain>` - Add DNS record
- `update <domain>` - Update DNS record
- `delete <domain>` - Delete DNS record

#### Module 5: `auth`
**Purpose:** Authentication and connection testing

**Commands:**
- `ping` - Test WAPI connection
- `test` - Verify credentials
- `status` - Check API status

**Example Usage:**
```bash
wapi auth ping
wapi auth test
```

#### Module 6: `config`
**Purpose:** Configuration management

**Commands:**
- `show` - Display current configuration
- `set <key> <value>` - Set configuration value
- `unset <key>` - Remove configuration value
- `validate` - Validate configuration

**Example Usage:**
```bash
wapi config show
wapi config set username user@example.com
```

## 3. Global Options

All commands support these global options:

```
--config <file>     Specify configuration file (default: config.env)
--format <format>   Output format: json, xml, table, yaml (default: table)
--verbose / -v      Verbose output
--quiet / -q         Quiet mode (errors only)
--no-wait            Don't wait for async operations
--output <file>      Write output to file
```

## 4. Command Specification Details

### 4.1 Domain Module Commands

#### `wapi domain list`

**Description:** List all domains in the account

**Options:**
- `--status <status>` - Filter by status (ok, expired, etc.)
- `--tld <tld>` - Filter by TLD (cz, com, etc.)
- `--format <format>` - Output format

**Output:** Table or JSON list of domains

**Example:**
```bash
wapi domain list
wapi domain list --tld cz --format json
```

#### `wapi domain info <domain>`

**Description:** Get detailed information about a domain

**Arguments:**
- `<domain>` - Domain name (required)

**Options:**
- `--format <format>` - Output format

**Output:** Domain details including status, nameservers, expiration, etc.

**Example:**
```bash
wapi domain info example.com
wapi domain info example.com --format json
```

#### `wapi domain update-ns <domain>`

**Description:** Update domain nameservers

**Arguments:**
- `<domain>` - Domain name (required)

**Options:**
- `--nsset <name>` - Use existing NSSET
- `--nameserver <ns>` - Add nameserver (can be used multiple times)
  Format: `name:ipv4:ipv6` or `name:ipv4`
- `--source-domain <domain>` - Copy nameservers from another domain
- `--wait` - Wait for async operation completion

**Example:**
```bash
wapi domain update-ns example.com --nsset MY-NSSET
wapi domain update-ns example.com --nameserver ns1.example.com:1.2.3.4:2001:db8::1
wapi domain update-ns example.com --source-domain example.org
```

### 4.2 NSSET Module Commands

#### `wapi nsset list`

**Description:** List all NSSETs

**Options:**
- `--format <format>` - Output format

**Output:** List of NSSET names and basic information

#### `wapi nsset info <nsset>`

**Description:** Get detailed NSSET information

**Arguments:**
- `<nsset>` - NSSET name (required)

**Output:** NSSET details including nameservers and GLUE records

#### `wapi nsset create <name>`

**Description:** Create a new NSSET

**Arguments:**
- `<name>` - NSSET name (required)

**Options:**
- `--nameserver <ns>` - Add nameserver (required, can be used multiple times)
  Format: `name:ipv4:ipv6` or `name:ipv4`
- `--tld <tld>` - Top-level domain (default: cz)
- `--tech-c <contact>` - Technical contact handle
- `--wait` - Wait for async operation completion

**Example:**
```bash
wapi nsset create MY-NSSET \
  --nameserver ns1.example.com:192.0.2.1:2001:db8::1 \
  --nameserver ns2.example.com:192.0.2.2:2001:db8::2
```

### 4.3 Contact Module Commands

#### `wapi contact list`

**Description:** List all contact handles

**Output:** List of contact handles

#### `wapi contact info <contact>`

**Description:** Get contact information

**Arguments:**
- `<contact>` - Contact handle (required)

## 5. Python Package Structure

### 5.1 Directory Structure

```
wapi/
├── __init__.py
├── __main__.py              # Entry point for 'python -m wapi'
├── cli.py                    # Main CLI parser
├── config.py                 # Configuration management
├── api/
│   ├── __init__.py
│   ├── client.py             # WEDOS API client
│   └── auth.py               # Authentication
├── commands/
│   ├── __init__.py
│   ├── domain.py             # Domain module commands
│   ├── nsset.py              # NSSET module commands
│   ├── contact.py            # Contact module commands
│   ├── dns.py                # DNS module commands
│   ├── auth.py               # Auth module commands
│   └── config.py             # Config module commands
└── utils/
    ├── __init__.py
    ├── formatters.py         # Output formatting
    └── validators.py         # Input validation
```

### 5.2 Entry Point Configuration

**setup.py or pyproject.toml:**
```python
entry_points={
    'console_scripts': [
        'wapi=wapi.cli:main',
    ],
}
```

This allows installation as:
```bash
pip install -e .
wapi domain list
```

## 6. Implementation Files List

### 6.1 Core Files

1. **`wapi/__init__.py`**
   - Package initialization
   - Version information
   - Exports main classes

2. **`wapi/__main__.py`**
   - Allows `python -m wapi` execution
   - Calls CLI main function

3. **`wapi/cli.py`**
   - Main CLI parser using `argparse` or `click`
   - Command routing
   - Global option handling
   - Error handling and output formatting

4. **`wapi/config.py`**
   - Configuration file loading (config.env)
   - Environment variable support
   - Configuration validation
   - Default value management

### 6.2 API Client Files

5. **`wapi/api/__init__.py`**
   - API package exports

6. **`wapi/api/client.py`**
   - `WedosAPIClient` class
   - HTTP request handling
   - XML/JSON format support
   - Response parsing
   - Error handling

7. **`wapi/api/auth.py`**
   - Authentication hash calculation
   - Timezone handling (Europe/Prague)
   - Credential management

### 6.3 Command Module Files

8. **`wapi/commands/__init__.py`**
   - Command package exports
   - Command registration

9. **`wapi/commands/domain.py`**
   - Domain module implementation
   - Functions: `list_domains()`, `get_domain_info()`, `update_nameservers()`, etc.
   - Command handlers for each domain command

10. **`wapi/commands/nsset.py`**
    - NSSET module implementation
    - Functions: `list_nssets()`, `get_nsset_info()`, `create_nsset()`, etc.
    - Command handlers for each NSSET command

11. **`wapi/commands/contact.py`**
    - Contact module implementation
    - Functions: `list_contacts()`, `get_contact_info()`, etc.

12. **`wapi/commands/dns.py`**
    - DNS module implementation (if supported)
    - DNS record management functions

13. **`wapi/commands/auth.py`**
    - Authentication module
    - `ping()`, `test()`, `status()` functions

14. **`wapi/commands/config.py`**
    - Configuration management commands
    - Configuration file manipulation

### 6.4 Utility Files

15. **`wapi/utils/__init__.py`**
    - Utility package exports

16. **`wapi/utils/formatters.py`**
    - Output formatting functions
    - JSON, XML, table, YAML formatters
    - Pretty printing

17. **`wapi/utils/validators.py`**
    - Input validation functions
    - Domain name validation
    - IP address validation
    - Nameserver format validation

### 6.5 Supporting Files

18. **`setup.py` or `pyproject.toml`**
    - Package metadata
    - Dependencies
    - Entry point configuration
    - Installation instructions

19. **`requirements.txt`**
    - Python dependencies
    - Version specifications

20. **`README.md`** (update existing)
    - CLI usage documentation
    - Installation instructions
    - Examples

21. **`MANIFEST.in`** (optional)
    - Include non-Python files in package

## 7. Command Examples Reference

### 7.1 Domain Operations

```bash
# List all domains
wapi domain list

# Get domain information
wapi domain info example.com

# Update nameservers using existing NSSET
wapi domain update-ns example.com --nsset MY-NSSET

# Update nameservers with new nameservers
wapi domain update-ns example.com \
  --nameserver ns1.example.com:192.0.2.1:2001:db8::1 \
  --nameserver ns2.example.com:192.0.2.2:2001:db8::2

# Copy nameservers from another domain
wapi domain update-ns example.com --source-domain example.org

# List domains filtered by TLD
wapi domain list --tld cz

# Get domain info in JSON format
wapi domain info example.com --format json
```

### 7.2 NSSET Operations

```bash
# List all NSSETs
wapi nsset list

# Get NSSET information
wapi nsset info MY-NSSET

# Create new NSSET
wapi nsset create MY-NSSET \
  --nameserver ns1.example.com:192.0.2.1:2001:db8::1 \
  --nameserver ns2.example.com:192.0.2.2:2001:db8::2 \
  --tld cz \
  --tech-c MY-CONTACT

# Create NSSET and wait for completion
wapi nsset create MY-NSSET --nameserver ns1.example.com:192.0.2.1 --wait
```

### 7.3 Authentication

```bash
# Test connection
wapi auth ping

# Verify credentials
wapi auth test

# Check API status
wapi auth status
```

### 7.4 Configuration

```bash
# Show current configuration
wapi config show

# Set configuration value
wapi config set username user@example.com

# Use custom config file
wapi --config /path/to/config.env domain list
```

## 8. Error Handling

### 8.1 Error Categories

1. **Configuration Errors**
   - Missing credentials
   - Invalid configuration file
   - Missing required settings

2. **API Errors**
   - Connection failures
   - Authentication failures
   - Invalid API responses
   - WEDOS error codes (2xxx series)

3. **Validation Errors**
   - Invalid domain names
   - Invalid IP addresses
   - Invalid command syntax

4. **Runtime Errors**
   - File I/O errors
   - Network timeouts
   - Async operation timeouts

### 8.2 Error Output Format

Errors should be clearly formatted:

```bash
$ wapi domain info invalid..domain
Error: Invalid domain name format
  Domain: invalid..domain
  Reason: Contains consecutive dots

$ wapi domain info nonexistent.com
API Error: Domain not found
  Code: 2103
  Domain: nonexistent.com
  Suggestion: Check domain name spelling
```

## 9. Output Formats

### 9.1 Table Format (Default)

Human-readable table output:

```
Domain          Status    Expires      NSSET
example.com     ok        2025-12-31   NS-EXAMPLE-COM-123
example.org     ok        2026-01-15   NS-EXAMPLE-ORG-456
```

### 9.2 JSON Format

Structured JSON output for scripting:

```json
{
  "domains": [
    {
      "name": "example.com",
      "status": "ok",
      "expires": "2025-12-31",
      "nsset": "NS-EXAMPLE-COM-123"
    }
  ]
}
```

### 9.3 XML Format

XML output matching WAPI format:

```xml
<response>
  <code>1000</code>
  <result>OK</result>
  <data>
    <domain>...</domain>
  </data>
</response>
```

### 9.4 YAML Format

YAML output for configuration files:

```yaml
domains:
  - name: example.com
    status: ok
    expires: 2025-12-31
```

## 10. Asynchronous Operations

### 10.1 POLL Queue Support

Commands that trigger async operations support `--wait` flag:

```bash
# Start operation and wait for completion
wapi nsset create MY-NSSET --nameserver ns1.example.com:192.0.2.1 --wait

# Start operation without waiting
wapi nsset create MY-NSSET --nameserver ns1.example.com:192.0.2.1 --no-wait
```

### 10.2 Polling Implementation

When `--wait` is used:
1. Command starts async operation
2. CLI polls API for status
3. Shows progress indicator
4. Returns final result when complete

## 11. Testing Requirements

### 11.1 Unit Tests

Each module should have unit tests:
- `tests/test_domain.py`
- `tests/test_nsset.py`
- `tests/test_contact.py`
- `tests/test_auth.py`
- `tests/test_config.py`
- `tests/test_cli.py`

### 11.2 Integration Tests

End-to-end tests with mock API:
- `tests/integration/test_domain_operations.py`
- `tests/integration/test_nsset_operations.py`

### 11.3 Test Data

All tests use RFC-compliant test data:
- Domains: `example.com`, `example.org`
- IPs: `192.0.2.0/24`, `2001:db8::/32`

## 12. Documentation Requirements

### 12.1 Command Documentation

Each command should have:
- Description
- Usage syntax
- Options explanation
- Examples
- Error conditions

### 12.2 API Documentation

Code should include:
- Docstrings for all functions
- Type hints
- Parameter descriptions
- Return value descriptions

### 12.3 User Documentation

- Installation guide
- Quick start tutorial
- Command reference
- Examples and use cases
- Troubleshooting guide

## 13. Dependencies

### 13.1 Required Packages

- `requests` - HTTP client library
- `click` or `argparse` - CLI framework
- `pyyaml` - YAML support (optional)
- `tabulate` - Table formatting (optional)

### 13.2 Python Version

- Minimum: Python 3.6
- Recommended: Python 3.8+

## 14. Implementation Priority

### Phase 1: Core Infrastructure
1. CLI framework setup
2. Configuration management
3. API client implementation
4. Authentication

### Phase 2: Essential Commands
1. `wapi auth ping`
2. `wapi domain list`
3. `wapi domain info`
4. `wapi domain update-ns`

### Phase 3: NSSET Operations
1. `wapi nsset list`
2. `wapi nsset info`
3. `wapi nsset create`

### Phase 4: Additional Features
1. Contact management
2. DNS record management
3. Advanced formatting options
4. Command completion

## 15. Academic Standards Compliance

### 15.1 Code Quality
- PEP 8 style guide compliance
- Type hints (PEP 484)
- Comprehensive docstrings (Google or NumPy style)
- Unit test coverage > 80%

### 15.2 Documentation
- US English spelling and terminology
- Clear, concise technical writing
- Examples using RFC-compliant test data
- Proper citation of standards (RFC 2606, 5737, 3849)

### 15.3 Security
- No hardcoded credentials
- Secure credential storage
- Input validation
- Error message sanitization

## 16. References

- [WEDOS WAPI Manual](https://kb.wedos.cz/wapi-manual/)
- [Python CLI Best Practices](https://docs.python.org/3/library/argparse.html)
- [Click Documentation](https://click.palletsprojects.com/)
- [RFC 2606](https://tools.ietf.org/html/rfc2606) - Reserved Top-Level DNS Names
- [RFC 5737](https://tools.ietf.org/html/rfc5737) - IPv4 Documentation Addresses
- [RFC 3849](https://tools.ietf.org/html/rfc3849) - IPv6 Documentation Addresses

---

**Document Status:** Ready for Implementation  
**Next Steps:** Begin Phase 1 implementation
