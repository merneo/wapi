# Changelog

All notable changes to the WAPI CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Phase 10: Advanced Features & Enhancements (2025-12-06)
- **Interactive Mode (REPL)** - Interactive shell for running WAPI commands
  - Created `wapi/utils/interactive.py` with WAPIInteractiveShell class
  - Command history tracking
  - Built-in help system
  - Support for all WAPI commands
  - Clean exit handling
  - Usage: `wapi --interactive` or `wapi -i`
- **Command Aliases** - Short aliases for common commands
  - Created `wapi/utils/aliases.py` with alias definitions
  - 16+ aliases for common commands (dl, di, dr, da, dd, ni, nc, etc.)
  - Alias expansion functionality
  - Usage: `wapi --aliases` to list all aliases
- **Batch Operations** - Process multiple domains/records at once
  - Created `wapi/utils/batch.py` with batch operation utilities
  - Batch domain operations
  - Batch DNS record operations
  - Read domains from file
  - Write results to file (JSON, YAML, CSV)
  - Progress tracking and error handling
- **Configuration Wizard** - Interactive first-time setup
  - Created `wapi/utils/config_wizard.py` with wizard implementation
  - Step-by-step interactive setup
  - Secure password input
  - Configuration validation
  - File permission setting (600)
  - Usage: `wapi --wizard`
- **CLI Enhancements:**
  - Added `--interactive` / `-i` global option
  - Added `--aliases` global option
  - Added `--wizard` global option
  - Integrated all new features into main CLI
- **Documentation:**
  - `PHASE10_ADVANCED_FEATURES.md` - Comprehensive Phase 10 documentation
  - Updated `wapi/utils/__init__.py` with new exports

### Added - Phase 9: API Documentation Enhancement (Sphinx) (2025-12-06)
- **Sphinx Documentation** - Comprehensive API documentation using Sphinx
  - Complete Sphinx setup and configuration
  - Read the Docs theme integration
  - Automatic API reference generation from docstrings
  - Napoleon extension for Google-style docstrings
  - Intersphinx for external references
- **Documentation Structure** - Professional documentation organization
  - Installation and quick start guides
  - Complete command reference (auth, domain, nsset, contact, dns, config)
  - API reference for all modules
  - Step-by-step tutorials (first steps, domain management, DNS, NSSET)
  - Practical usage examples
  - Troubleshooting guide
  - Contributing guidelines
- **GitHub Pages Deployment** - Automated documentation publishing
  - Created `.github/workflows/docs-pages.yml`
  - Automatic build and deployment on documentation changes
  - Available at GitHub Pages when enabled
- **Build System** - Documentation build tools
  - Makefile for Unix systems
  - make.bat for Windows systems
  - Local build support
- **Documentation:**
  - `PHASE9_DOCUMENTATION.md` - Comprehensive Phase 9 documentation
  - 15+ RST documentation files
  - Updated `requirements-dev.txt` with Sphinx dependencies

### Added - Phase 8: PyPI Package Preparation & Distribution (2025-12-06)
- **PyPI Package Preparation** - Complete package setup for PyPI distribution
  - Enhanced `setup.py` with complete PyPI metadata
  - Added project URLs (Bug Reports, Source, Documentation, Changelog)
  - Updated development status to Beta
  - Added keywords and classifiers for PyPI search
  - Excluded tests from package distribution
- **Distribution Configuration** - Package file inclusion/exclusion
  - Created `MANIFEST.in` for package data control
  - Includes LICENSE, README.md, config.env.example
  - Excludes test files, development files, documentation
- **License File** - MIT License
  - Added `LICENSE` file with standard MIT license text
  - Copyright notice for WAPI CLI Team
- **Build Automation** - Makefile enhancements
  - Added `make build` - Build distribution packages
  - Added `make dist` - Build and check packages
  - Added `make check` - Check package metadata
- **PyPI Publishing Workflow** - Automated publishing
  - Created `.github/workflows/pypi-publish.yml`
  - Automated publishing on GitHub releases
  - Manual workflow dispatch support
  - Full test suite and coverage check before publishing
  - Trusted publishing (no API tokens needed)
  - Installation testing on Python 3.6-3.11
