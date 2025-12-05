# Changelog

All notable changes to the WAPI CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2025-01-05

### Added
- **Async Polling Support**: Implemented `poll_until_complete` method in `WedosAPIClient`
- **Polling for Domain Update**: `wapi domain update-ns --wait` now polls until nameservers are updated
- **Polling for NSSET Create**: `wapi nsset create --wait` now polls until NSSET is created
- **Polling for DNS Add**: `wapi dns add --wait` now polls until DNS record is added
- **Polling for DNS Delete**: `wapi dns delete --wait` now polls until DNS record is deleted
- **DNS Record Update**: `wapi dns update <domain> --id <id>` command for updating DNS records
  - Support for updating name, type, value, and TTL
  - `--wait` flag support with polling
- Progress indicators during polling (when not in quiet mode)
- Timeout handling (default: 60 attempts × 10 seconds = 10 minutes)

### Changed
- `--wait` flag now actually waits for async operations to complete
- Polling uses appropriate check commands (`domain-info`, `nsset-info`, `dns-rows-list`)
- Improved async operation handling with proper status checking

### Technical Details
- Added `poll_until_complete()` method to `WedosAPIClient` class
- Custom completion check functions for each operation type
- Configurable polling parameters (max_attempts, interval)
- Verbose mode support for polling progress

## [0.6.0] - 2025-01-05
- Contact list implementation
- NSSET list implementation
- DNS record update operation
- Async operation polling (--wait flag)

## [0.6.0] - 2025-01-05

### Added
- Phase 6: Additional modules
  - `wapi/commands/contact.py` - Contact management
    - `wapi contact info <handle>` - Get contact information with sensitive data filtering
    - `wapi contact list` - List contacts (stub)
  - `wapi/commands/config.py` - Configuration management
    - `wapi config show` - Show configuration (passwords hidden)
    - `wapi config validate` - Validate configuration
    - `wapi config set <key> <value>` - Set configuration value
  - `wapi/commands/dns.py` - DNS management
    - `wapi dns list <domain>` - List nameservers for domain
    - `wapi dns records <domain>` - List DNS records (stub)
    - `wapi dns add/delete` - DNS record operations (stubs)

### Tested
- Contact info tested with FORPSI-VVN-S638343 - working correctly
- Config commands tested - working correctly
- DNS list tested with spravuju.cz - working correctly
- All sensitive data filtered from outputs

### Added (Post v0.6.0)
- DNS record operations fully implemented
  - `wapi dns records <domain>` - List all DNS records
  - `wapi dns add <domain>` - Add DNS record with full options
  - `wapi dns delete <domain>` - Delete DNS record by ID
- Domain list command implemented
  - `wapi domain list` - List all domains
  - `wapi domain list --tld <tld>` - Filter by TLD
  - `wapi domain list --status <status>` - Filter by status
- All operations tested and working correctly
- Phase 4: Domain module
- Phase 5: NSSET module
- Phase 6: Additional modules (contact, config, dns)

## [0.2.0] - 2025-01-05

### Added
- Phase 1: Configuration and authentication modules
  - `wapi/config.py` - Configuration loading from file and environment variables
  - `wapi/api/auth.py` - Authentication hash calculation with Prague timezone
  - `wapi/utils/validators.py` - Input validation (domain, IP, nameserver)
- Phase 2: API client core
  - `wapi/api/client.py` - Core WEDOS API client with XML/JSON support
  - `WedosAPIClient` class with `ping()` and `domain_info()` methods
  - XML response parsing with proper structure handling

### Fixed
- XML parser to correctly handle root `<response>` element
- Type hints compatibility (Tuple instead of tuple)
- Pytz import fallback for systems without pytz

### Tested
- All modules tested with production WAPI
- Domain info tested with spravuju.cz domain
- Ping command verified working

## [0.3.0] - 2025-01-05

