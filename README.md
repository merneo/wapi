# WEDOS WAPI Documentation - Complete Python Client Guide

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/merneo/wapi)
[![Documentation](https://img.shields.io/badge/Documentation-WIKI-green)](WIKI.md)
[![Python](https://img.shields.io/badge/Python-3.6+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CI/CD](https://github.com/merneo/wapi/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/merneo/wapi/actions)
[![Coverage](https://codecov.io/gh/merneo/wapi/branch/master/graph/badge.svg)](https://codecov.io/gh/merneo/wapi)

**WAPI CLI - Command-line interface for WEDOS WAPI** with verified commands, comprehensive documentation, and best practices. Manage WEDOS domains, NSSETs, contacts, and DNS records from the command line with a user-friendly interface.

## What is WEDOS WAPI?

WEDOS WAPI (Web API) is a RESTful API for managing domain registrations, DNS settings, nameservers, and other domain-related operations through WEDOS hosting services. This repository provides comprehensive documentation and examples for integrating WEDOS WAPI into Python applications.

**Key Features:**
- ✅ Complete CLI tool with 20+ commands
- ✅ Domain management (list, info, update nameservers)
- ✅ Domain availability search with automatic WHOIS fallback
- ✅ NSSET operations (create, info)
- ✅ DNS record management (list, add, delete)
- ✅ Contact information retrieval
- ✅ Configuration management
- ✅ Multiple output formats (table, JSON, XML, YAML)
- ✅ Sensitive data filtering
- ✅ Production-ready and fully tested
- ✅ **100% test coverage** (822 tests, all passing)

## 📚 Complete Documentation

**👉 [Read the Complete Wiki Documentation](WIKI.md)**

### Implementation & Development

- **[Implementation Phases](IMPLEMENTATION_PHASES.md)** - Phase-by-phase implementation plan ordered by complexity
- **[CLI Design Audit](CLI_DESIGN_AUDIT.md)** - Complete CLI design specification
- **[Implementation Files](IMPLEMENTATION_FILES.md)** - Detailed file list and specifications
- **[Command Reference](COMMAND_REFERENCE.md)** - Quick command reference guide
- **[Changelog](CHANGELOG.md)** - Active changelog with semantic versioning
- **[Workflow Guide](WORKFLOW.md)** - Safe repository development workflow
- **[Coverage Report](COVERAGE_100_PERCENT.md)** - 100% test coverage achievement report
- **[Quality Audit](QUALITY_AUDIT.md)** - Comprehensive quality audit

Our comprehensive wiki documentation (948+ lines) covers everything you need to work with WEDOS WAPI in Python:

### Core Topics
- **Quick Start Guide** - Get up and running in minutes
- **Installation Instructions** - Python dependencies and setup
- **Configuration Guide** - Environment variables and config files
- **Basic Usage Examples** - Your first API calls
- **Command-Line Tools** - Ready-to-use scripts

### Advanced Features
- **API Reference** - Complete method documentation
- **Common Operations** - Real-world use cases with code examples
- **Asynchronous Operations** - Handling POLL Queue and notification methods
- **XML vs JSON Formats** - When to use which format
- **Authentication** - Understanding WEDOS WAPI security

### Support & Best Practices
- **Troubleshooting Guide** - Common errors and solutions
- **Security Best Practices** - Protecting credentials and API keys
- **Standards Compliance** - RFC-compliant examples and practices

**All examples use academic test data** (example.com, RFC 5737 IPs) and have been verified on production WAPI systems.

## 🚀 Quick Start Guide

Get started with WEDOS WAPI in Python in just a few steps:

### Step 1: Install the Package
```bash
git clone https://github.com/merneo/wapi.git
cd wapi
pip install -e .
```

### Step 2: Configure Your Credentials
Copy the example configuration file and add your WEDOS WAPI credentials:
```bash
cp config.env.example config.env
# Edit config.env with your WAPI username and password
chmod 600 config.env  # Secure the file
```

### Step 3: Test Your Connection
```bash
wapi auth ping
```

### Step 4: Start Using the CLI
```bash
# List your domains
wapi domain list

# Get domain information
wapi domain info example.com

# Check availability with WHOIS fallback
wapi search example.com
wapi -s example.com  # short alias

# List DNS records
wapi dns records example.com
```

**For detailed instructions, see the [Complete Wiki](WIKI.md).**

## 📖 Repository Contents

This repository contains everything you need to work with WEDOS WAPI in Python:

### Documentation Files

- **[WIKI.md](WIKI.md)** - Comprehensive documentation (948+ lines)
  - **Quick Start** - Verify installation and test connection
  - **Installation** - Python setup and dependencies
  - **Configuration** - Environment variables and config files
  - **Basic Usage** - Initialize API client and make first calls
  - **Command-Line Tools** - Ready-to-use scripts for domain management
  - **API Reference** - Complete method documentation with examples
  - **Common Operations** - Real-world use cases (domain info, nameserver updates)
  - **Advanced Features** - Asynchronous operations, notification methods, polling
  - **Troubleshooting** - Common errors and solutions
  - **Security Best Practices** - Protecting credentials and API access

### Configuration Files

- **config.env.example** - Configuration template with all required settings
- **requirements.txt** - Python package dependencies (requests library)
- **.gitignore** - Excludes sensitive configuration files from version control

### Automation

- **.github/workflows/docs.yml** - GitHub Actions workflow for documentation validation

## 🔒 Security & Privacy

This repository follows security best practices:

- ✅ **No sensitive data** - No credentials, real domains, or IP addresses in repository
- ✅ **RFC-compliant examples** - All examples use standard test data:
  - Domains: `example.com`, `example.org` (RFC 2606)
  - IPv4: `192.0.2.0/24` (RFC 5737)
  - IPv6: `2001:db8::/32` (RFC 3849)
- ✅ **Secure credential storage** - Credentials stored in `config.env` (gitignored)
- ✅ **File permissions** - Configuration files use restricted permissions (600)
- ✅ **Automated checks** - GitHub Actions verify no sensitive data in commits

**See [Security Best Practices](WIKI.md#security-best-practices) in the wiki for detailed guidelines.**

## 📝 Standards & Compliance

This documentation adheres to industry standards and best practices:

### Internet Standards (RFC)
- **[RFC 2606](https://tools.ietf.org/html/rfc2606)** - Reserved Top-Level DNS Names (example.com, example.org)
- **[RFC 5737](https://tools.ietf.org/html/rfc5737)** - IPv4 Address Blocks Reserved for Documentation (192.0.2.0/24, 198.51.100.0/24)
- **[RFC 3849](https://tools.ietf.org/html/rfc3849)** - IPv6 Address Prefix Reserved for Documentation (2001:db8::/32)
- **[RFC 1918](https://tools.ietf.org/html/rfc1918)** - Address Allocation for Private Internets

### Documentation Standards
- **US English** - All documentation written in US English spelling and terminology
- **Technical accuracy** - All examples verified on production WAPI systems
- **Accessibility** - Clear structure, proper headings, and comprehensive table of contents

### Code Quality
- **Python 3.6+** - Compatible with modern Python versions
- **Type hints** - Code examples include type information where applicable
- **Error handling** - Examples demonstrate proper error handling

## 🔗 Official Resources & References

### WEDOS Documentation
- **[WEDOS WAPI Manual](https://kb.wedos.cz/wapi-manual/)** - Official WEDOS WAPI documentation
- **[WEDOS WAPI Commands Reference](https://kb.wedos.cz/wapi-manual/#wedos-api)** - Complete list of available WAPI commands
- **[WEDOS Knowledge Base](https://kb.wedos.cz/)** - Additional WEDOS resources and guides

### Related Standards
- **[RFC 2606](https://tools.ietf.org/html/rfc2606)** - Reserved Top-Level DNS Names
- **[RFC 5737](https://tools.ietf.org/html/rfc5737)** - IPv4 Documentation Addresses
- **[RFC 3849](https://tools.ietf.org/html/rfc3849)** - IPv6 Documentation Addresses

### Python Resources
- **[Python Requests Library](https://requests.readthedocs.io/)** - HTTP library used by the client
- **[Python Documentation](https://docs.python.org/3/)** - Official Python documentation

## 📊 Repository Status & Maintenance

- **Last Updated**: 2025-12-06
- **Current Version**: 1.0.0 (Documentation release)
- **Documentation Status**: Complete and verified
- **Examples Status**: All tested on production WAPI systems
- **Code Quality**: Production ready
- **Security**: No sensitive data, automated checks enabled
- **Standards Compliance**: RFC-compliant examples, US English documentation
- **Versioning**: [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Actively maintained

### Implementation Status

- **Phase 0**: Completed (Project setup)
- **Phase 1**: Completed (Config & Auth)
- **Phase 2**: Completed (API Client)
- **Phase 3**: Completed (CLI Framework)
- **Phase 4**: Completed (Domain Module)
- **Phase 5**: Completed (NSSET Module)
- **Phase 6**: Completed (Additional Modules)
- **Test Coverage**: 100% (822 tests)

**See [IMPLEMENTATION_PHASES.md](IMPLEMENTATION_PHASES.md) for detailed phase breakdown.**

## 🎯 Use Cases

This documentation is perfect for:

- **Domain Management** - Automate domain registration, transfers, and updates
- **DNS Configuration** - Programmatically manage nameservers and DNS records
- **Bulk Operations** - Handle multiple domains efficiently
- **Integration Projects** - Integrate WEDOS services into existing Python applications
- **Automation Scripts** - Create automated workflows for domain management
- **Learning WAPI** - Understand WEDOS WAPI through comprehensive examples

## 🤝 Contributing

This repository contains documentation only. For improvements or corrections:

1. Review the [WIKI.md](WIKI.md) documentation
2. Verify all examples work correctly
3. Ensure no sensitive data is included
4. Follow RFC standards for examples
5. Use US English spelling and terminology

## 📄 License

This documentation is provided "as is" without warranties. Use at your own risk.

## 🔍 Keywords

WEDOS, WAPI, Python, API client, domain management, DNS, nameservers, domain registration, REST API, Python library, domain automation, WEDOS integration, domain API, Python examples, API documentation, domain hosting, Czech domains, .cz domains, domain transfer, NSSET, GLUE records, asynchronous operations, POLL Queue, notification methods

---

**👉 [Read the Complete Wiki Documentation](WIKI.md) for detailed guides, API reference, and examples.**
