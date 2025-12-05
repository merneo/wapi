# WAPI CLI Command Reference

**Quick reference for all WAPI CLI commands**

## Command Structure

```
wapi [GLOBAL_OPTIONS] <MODULE> <COMMAND> [ARGUMENTS] [OPTIONS]
```

## Global Options

```
--config <file>     Configuration file (default: config.env)
--format <format>   Output format: json, xml, table, yaml (default: table)
--verbose / -v      Verbose output (DEBUG level logging)
--quiet / -q        Quiet mode (ERROR level only)
--log-file <path>   Log to file (optional, auto-rotates)
--log-level <level> Set log level: DEBUG, INFO, WARNING, ERROR
--help / -h         Show help
```

## Domain Module

### List Domains
```bash
wapi domain list
wapi domain list --tld cz
wapi domain list --status ok
wapi domain list --format json
```

### Domain Information
```bash
wapi domain info example.com
wapi domain info example.com --format json
```

### Update Nameservers
```bash
# Using existing NSSET
wapi domain update-ns example.com --nsset MY-NSSET

# With new nameservers
wapi domain update-ns example.com \
  --nameserver ns1.example.com:192.0.2.1:2001:db8::1 \
  --nameserver ns2.example.com:192.0.2.2:2001:db8::2

# Copy from another domain
wapi domain update-ns example.com --source-domain example.org

# Wait for async completion
wapi domain update-ns example.com --nsset MY-NSSET --wait
```

### Domain Operations (if supported)
```bash
wapi domain create example.com
wapi domain transfer example.com
wapi domain renew example.com
wapi domain delete example.com
```

## NSSET Module

### List NSSETs
```bash
wapi nsset list
wapi nsset list --format json
```

### NSSET Information
```bash
wapi nsset info MY-NSSET
wapi nsset info MY-NSSET --format json
```

### Create NSSET
```bash
wapi nsset create MY-NSSET \
  --nameserver ns1.example.com:192.0.2.1:2001:db8::1 \
  --nameserver ns2.example.com:192.0.2.2:2001:db8::2 \
  --tld cz \
  --tech-c MY-CONTACT \
  --wait
```

### NSSET Operations (if supported)
```bash
wapi nsset update MY-NSSET --nameserver ns3.example.com:192.0.2.3
wapi nsset delete MY-NSSET
```

## Contact Module

### List Contacts
```bash
wapi contact list
wapi contact list --format json
```

### Contact Information
```bash
wapi contact info MY-CONTACT
```

### Contact Operations (if supported)
```bash
wapi contact create
wapi contact update MY-CONTACT
```

## DNS Module (if supported)

### List DNS Records
```bash
wapi dns list example.com
```

### DNS Record Operations
```bash
# Add DNS record
wapi dns add example.com --type A --name www --value 192.0.2.1

# Update DNS record
wapi dns update example.com --id 123 --value 192.0.2.2
wapi dns update example.com --id 123 --name www --value 192.0.2.3 --ttl 7200 --wait

# Delete DNS record
wapi dns delete example.com --id 123
```

## Auth Module

### Login (Interactive)
```bash
# Interactive login (prompts for username and password)
wapi auth login

# Login with username provided
wapi auth login --username user@example.com

# Login with both (not recommended)
wapi auth login --username user@example.com --password mypassword
```

### Logout
```bash
wapi auth logout
```

### Check Status
```bash
wapi auth status
```

### Test Connection
```bash
wapi auth ping
```

## Config Module

### Show Configuration
```bash
wapi config show
```

### Set Configuration
```bash
wapi config set username user@example.com
wapi config set password mypassword
```

### Remove Configuration
```bash
wapi config unset username
```

### Validate Configuration
```bash
wapi config validate
```

## Examples

### Complete Workflow
```bash
# 1. Test connection
wapi auth ping

# 2. List all domains
wapi domain list

# 3. Get domain information
wapi domain info example.com

# 4. Create NSSET
wapi nsset create MY-NSSET \
  --nameserver ns1.example.com:192.0.2.1:2001:db8::1 \
  --nameserver ns2.example.com:192.0.2.2:2001:db8::2

# 5. Assign NSSET to domain
wapi domain update-ns example.com --nsset MY-NSSET --wait

# 6. Verify update
wapi domain info example.com
```

### Using Different Formats
```bash
# Table format (default, human-readable)
wapi domain list

# JSON format (for scripting)
wapi domain list --format json

# XML format
wapi domain list --format xml

# YAML format
wapi domain list --format yaml

# Save to file
wapi domain list --format json --output domains.json
```

### Error Handling
```bash
# Verbose output for debugging
wapi domain info example.com --verbose

# Quiet mode (errors only)
wapi domain list --quiet

# Custom config file
wapi --config /path/to/config.env domain list
```

## Command Aliases

Some commands support short aliases:

```bash
# List commands
wapi domain -l          # Same as: wapi domain list
wapi nsset -l            # Same as: wapi nsset list
wapi contact -l          # Same as: wapi contact list

# Help
wapi -h                  # Same as: wapi --help
wapi domain -h           # Show domain module help
wapi domain info -h      # Show info command help
```

## Output Examples

### Table Format (Default)
```
Domain          Status    Expires      NSSET
example.com     ok        2025-12-31   NS-EXAMPLE-COM-123
example.org     ok        2026-01-15   NS-EXAMPLE-ORG-456
```

### JSON Format
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

## Notes

- All examples use RFC-compliant test data (example.com, 192.0.2.0/24)
- Commands marked "(if supported)" depend on WEDOS WAPI capabilities
- Use `--wait` flag for async operations when POLL Queue is enabled
- Use `--format json` for scripting and automation
- See `CLI_DESIGN_AUDIT.md` for complete specifications