### Added
- Phase 3: CLI framework and basic commands
  - `wapi/cli.py` - Main CLI parser with argparse
  - `wapi/__main__.py` - Module entry point for `python -m wapi`
  - `wapi/utils/formatters.py` - Output formatting (table, JSON, XML, YAML)
- Implemented commands:
  - `wapi auth ping` - Test API connection
  - `wapi domain info <domain>` - Get domain information
- Global options:
  - `--config <file>` - Specify configuration file
  - `--format <format>` - Output format (table, json, xml, yaml)
  - `--verbose / -v` - Verbose output
  - `--quiet / -q` - Quiet mode

### Tested
- CLI commands tested with spravuju.cz domain
- All output formats verified working
- Ping and domain info commands functional

## [0.4.0] - 2025-01-05

### Added
- Phase 4: Domain module complete
  - `wapi/commands/domain.py` - Domain command handlers
  - `wapi domain info <domain>` - Get domain information with sensitive data filtering
  - `wapi domain update-ns <domain>` - Update domain nameservers
    - `--nsset <name>` - Use existing NSSET
    - `--nameserver <ns>` - Add nameserver (can be used multiple times)
    - `--source-domain <domain>` - Copy nameservers from another domain
    - `--wait` - Wait for async operation completion
- Sensitive data filtering
  - All personal information (email, phone, address, etc.) filtered from output
  - Sensitive fields show as `[HIDDEN]` in output
- API client enhancements
  - `domain_update_ns()` method with automatic NSSET creation
  - Support for existing NSSET assignment
  - Nameserver copying from source domain

### Tested
- Domain info tested with spravuju.cz - working correctly
- Sensitive data filtering verified
- Domain structure analyzed and documented

## [0.5.0] - 2025-01-05

### Added
- Phase 5: NSSET module
  - `wapi/commands/nsset.py` - NSSET command handlers
  - `wapi nsset create <name>` - Create new NSSET with nameservers
    - `--nameserver <ns>` - Nameserver (can be used multiple times)
    - `--tld <tld>` - Top-level domain (default: cz)
    - `--tech-c <handle>` - Technical contact handle
    - `--wait` - Wait for async completion
  - `wapi nsset info <name>` - Get NSSET information
  - `wapi nsset list` - List NSSETs (stub for future implementation)

### Changed
- Use spravuju.cz for CZ domain testing
- Use linuxloser.com for COM domain testing

### Tested
- NSSET info tested with spravuju.cz NSSET - working correctly
- NSSET structure analyzed and documented

## [0.1.0] - 2025-01-05

### Added
- Phase 0: Project setup and foundation
  - Package structure (wapi/, wapi/api/, wapi/commands/, wapi/utils/, tests/)
  - `wapi/__init__.py` with version information
  - `setup.py` with entry point configuration
  - `requirements.txt` with dependencies

### Implementation Phases
See `IMPLEMENTATION_PHASES.md` for detailed phase-by-phase implementation plan ordered by complexity.

## [1.0.0] - 2025-01-05

### Added
- Initial public release
- Complete WIKI documentation (1092 lines)
- README with SEO-optimized content
- CLI design audit and specification
- Implementation files list
- Command reference guide
- Workflow guide for safe repository development
- GitHub Actions workflow for documentation validation
- Configuration template (config.env.example)

### Documentation
- Comprehensive wiki covering all WAPI operations
- API reference with verified examples
- Security best practices
- Troubleshooting guide
- Notification methods documentation
- All examples use RFC-compliant test data

### Security
- No sensitive data in repository
- All credentials stored securely
- Automated security checks in CI/CD

---

## Version History

- **1.0.0** (2025-01-05) - Initial public release with complete documentation

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner
- **PATCH** version for backward compatible bug fixes

### Version Stages

- **0.x.x** - Development/Alpha (breaking changes allowed)
- **1.x.x** - Stable release (backward compatible changes)
- **x.0.0** - Major release (may include breaking changes)

---

**Note:** This changelog is actively maintained. All changes should be documented here.
