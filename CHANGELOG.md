# Changelog

All notable changes to the WAPI CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
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
- Domain info tested with armlab.cz domain
- Ping command verified working

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