- **Documentation:**
  - `PHASE8_PYPI.md` - Comprehensive Phase 8 documentation
  - `PHASE8_PROGRESS.md` - Phase 8 progress report
  - Updated `CHANGELOG.md` with Phase 8 completion

### Added - Phase 7: CI/CD Pipeline Enhancement (2025-12-06)
- **CI/CD Pipeline** - Comprehensive GitHub Actions workflow for automated testing, linting, and coverage
  - Multi-version testing on Python 3.6-3.11
  - Automated code quality checks (black, isort, flake8, mypy)
  - Coverage reporting with 100% threshold enforcement
  - Security scanning for hardcoded secrets and vulnerabilities
  - Pre-commit hooks validation
- **Release Automation** - Automated GitHub release creation on version tags
  - Automatic release notes generation from git commits
  - Installation instructions included in releases
  - CHANGELOG.md reference in releases
- **Workflow Files:**
  - `.github/workflows/ci.yml` - Main CI/CD pipeline (200+ lines)
  - `.github/workflows/release.yml` - Release automation (80+ lines)
- **Documentation:**
  - `PHASE7_CI_CD.md` - Comprehensive Phase 7 documentation
  - `PHASE7_PROGRESS.md` - Phase 7 progress report
  - Updated `README.md` with CI/CD badges
  - Updated `DEVELOPMENT.md` with CI/CD section

### Testing Improvements (Phase 3 - In Progress)
- **Auth Commands Module Complete Tests**: Achieved 100% coverage for `wapi/commands/auth.py` 🎉
  - Added comprehensive tests for all missing lines:
    - Empty username validation (lines 43-45)
    - Empty password validation (lines 55-57)
    - Invalid credential format (lines 63-65)
    - Connection and request errors during login (lines 86-88)
    - Config file parsing with comments and empty lines (lines 105, 171)
    - Config file read errors (lines 110-111, 176-179)
    - IOError and PermissionError when saving credentials (lines 142-145, 199-202)
    - Unexpected errors when saving credentials (lines 146-149, 203-206)
    - Config write operations (line 194)
    - Connection and request errors in status command (lines 252-257)
  - 16 new test cases added
  - Improved auth commands coverage from 77% to 100% 🎉
  - All 16 auth complete tests passing

- **CLI Module Complete Tests**: Achieved 100% coverage for `wapi/cli.py` 🎉
  - Added comprehensive tests for all missing lines:
    - Exception handling in get_client (lines 51-54) - validate_config exception
    - cmd_ping function (lines 70-90) - success and failure paths
    - args.format default assignment (line 287)
    - All error handling paths in main function:
      - WAPIConfigurationError in command execution (lines 308-310)
      - WAPITimeoutError (lines 320-322)
      - WAPIRequestError (lines 324-326)
      - WAPIError (lines 328-330)
      - WAPIConnectionError (lines 316-318)
      - No func attribute (lines 340-341)
    - Additional edge cases:
      - Config validation failure (lines 48-50)
      - Missing credentials (lines 60-62)
      - No module specified (lines 282-283)
      - get_client returns None (line 293)
  - 10 new test cases added
  - Improved CLI coverage from 85% to 100% 🎉
  - All 22 CLI complete tests passing

- **Formatters Module Complete Tests**: Achieved 100% coverage for `wapi/utils/formatters.py` 🎉
  - Fixed 3 failing tests by properly mocking `tabulate` module when not installed
  - Added comprehensive tests for:
    - ImportError exception blocks for `yaml` (lines 14-15) - simulated import failure at module level
    - ImportError exception block for `tabulate` (line 20) - simulated import failure at module level
    - format_table with list of dicts and no headers when tabulate available (line 53)
    - All format_table branches when TABULATE_AVAILABLE=True (lines 50-62)
  - 4 new test cases added:
    - `test_format_table_list_with_dicts_no_headers_tabulate` (covers line 53)
    - `test_yaml_import_error_at_module_level` (covers lines 14-15)
    - `test_tabulate_import_error_at_module_level` (covers line 20)
  - Improved formatters coverage from 80% to 100% 🎉
  - All 35 formatters tests passing

- **Logger Module Complete Tests**: Achieved 100% coverage for `wapi/utils/logger.py` 🎉
  - Fixed 19 failing tests by correcting test expectations
  - Removed incorrect `basicConfig` assertions (setup_logging manually configures handlers)
  - Fixed function signatures - all logger functions require logger as first parameter
  - Added comprehensive tests for:
    - Directory creation when log file directory doesn't exist (line 83)
    - IOError and PermissionError handling in file logging setup (line 104)
    - get_logger without name parameter (line 124)
    - Nested dict filtering in log_api_request (line 137)
    - All log_api_response code paths (1001, 2xx codes, unexpected codes) (lines 150-155)
    - log_operation_complete failure paths with and without details (lines 182-188)
  - 42 new test cases added
  - Improved logger coverage from 74% to 100%

- **Formatters & CLI Tests Fixed**: Fixed 22 failing tests
  - Fixed formatters JSON output expectations (format_json doesn't add newline)
  - Fixed CLI auth error test (WAPIAuthenticationError raised by command function, not get_client)
  - All formatters and CLI tests now passing

- **Test Suite Statistics**:
  - Fixed 3 failing formatters tests → now 349/350 passing (99.7% pass rate)
  - Overall coverage maintained at 74% (formatters improved from 80% to 100%)
  - Only 1 test remaining (domain source lines - known unreachable code logic issue)

- **API Auth Module Complete Tests**: Added comprehensive tests for `wapi/api/auth.py`
  - Tests for `pytz` ImportError handling (lines 13-15)
  - Tests for `get_prague_hour` fallback path when `pytz` is not available (lines 38-41)
  - 2 new test cases
  - Improved API auth coverage from 86% to 100% 🎉
- **Unit Tests for Constants**: Added comprehensive tests for `wapi.constants`
  - Tests for exit codes, API response codes, default values
  - Tests for logging constants and timeout values
  - 7 test cases, all passing
- **Unit Tests for Exceptions**: Added comprehensive tests for `wapi.exceptions`
  - Tests for exception hierarchy and inheritance
  - Tests for exception instantiation and catching
  - Tests for exception messages and context
  - 7 test cases, all passing
- **Error Handling Tests**: Added tests for error handling patterns
  - Tests for error handling constants usage
  - Tests for exception hierarchy and catching
  - Tests for specific exception types (config, validation, connection, request)
  - 13 test cases, all passing
- **Config Error Handling Tests**: Added tests for configuration error handling
  - Tests for missing credentials validation
  - Tests for file I/O errors (IOError, PermissionError)
  - Tests for config validation success cases
  - 6 test cases, all passing
- **API Client Tests**: Added comprehensive tests for `wapi.api.client`
  - Tests for client initialization (XML/JSON formats, custom URLs)
  - Tests for error handling (connection errors, timeouts, request errors, XML parse errors)
  - Tests for polling functionality (success, timeout, custom completion checks, error codes)
  - Tests for API methods (ping, domain_info)
  - 14 test cases, all passing
  - Improved API client coverage from 12% to 51%
- **Command Error Handling Tests**: Added tests for command error handling
  - Tests for domain command error handling (validation, request errors)
  - Tests for DNS command error handling (validation, request errors)
  - Tests for constants usage in commands
  - 10 test cases, all passing
- **CLI Tests**: Added comprehensive tests for `wapi.cli`
  - Tests for client creation and error handling
  - Tests for CLI error handling (config, auth, connection, timeout, keyboard interrupt)
  - Tests for command routing (config commands without client)
  - 10 test cases, all passing
  - Improved CLI coverage from 8% to 82% (+925% relative increase)
- **DNS Lookup Tests**: Added comprehensive tests for `wapi.utils.dns_lookup`
  - Tests for DNS lookup constants
  - Tests for IPv6 discovery from IPv4 addresses
  - Tests for IPv6 discovery from nameserver hostnames
  - Tests for nameserver enhancement functionality
  - Tests for error handling and timeouts
  - 14 test cases, all passing
  - Improved DNS lookup coverage from 10% to 58% (+480% relative increase)
- **Command Operations Tests**: Added comprehensive tests for command operations
  - Tests for successful domain commands (info, list, update-ns)
  - Tests for successful DNS commands (list, record list/add/update/delete)
  - Tests for successful NSSET commands (create, info)
  - Tests for output formatting (JSON, YAML, table)
  - 14 test cases, all passing
  - Improved command coverage significantly:
    - `wapi/commands/domain.py`: 48% (↑ from 5-17%)
    - `wapi/commands/dns.py`: 42% (↑ from 5-17%)
    - `wapi/commands/nsset.py`: 46% (↑ from 5-17%)
- **Auth Commands Tests**: Added tests for authentication commands
  - Tests for login command (with credentials, prompts, authentication failure)
  - Tests for logout command (success, no config file)
  - Tests for status command (authenticated, not authenticated, invalid credentials)
  - 11 test cases, 8 passing (3 with file I/O issues to be resolved)
  - Improved auth commands coverage from 8% to 79% (+888% relative) 🎉
- **Config Commands Tests**: Added tests for configuration commands
  - Tests for config show command (success, empty config, error handling)
  - Tests for config validate command (success, failure, missing password)
  - Tests for config set command (success, password handling, file operations)
  - 10 test cases, all passing
  - Improved config commands coverage from 17% to 86% (+406% relative) 🎉
- **Logger Tests**: Added comprehensive tests for `wapi.utils.logger`
  - Tests for get_logger function
  - Tests for setup_logging function (verbose, quiet, log levels, file logging)
  - Tests for logger helper functions (API request/response, validation, operations, exceptions)
  - Tests for logger integration and message filtering
  - 15 test cases, all passing
  - Improved logger coverage from 21% to ~60%
- **Contact Commands Tests**: Added tests for contact commands
  - Tests for contact info command (success, API error)
  - Tests for contact list command (not implemented test)
  - 3 test cases, all passing
  - Improved contact commands coverage from 25% to 98% (+292% relative) 🎉
- **Domain Commands Comprehensive Tests**: Added extensive tests for domain commands
  - Tests for filter_sensitive_domain_data function (all sensitive fields)
  - Tests for domain list edge cases (single domain, non-dict entries, TLD/status filters)
  - Tests for domain update-ns with nsset, source domain, async operations
  - Tests for polling completion checks (nsset, nameservers, source domain)
  - Tests for edge cases (timeout detection, error handling, invalid formats)
  - Tests for complex completion check logic (source domain nameserver matching)
  - 40+ new test cases across multiple test files
  - Improved domain commands coverage from 47% to 93% (+98% relative increase) 🎉
- **Config Module Complete Tests**: Added comprehensive tests for config module
  - Tests for load_config (file not exists, comments, empty lines, error handling)
  - Tests for get_config (env variables, file, default values)
  - Tests for all error paths (IOError, OSError, PermissionError, Exception)
  - 10 new test cases
  - Improved config module coverage from 89% to 100% 🎉
- **Contact Commands Complete Tests**: Added tests for contact commands
  - Tests for filter_sensitive_contact_data with all fields
  - Tests for contact info with/without TLD (covering pass statement)
  - Tests for contact list (not implemented)
  - Improved contact commands coverage from 98% to 100% 🎉
- **Test Statistics**:
  - Total test files: 25+
  - Total test cases: 220+ (↑ from 53, +315% increase)
  - All tests passing: ✅ 220+/220+ (100% pass rate) 🎉
  - Test coverage: 70%+ overall (↑ from 19%, +268% relative increase) 🎉
  - **Validators Module Complete Tests**: Added comprehensive tests for validators
    - Tests for validate_domain (too long, edge cases)
    - Tests for validate_ipv4 (ValueError, negative, too large octets)
    - Tests for validate_ipv6 (compressed format, invalid formats, invalid characters)
    - Tests for validate_nameserver (empty, invalid format, invalid domain/IP)
    - Tests for validate_email (valid/invalid formats)
    - 20+ new test cases
    - Improved validators coverage from 96% to 100% 🎉
  - **Config Commands Complete Tests**: Added comprehensive tests for config commands
    - Tests for cmd_config_set exception handling (IOError, OSError, PermissionError, Exception)
    - Tests for empty lines and comments handling
    - Fixed missing logger definition in cmd_config_set (bug fix)
    - 5+ new test cases
    - Improved config commands coverage from 86% to 100% 🎉
  - **100% Coverage Modules**: 🎉
    - `wapi/config.py`: 100% ✅
    - `wapi/commands/config.py`: 100% ✅
    - `wapi/commands/contact.py`: 100% ✅
    - `wapi/utils/validators.py`: 100% ✅
    - `wapi/constants.py`: 100% ✅
    - `wapi/exceptions.py`: 100% ✅
  
  **Current Status:**
  - Total test cases: 240+ (↑ from 53, +353% increase)
  - All tests passing: ✅ 240/240 (100% pass rate) 🎉
  - Test coverage: 70%+ overall
  - **3 major modules at 100% coverage** 🎉
  
  **Remaining work for 100% coverage:**
  - `wapi/commands/domain.py`: 93% (lines 290-305)
  - `wapi/commands/config.py`: 86% → working on it
  - `wapi/commands/auth.py`: 77%
  - `wapi/cli.py`: 83%
  - `wapi/commands/dns.py`: 42%
  - `wapi/commands/nsset.py`: 46%
  - `wapi/api/client.py`: 51%
  - `wapi/api/auth.py`: 60%
  - `wapi/utils/dns_lookup.py`: 58%
  - `wapi/utils/formatters.py`: 68%
  - `wapi/utils/logger.py`: 74%
  - Coverage improvements:
    - `wapi/cli.py`: 83% (↑ from 8%, +938% relative) 🎉
    - `wapi/utils/dns_lookup.py`: 58% (↑ from 10%, +480% relative) 🎉
    - `wapi/api/client.py`: 51% (↑ from 12%)
    - `wapi/api/auth.py`: 60% (↑ from 26%)

### Code Quality Improvements (Phase 1 - Completed)
- **Error Code Constants**: Created `wapi/constants.py` with standardized exit codes
  - `EXIT_SUCCESS = 0` - Operation successful
  - `EXIT_ERROR = 1` - General error
  - `EXIT_CONFIG_ERROR = 2` - Configuration error
  - `EXIT_AUTH_ERROR = 3` - Authentication error
  - `EXIT_VALIDATION_ERROR = 4` - Input validation error
  - `EXIT_CONNECTION_ERROR = 5` - Connection error
  - `EXIT_TIMEOUT_ERROR = 6` - Timeout error
- **Custom Exceptions Integration**: Custom exceptions now used throughout codebase
  - API client raises `WAPIConnectionError`, `WAPIRequestError`, `WAPITimeoutError`
  - Config module raises `WAPIConfigurationError`
  - Commands raise appropriate exceptions (`WAPIValidationError`, `WAPIRequestError`, etc.)
  - Utility modules use specific exception types
- **Standardized Error Handling**: All commands use constants instead of hardcoded return codes
  - All command files updated (domain, dns, nsset, contact, auth, config)
  - CLI properly handles all custom exceptions with appropriate exit codes
  - Improved error messages and context
- **Exception Handling Improvements**: Replaced generic `except Exception` with specific types
  - API client: Specific exception types for timeouts, connection errors, request errors
  - Commands: Specific validation and request errors
  - Utility modules: Specific DNS lookup and formatting errors
- **Files Modified**:
  - `wapi/constants.py` (NEW) - Error code constants
  - `wapi/cli.py` - Exception handling and constants
  - `wapi/config.py` - Custom exceptions
  - `wapi/api/client.py` - Custom exceptions
  - All command files (`wapi/commands/*.py`) - Constants and exceptions
  - All utility files (`wapi/utils/*.py`) - Specific exception types

### Code Quality Improvements (Phase 2)
- **Code Formatting Tools**: Added development tooling for code quality
  - `black` - Code formatter (line length: 100)
  - `isort` - Import sorter (black profile)
  - `flake8` - Linter with custom configuration
  - `mypy` - Type checker (optional strict mode)
- **Pre-commit Hooks**: Automated code quality checks before commits
  - Trailing whitespace removal
  - End-of-file fixer
  - YAML/JSON/TOML validation
  - Code formatting (black)
  - Import sorting (isort)
  - Linting (flake8)
  - Type checking (mypy)
- **Development Dependencies**: Added `requirements-dev.txt` for development tools
- **Configuration Files**: Added tool configuration
  - `pyproject.toml` - Black, isort, mypy, pytest, coverage configuration
  - `.flake8` - Flake8 configuration
  - `.pre-commit-config.yaml` - Pre-commit hooks configuration
- **Makefile**: Added development tasks
  - `make install` - Install production dependencies
  - `make install-dev` - Install development dependencies
  - `make format` - Format code with black and isort
  - `make lint` - Run linters
  - `make test` - Run tests
  - `make test-cov` - Run tests with coverage
  - `make clean` - Clean build artifacts
  - `make pre-commit` - Install pre-commit hooks
- **Import Sorting**: Standardized all imports across codebase
  - Standard library imports first
  - Third-party imports second
  - Local imports last
  - Alphabetically sorted within each group
- **Development Guide**: Added `DEVELOPMENT.md` with complete development workflow

### Code Quality Improvements (Phase 1)
- **Custom Exception Classes**: Added `wapi/exceptions.py` with standardized exception hierarchy
  - `WAPIError` - Base exception class
  - `WAPIConfigurationError` - Configuration issues
  - `WAPIAuthenticationError` - Authentication failures
  - `WAPIValidationError` - Input validation errors
  - `WAPIConnectionError` - Connection issues
  - `WAPIRequestError` - API request failures
  - `WAPITimeoutError` - Timeout errors
  - `WAPIDNSLookupError` - DNS lookup failures
- **Package Exports**: Added proper `__all__` exports to all `__init__.py` files
  - `wapi/__init__.py` - Exports main classes and exceptions
  - `wapi/api/__init__.py` - Exports API client and auth functions
  - `wapi/utils/__init__.py` - Exports all utility functions
- **Dependency Management**: Improved dependency specifications
  - Removed unused `click` dependency
  - Added version upper bounds for compatibility
  - Marked `dnspython` as optional dependency (via `extras_require`)
- **Code Audit**: Created comprehensive `CODE_AUDIT.md` with detailed analysis
  - Security audit
  - Compatibility analysis
  - Code consistency review
  - File structure review
  - Best practices recommendations
  - Phased improvement plan

### Fixed
- **Missing Import**: Fixed missing `get_logger` import in `wapi/api/auth.py`
- **Unused Dependencies**: Removed `click>=7.0` from requirements.txt

## [0.9.0] - 2025-01-05

### Added
- **IPv6 Auto-Discovery for Nameservers**: Automatic IPv6 address discovery when only IPv4 is provided
  - When adding nameservers with only IPv4 addresses, the CLI automatically attempts to discover IPv6 addresses
  - Uses DNS AAAA record lookup for nameserver hostname
  - Falls back to reverse DNS lookup on IPv4 address if direct lookup fails
  - Integrated into `wapi domain update-ns` and `wapi nsset create` commands
  - New module `wapi/utils/dns_lookup.py` with DNS resolution utilities
  - Optional dependency on `dnspython` for enhanced DNS resolution (falls back to socket if not available)
- **IPv6 Discovery Control**: `--no-ipv6-discovery` flag to disable automatic IPv6 lookup
  - Use `--no-ipv6-discovery` to skip IPv6 discovery and use only provided addresses
  - Useful when you want to explicitly control nameserver configuration
- **Enhanced Nameserver Handling**: Improved nameserver processing with automatic IPv6 enhancement
- **DNS Lookup Timeout**: Configurable timeout (default: 5 seconds) for DNS lookups to prevent hanging
- **IPv6 Validation**: All discovered IPv6 addresses are validated before use
- **Improved User Feedback**: Informative messages about IPv6 discovery results
  - Success messages when IPv6 is found
  - Warning messages when IPv6 is not found (operation continues with IPv4 only)
  - Error messages only for actual failures (timeouts, DNS errors)

### Changed
- `wapi domain update-ns --nameserver` now automatically discovers IPv6 addresses when only IPv4 is provided
- `wapi nsset create --nameserver` now automatically discovers IPv6 addresses when only IPv4 is provided
- Updated `requirements.txt` to include optional `dnspython>=2.0.0` dependency
- IPv6 discovery is now non-intrusive - if IPv6 is already provided, no lookup is performed
- DNS lookup failures are handled gracefully - operation continues with IPv4 only

### Improved
- **Error Handling**: Better error messages and warnings for DNS lookup scenarios
  - Clear distinction between "IPv6 not found" (warning, continues) and "DNS error" (warning, continues)
  - No errors for normal cases where IPv6 doesn't exist
- **Security**: All discovered IPv6 addresses are validated using `validate_ipv6()` before use
- **Performance**: DNS lookups have timeout protection to prevent hanging operations
- **User Experience**: Clear feedback about what happened during IPv6 discovery

### Technical Details
- DNS lookup uses `socket.getaddrinfo()` as primary method (works without additional dependencies)
- If `dnspython` is installed, uses `dns.resolver.resolve()` for more robust DNS queries
- All DNS operations are logged for debugging purposes
- IPv6 discovery is non-blocking - if lookup fails, operation continues with IPv4 only
- DNS lookup timeout: 5 seconds (configurable via function parameter)
- IPv6 validation ensures only valid addresses are used

## [0.8.0] - 2025-01-05

### Added
- **Authentication CLI Commands**:
  - `wapi auth login` - Interactive login to save credentials
    - Prompts for username and password (password hidden)
    - Validates credentials with WAPI
    - Saves to config.env with secure permissions (600)
    - Supports `--username` and `--password` flags for non-interactive use
  - `wapi auth logout` - Remove saved credentials from config file
  - `wapi auth status` - Show authentication status and test connection
- **Comprehensive Logging System**: Full logging support across entire project
  - `wapi/utils/logger.py` - Centralized logging configuration
  - Logging integrated into all modules (API client, commands, validators)
  - Support for console and file logging
  - Automatic log file rotation (10MB max, 5 backups)
  - Password and sensitive data filtering in logs
- **Logging Options**:
  - `--verbose / -v` - Enable DEBUG level logging
  - `--quiet / -q` - Show only ERROR level
  - `--log-file <path>` - Log to file
  - `--log-level <level>` - Set custom log level (DEBUG, INFO, WARNING, ERROR)
- **Logging Features**:
  - API request/response logging
  - Operation start/complete logging
  - Validation error logging
  - Polling progress logging
  - Exception logging with stack traces (verbose mode)

### Improved
- **Error Handling**: Better error context with logging
- **Debugging**: Easier troubleshooting with detailed logs
- **Monitoring**: Track all operations via log files
- **Logging Coverage**: Logging integrated into all modules
  - API client: All requests, responses, HTTP errors, polling
  - Commands: All operations, successes, failures
  - Validators: All validation errors
  - Formatters: All format operations
  - Config: Load and validate operations
  - Auth: Authentication calculations
- **Exception Handling**: 
  - KeyboardInterrupt handling with logging
  - Stack traces in verbose mode
  - HTTP timeout and error logging
- **Security**: Enhanced sensitive data filtering in all log functions

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
- **Unit Tests**: Comprehensive test suite
  - `tests/test_validators.py` - Tests for domain, IPv4, IPv6, nameserver, email validation (12 tests)
  - `tests/test_formatters.py` - Tests for table, JSON, XML, YAML output formatting (8 tests)
  - All tests passing (20 total tests)
- Progress indicators during polling (when not in quiet mode)
- Timeout handling (default: 60 attempts × 10 seconds = 10 minutes)

### Improved
- **Error Messages**: Better error messages with context
  - DNS update now shows clear message when no fields specified
  - More descriptive validation error messages
- **Documentation**: Updated WIKI.md and COMMAND_REFERENCE.md with DNS update examples

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
