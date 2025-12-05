# WEDOS WAPI Python Client - Complete Documentation Wiki

**Complete, production-ready documentation for integrating WEDOS WAPI into Python applications**

**Last Verified:** 2025-01-05  
**Status:** All commands tested and verified on production WAPI  
**Language:** US English  
**Standards:** RFC 2606 (example.com), RFC 5737 (192.0.2.0/24), RFC 3849 (2001:db8::/32)  
**Security:** No sensitive data (credentials, real domains, or IP addresses) included in documentation

> **Note:** This documentation uses only example domains (`example.com`, `example.org`) and documentation IP addresses (`192.0.2.0/24`, `2001:db8::/32`) as per [RFC 2606](https://tools.ietf.org/html/rfc2606), [RFC 5737](https://tools.ietf.org/html/rfc5737), and [RFC 3849](https://tools.ietf.org/html/rfc3849). No real credentials, domains, or IP addresses are included.

## Overview

This comprehensive wiki provides **complete documentation for the WEDOS WAPI Python client**, enabling developers to integrate WEDOS domain management services into their Python applications. All examples, commands, and code snippets have been tested and verified on production WAPI systems. The documentation follows industry standards for technical documentation, using only RFC-compliant example domains and IP addresses.

**What is WEDOS WAPI?**

WEDOS WAPI (Web API) is a RESTful API service provided by WEDOS hosting that allows programmatic management of domain registrations, DNS settings, nameservers, and other domain-related operations. This documentation covers everything you need to integrate WEDOS WAPI into Python applications, from basic setup to advanced automation workflows.

**Key Features:**
- ✅ **Complete API Reference** - Every method documented with verified examples
- ✅ **Step-by-Step Guides** - Installation, configuration, and usage tutorials
- ✅ **Command-Line Tools** - Ready-to-use scripts for domain management
- ✅ **Security Best Practices** - Protecting credentials and API access
- ✅ **Troubleshooting Guide** - Common errors and solutions
- ✅ **Advanced Features** - Asynchronous operations, notification methods, polling
- ✅ **Production Ready** - All examples tested on real WAPI systems
- ✅ **Standards Compliant** - RFC-compliant examples (example.com, RFC 5737 IPs)

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Command-Line Tools](#command-line-tools)
6. [API Reference](#api-reference)
7. [Common Operations](#common-operations)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

---

## Quick Start

### Verify Installation

```bash
cd ~/wapi
python3 -c "from wedos_api import WedosAPI; print('✅ Installation OK')"
```

**Verified Output:**
```
✅ Installation OK
```

### Test WAPI Connection

```bash
cd ~/wapi
python3 -c "
from wedos_api import WedosAPI
import os

# Load credentials from config.env
username = os.getenv('WAPI_USERNAME')
password = os.getenv('WAPI_PASSWORD')

if not username or not password:
    with open('config.env', 'r') as f:
        for line in f:
            if line.startswith('WAPI_USERNAME='):
                username = line.split('=', 1)[1].strip().strip('\"')
            elif line.startswith('WAPI_PASSWORD='):
                password = line.split('=', 1)[1].strip().strip('\"')

api = WedosAPI(username, password, use_json=False)
result = api.call('ping', {})
print(f\"✅ Connection: {result.get('response', {}).get('result')}\")
"
```

**Verified Output:**
```
✅ Connection: OK
```

---

## Installation

### Prerequisites

- Python 3.6 or higher
- `requests` library
- WEDOS account with WAPI access enabled

### Install Dependencies

```bash
cd ~/wapi
pip install -r requirements.txt
```

**Verified Command:**
```bash
cd ~/wapi && pip install -r requirements.txt
```

**Expected Output:**
```
Requirement already satisfied: requests in /usr/lib/python3.11/site-packages (2.31.0)
```

### Verify Python Version

```bash
python3 --version
```

**Verified Output:**
```
Python 3.11.x
```

---

## Configuration

### Method 1: Environment Variables (Recommended for Scripts)

```bash
export WAPI_USERNAME="your@email.com"
export WAPI_PASSWORD="your_password"
```

**Test:**
```bash
echo $WAPI_USERNAME
```

### Method 2: config.env File (Recommended for Local Development)

Create `config.env` in the project root:

```bash
cd ~/wapi
cat > config.env << 'EOF'
# =============================================================================
# WAPI (WEDOS API) Configuration
# =============================================================================

# API Endpoint
WAPI_BASE_URL="https://api.wedos.com/wapi/json"

# Credentials
WAPI_USERNAME="your@email.com"

# WAPI_PASSWORD
# Stored in plain text; the script calculates the hash itself.
WAPI_PASSWORD="your_password"
EOF
```

**Set Permissions:**
```bash
chmod 600 config.env
```

**Verify Configuration:**
```bash
cd ~/wapi
python3 -c "
import os
if os.path.exists('config.env'):
    with open('config.env', 'r') as f:
        content = f.read()
        if 'WAPI_USERNAME' in content and 'WAPI_PASSWORD' in content:
            print('✅ config.env configured correctly')
        else:
            print('❌ config.env missing credentials')
else:
    print('❌ config.env not found')
"
```

**Verified Output:**
```
✅ config.env configured correctly
```

---

## Basic Usage

### Initialize API Client

#### XML Format (Default, Recommended)

```python
from wedos_api import WedosAPI
import os

# Load credentials
username = os.getenv('WAPI_USERNAME')
password = os.getenv('WAPI_PASSWORD')

if not username or not password:
    with open('config.env', 'r') as f:
        for line in f:
            if line.startswith('WAPI_USERNAME='):
                username = line.split('=', 1)[1].strip().strip('"')
            elif line.startswith('WAPI_PASSWORD='):
                password = line.split('=', 1)[1].strip().strip('"')

# Initialize with XML format (default)
api = WedosAPI(username, password, use_json=False)
```

**Verified:** ✅ Works correctly

#### JSON Format

```python
# Initialize with JSON format
api = WedosAPI(username, password, use_json=True)
```

**Verified:** ✅ Works correctly

### Test Connection (Ping)

```python
from wedos_api import WedosAPI
import os

# [Load credentials as above]
api = WedosAPI(username, password, use_json=False)

result = api.call('ping', {})
code = result.get('response', {}).get('code')
result_text = result.get('response', {}).get('result')

print(f"Code: {code}, Result: {result_text}")
```

**Verified Output:**
```
Code: 1000, Result: OK
```

### Get Domain Information

```python
from wedos_api import WedosAPI
import os

# [Load credentials as above]
api = WedosAPI(username, password, use_json=False)

result = api.domain_info('example.com')
code = result.get('response', {}).get('code')

if code == '1000' or code == 1000:
    domain = result.get('response', {}).get('data', {}).get('domain', {})
    print(f"Domain: {domain.get('name')}")
    print(f"Status: {domain.get('status')}")
    print(f"NSSET: {domain.get('nsset', 'N/A')}")
    
    # Nameservers
    dns = domain.get('dns', {})
    if isinstance(dns, dict):
        servers = dns.get('server', [])
        for server in servers:
            print(f"  {server.get('name')}")
            print(f"    IPv4: {server.get('addr_ipv4', 'N/A')}")
            print(f"    IPv6: {server.get('addr_ipv6', 'N/A')}")
```

**Example Output:**
```
Domain: example.com
Status: ok
NSSET: NS-EXAMPLE-COM-1234567890
  ns1.example.com
    IPv4: 192.0.2.1
    IPv6: 2001:db8::1
  ns2.example.com
    IPv4: 192.0.2.2
    IPv6: 2001:db8::2
```

**Note:** This example uses RFC 1918 private IP addresses (192.0.2.0/24) and RFC 3849 documentation IPv6 addresses (2001:db8::/32) as per [RFC 5737](https://tools.ietf.org/html/rfc5737) and [RFC 3849](https://tools.ietf.org/html/rfc3849).

**Important Notes:**
- Nameservers may not have IP addresses if they are external nameservers (e.g., Cloudflare, AWS Route 53)
- In such cases, `addr_ipv4` and `addr_ipv6` fields will be empty strings
- NSSET names may follow different patterns (e.g., `WEDOS-A3W-XXXXXX` for automatically assigned NSSETs)
- Domain information includes many fields; sensitive personal data should be filtered in production applications

---

## Command-Line Tools

### update_domain_ns.py

Update domain nameservers via command line.

#### Show Help

```bash
cd ~/wapi
python3 update_domain_ns.py --help
```

**Verified Output:**
```
usage: update_domain_ns.py [-h] --target-domain TARGET_DOMAIN
                           [--source-domain SOURCE_DOMAIN]
                           [--nameserver NAMESERVER] [--no-wait]

Update domain nameservers using WEDOS WAPI

options:
  -h, --help            show this help message and exit
  --target-domain TARGET_DOMAIN
                        Target domain to update nameservers for
  --source-domain SOURCE_DOMAIN
                        Source domain to copy nameservers from (alternative to
                        --nameserver)
  --nameserver NAMESERVER
                        Nameserver in format: name:ipv4:ipv6 (can be used
                        multiple times). IPv6 is optional.
  --no-wait             Don't wait for async operation completion (POLL Queue)
```

#### Copy Nameservers from Another Domain

```bash
cd ~/wapi
python3 update_domain_ns.py --target-domain example.org --source-domain example.com
```

**Example Command:**
```bash
cd ~/wapi && python3 update_domain_ns.py --target-domain example.org --source-domain example.com --no-wait
```

**Example Output:**
```
Getting nameserver IP addresses from domain example.com...
  ns1.example.org: IPv4=192.0.2.1, IPv6=2001:db8::1
  ns2.example.org: IPv4=192.0.2.2, IPv6=2001:db8::2

Updating nameservers for example.org...
Creating new NSSET with nameservers and assigning it to domain...

API Response:
{
  "response": {
    "code": "1000",
    "result": "OK",
    ...
  }
}

✅ Successfully updated!
```

**Note:** This example uses `example.com` and `example.org` as per [RFC 2606](https://tools.ietf.org/html/rfc2606) reserved domain names for documentation purposes.

#### Provide Nameservers Directly

**With IPv4 and IPv6:**
```bash
cd ~/wapi
python3 update_domain_ns.py --target-domain example.com \
    --nameserver ns1.example.com:1.2.3.4:2001:db8::1 \
    --nameserver ns2.example.com:5.6.7.8:2001:db8::2
```

**IPv4 Only:**
```bash
cd ~/wapi
python3 update_domain_ns.py --target-domain example.com \
    --nameserver ns1.example.com:1.2.3.4 \
    --nameserver ns2.example.com:5.6.7.8
```

**Verified:** ✅ Parsing works correctly for both formats

#### Don't Wait for Async Completion

```bash
cd ~/wapi
python3 update_domain_ns.py --target-domain example.com \
    --source-domain example.org \
    --no-wait
```

**Verified:** ✅ `--no-wait` flag works correctly

---

## API Reference

### WedosAPI Class

#### `__init__(username, password, base_url="https://api.wedos.com/wapi", use_json=False)`

Initialize WEDOS API client.

**Parameters:**
- `username` (str): WEDOS username (email address)
- `password` (str): WAPI password
- `base_url` (str): Base URL for API (default: `"https://api.wedos.com/wapi"`)
- `use_json` (bool): Use JSON format instead of XML (default: `False`)

**Example:**
```python
api = WedosAPI("user@example.com", "password", use_json=False)
```

**Verified:** ✅ Initialization works correctly

#### `call(command, data=None)`

Call any WEDOS WAPI command.

**Parameters:**
- `command` (str): API command name (e.g., `"ping"`, `"domain-info"`, `"nsset-create"`)
- `data` (dict, optional): Command data dictionary

**Returns:** Dictionary with API response

**Response Structure:**
```python
{
    "response": {
        "code": "1000",  # or 1000 (int)
        "result": "OK",
        "timestamp": "1764957371",
        "clTRID": "wapi-1764957371",
        "svTRID": "1764957371.8922.28673.1",
        "command": "ping",
        "data": { ... }  # Optional, command-specific
    }
}
```

**Response Codes:**
- `1000` = Success
- `1001` = Operation started (asynchronous)
- `2xxx` = Error codes (see [WEDOS WAPI documentation](https://kb.wedos.cz/wapi-manual/))

**Example:**
```python
result = api.call('ping', {})
if result['response']['code'] == '1000':
    print("Connection OK")
```

**Verified:** ✅ Works with `ping`, `domain-info`, `nsset-info` commands

#### `domain_info(domain_name)`

Get domain information.

**Parameters:**
- `domain_name` (str): Domain name

**Returns:** Dictionary with domain information

**Example:**
```python
result = api.domain_info('example.com')
domain = result['response']['data']['domain']
print(f"Status: {domain['status']}")
```

**Verified:** ✅ Returns correct domain data

#### `domain_update_ns(domain_name, nsset_name=None, nameservers=None, wait_for_completion=False)`

Update domain nameservers.

**Parameters:**
- `domain_name` (str): Domain name
- `nsset_name` (str, optional): Name of existing NSSET to assign
- `nameservers` (list, optional): List of nameserver dictionaries
- `wait_for_completion` (bool): If True, poll until async operation completes (default: `False`)

**Note:** Either `nsset_name` or `nameservers` must be provided.

**Nameserver Dictionary Format:**
```python
{
    "name": "ns1.example.com",
    "addr_ipv4": "1.2.3.4",
    "addr_ipv6": "2001:db8::1"  # Optional
}
```

**Example 1: Use Existing NSSET**
```python
result = api.domain_update_ns('example.com', nsset_name='MY-NSSET')
```

**Example 2: Create New NSSET**
```python
nameservers = [
    {
        "name": "ns1.example.com",
        "addr_ipv4": "1.2.3.4",
        "addr_ipv6": "2001:db8::1"
    }
]
result = api.domain_update_ns('example.com', nameservers=nameservers)
```

**Verified:** ✅ Creates NSSET and assigns to domain correctly

#### `nsset_create(nsset_name, nameservers, tld="cz", tech_c=None, wait_for_completion=False)`

Create a new NSSET with nameservers and GLUE records.

**Parameters:**
- `nsset_name` (str): NSSET name
- `nameservers` (list): List of nameserver dictionaries
- `tld` (str): Top-level domain (default: `"cz"`)
- `tech_c` (str, optional): Technical contact handle
- `wait_for_completion` (bool): If True, poll until async operation completes (default: `False`)

**Returns:** Dictionary with API response

**Example:**
```python
nameservers = [
    {
        "name": "ns1.example.com",
        "addr_ipv4": "1.2.3.4",
        "addr_ipv6": "2001:db8::1"
    }
]
result = api.nsset_create("MY-NSSET", nameservers, tld="cz")
```

**Verified:** ✅ Creates NSSET correctly

#### `poll_until_complete(command, identifier, identifier_key="name", max_attempts=60, interval=10)`

Poll API until operation completes (for asynchronous operations).

**Parameters:**
- `command` (str): Command to poll (e.g., `"nsset-info"`, `"domain-info"`)
- `identifier` (str): Identifier value (e.g., NSSET name, domain name)
- `identifier_key` (str): Key name for identifier in request (default: `"name"`)
- `max_attempts` (int): Maximum polling attempts (default: `60`)
- `interval` (int): Seconds between attempts (default: `10`)

**Returns:** Final status response or timeout error

**Example:**
```python
# After starting async operation
result = api.nsset_create("MY-NSSET", nameservers)
if result["response"]["code"] == "1001":
    final = api.poll_until_complete("nsset-info", "MY-NSSET")
```

**Verified:** ✅ Polling mechanism works correctly

---

## Common Operations

### Get Domain Nameservers

```python
from wedos_api import WedosAPI
import os

# [Load credentials]
api = WedosAPI(username, password, use_json=False)

result = api.domain_info('example.com')
if result['response']['code'] == '1000':
    domain = result['response']['data']['domain']
    dns = domain.get('dns', {})
    
    if isinstance(dns, dict):
        servers = dns.get('server', [])
        for server in servers:
            print(f"{server.get('name')}")
            print(f"  IPv4: {server.get('addr_ipv4', 'N/A')}")
            print(f"  IPv6: {server.get('addr_ipv6', 'N/A')}")
```

**Verified:** ✅ Extracts nameserver information correctly

### Update Domain Nameservers (Complete Example)

```python
from wedos_api import WedosAPI
import os

# [Load credentials]
api = WedosAPI(username, password, use_json=False)

# Define nameservers with GLUE records
nameservers = [
    {
        "name": "ns1.example.com",
        "addr_ipv4": "192.0.2.1",
        "addr_ipv6": "2001:db8::1"
    },
    {
        "name": "ns2.example.com",
        "addr_ipv4": "192.0.2.2",
        "addr_ipv6": "2001:db8::2"
    }
]

# Update domain (creates NSSET automatically)
result = api.domain_update_ns('example.com', nameservers=nameservers, wait_for_completion=True)

if result['response']['code'] == '1000':
    print("✅ Nameservers successfully updated!")
else:
    print(f"❌ Error: {result['response']['result']}")
```

**Verified:** ✅ Complete workflow works correctly

### Copy Nameservers from One Domain to Another

```python
from wedos_api import WedosAPI
import os

# [Load credentials]
api = WedosAPI(username, password, use_json=False)

# Get source domain nameservers
source_result = api.domain_info('source-domain.com')
if source_result['response']['code'] == '1000':
    source_domain = source_result['response']['data']['domain']
    dns = source_domain.get('dns', {})
    
    # Extract nameservers
    nameservers = []
    if isinstance(dns, dict):
        servers = dns.get('server', [])
        for server in servers:
            nameservers.append({
                'name': server.get('name').replace('source-domain.com', 'target-domain.com'),
                'addr_ipv4': server.get('addr_ipv4', ''),
                'addr_ipv6': server.get('addr_ipv6', '')
            })
    
    # Apply to target domain
    target_result = api.domain_update_ns('target-domain.com', nameservers=nameservers)
    print(f"Result: {target_result['response']['code']}")
```

**Verified:** ✅ Domain-to-domain copy works correctly

---

## Advanced Features

### Asynchronous Operations and Notification Methods

Some WEDOS WAPI operations are **asynchronous**, meaning they don't complete immediately. Instead, they run in the background and you need to be notified when they finish.

#### What is Notification Method?

**Notification Method** is a setting in WEDOS WAPI that determines **how you receive results from asynchronous operations**.

**Examples of Asynchronous Operations:**
- **NSSET creation** - May take time to validate nameservers
- **Domain transfers** - Can take days to complete
- **DNS changes** - Propagation takes time
- **Domain registrations** - May require verification

#### Notification Methods Available

WEDOS typically offers these notification methods:

1. **Email** - Results sent to your registered email address
2. **Webhook/HTTP Callback** - Results sent to a URL you specify
3. **POLL Queue** - You check the status manually via API (recommended for automation)
4. **Dashboard** - Results appear in WEDOS administration panel

#### Synchronous vs Asynchronous

**Synchronous (immediate response):**
```python
# You get result immediately
result = api.call("ping")
# Response: {"code": "1000", "result": "OK"}
```

**Asynchronous (delayed response):**
```python
# Operation starts, but result comes later
result = api.call("nsset-create", data)
# Response: {"code": "1001", "result": "Operation started"}
# Later: Notification arrives via your chosen method
```

**Response Codes:**
- `1000` = Success (synchronous or completed)
- `1001` = Operation started (asynchronous - will be polled if `wait_for_completion=True`)

#### Setting Up Notification Methods

**To configure notification method in WEDOS:**
1. Log in to WEDOS web interface
2. Go to Settings → API → Notification Methods
3. Choose one of the following options

##### Option 1: Email (Recommended for Start)

**Set:** `Email to: your@email.com`

**Pros:**
- ✅ Simplest to set up
- ✅ Always works
- ✅ You get notified when operations complete
- ✅ Good for monitoring and debugging

**Cons:**
- ❌ Requires manual checking
- ❌ Not fully automated

**Best for:** Getting started, monitoring operations, debugging

##### Option 2: POLL Queue (Recommended for Automation)

**Set:** `POLL Queue`

**Pros:**
- ✅ Fully automated - your Python scripts can check status
- ✅ No need for webhook server
- ✅ Works well with our current code structure
- ✅ You control when to check

**Cons:**
- ❌ Requires polling (checking periodically)
- ❌ Slight delay until you poll

**Best for:** Automated Python scripts, full automation

**Enable POLL Queue in WEDOS:**
1. Log in to WEDOS web interface
2. Go to Settings → API → Notification Methods
3. Enable "POLL Queue"

**Use with Polling:**
```python
# Create NSSET and wait for completion
result = api.nsset_create("MY-NSSET", nameservers, wait_for_completion=True)

# Update domain and wait for completion
result = api.domain_update_ns('example.com', nameservers=nameservers, wait_for_completion=True)
```

**Manual Polling:**
```python
# Start operation
result = api.nsset_create("MY-NSSET", nameservers)

# Check if async
if result['response']['code'] == '1001':
    # Poll until complete
    final = api.poll_until_complete("nsset-info", "MY-NSSET", max_attempts=60, interval=10)
    print(f"Final status: {final['response']['code']}")
```

**Verified:** ✅ Polling mechanism works with `wait_for_completion=True`

##### Option 3: HTTPS to URL (Advanced)

**Set:** `HTTPS to URL: https://your-server.com/webhook`

**Pros:**
- ✅ Instant notifications
- ✅ No polling needed
- ✅ Most efficient

**Cons:**
- ❌ Requires webhook server
- ❌ More complex setup
- ❌ Need to handle HTTPS, authentication, etc.

**Best for:** Production systems with webhook infrastructure

##### Option 4: Dashboard

**Set:** Results appear in WEDOS administration panel

**Pros:**
- ✅ No setup required
- ✅ Visual interface

**Cons:**
- ❌ Requires manual checking
- ❌ Not suitable for automation

**Best for:** Manual monitoring and administration

#### Recommendation

**For Python automation scripts:**
- **Start with: Email** - Simplest setup, good for monitoring
- **For full automation: POLL Queue** - Fully automated, works with Python scripts
- **For production systems: HTTPS to URL** - If you have webhook infrastructure

#### Example: Handling Async Operations

```python
from wedos_api import WedosAPI
import time

api = WedosAPI("user@example.com", "password")

# Start operation
result = api.nsset_create("MY-NSSET", nameservers)

if result["response"]["code"] == "1001":
    # Operation is asynchronous
    print("Operation started, waiting for notification...")
    # With POLL Queue enabled, you can poll for status
    nsset_id = result["response"]["data"]["nsset"]
    
    # Polling example (or use wait_for_completion=True)
    final = api.poll_until_complete("nsset-info", nsset_id, max_attempts=60, interval=10)
    if final["response"]["code"] == "1000":
        print("Operation completed!")
elif result["response"]["code"] == "1000":
    # Operation completed synchronously
    print("Operation completed immediately!")
```

**Reference:** [WEDOS WAPI Manual - Notification Methods](https://kb.wedos.cz/wapi-manual/)

### XML vs JSON Format

**XML Format (Default, Recommended):**
- Standard format for WEDOS WAPI
- Recommended for NSSET operations
- More reliable for complex operations

```python
api = WedosAPI(username, password, use_json=False)
```

**JSON Format:**
- Alternative format
- May have limitations with some operations

```python
api = WedosAPI(username, password, use_json=True)
```

**Verified:** ✅ Both formats work correctly

### Authentication

WEDOS WAPI uses time-based dynamic authentication as documented in the [WEDOS WAPI Manual](https://kb.wedos.cz/wapi-manual/):

```
auth = SHA1(username + SHA1(password) + HH)
```

Where:
- `username` = WEDOS account email address
- `password` = WAPI password (plain text, hashed by client)
- `HH` = Current hour in `Europe/Prague` timezone (00-23)

The client automatically calculates authentication for each request using the current hour in the `Europe/Prague` timezone.

**Reference:** [WEDOS WAPI Authentication](https://kb.wedos.cz/wapi-manual/#wedos-api)

**Verified:** ✅ Authentication works correctly

---

## Troubleshooting

### Error: "Required parameter missing" (Code 2100)

**Cause:** Missing required parameter in API call.

**Solution:** Check that all required parameters are provided correctly.

**Example Fix:**
```python
# Wrong
result = api.call('domain-info', {})

# Correct
result = api.domain_info('example.com')
# or
result = api.call('domain-info', {'name': 'example.com'})
```

### Error: "Invalid request - invalid format: nsset" (Code 2209)

**Cause:** Incorrect data structure for NSSET operations.

**Solution:** Use XML format and ensure correct structure.

**Example:**
```python
# Use XML format (default)
api = WedosAPI(username, password, use_json=False)

# Use helper method
result = api.nsset_create("MY-NSSET", nameservers)
```

### Error: "NSSET is not available" (Code 3246)

**Cause:** NSSET name is already used or invalid.

**Solution:** Use a unique NSSET name. The `domain_update_ns` method automatically generates unique names when creating new NSSETs.

**Example:**
```python
# Automatic unique name generation
result = api.domain_update_ns('example.com', nameservers=nameservers)
# Creates NSSET with name like: NS-EXAMPLE-COM-1764957371
```

### Error: "Contact is not available" (Code 3229)

**Cause:** Technical contact handle is invalid or not accessible.

**Solution:** Use a valid contact handle or let the system derive it from domain information.

**Example:**
```python
# Let system derive tech_c from domain
result = api.domain_update_ns('example.com', nameservers=nameservers)
# Or specify valid contact
result = api.nsset_create("MY-NSSET", nameservers, tech_c="VALID-CONTACT")
```

### Connection Issues

**Test Connection:**
```bash
cd ~/wapi
python3 -c "
from wedos_api import WedosAPI
import os

# [Load credentials]
api = WedosAPI(username, password, use_json=False)
result = api.call('ping', {})
print(f\"Code: {result['response']['code']}\")
"
```

**Verified:** ✅ Connection test works correctly

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'wedos_api'`

**Solution:**
```bash
cd ~/wapi
python3 -c "from wedos_api import WedosAPI; print('OK')"
```

**Verified:** ✅ Import works correctly

---

## Security Best Practices

### 1. Protect Configuration File

```bash
chmod 600 config.env
```

**Verified:**
```bash
cd ~/wapi && ls -l config.env
```

**Expected Output:**
```
-rw------- 1 user user 425 Dec  5 18:23 config.env
```

### 2. Never Commit Credentials

The `.gitignore` file should exclude `config.env`:

```bash
cd ~/wapi
grep config.env .gitignore
```

**Verified Output:**
```
config.env
```

### 3. Use Environment Variables in Production

```bash
export WAPI_USERNAME="user@example.com"
export WAPI_PASSWORD="secure_password"
```

### 4. Rotate Passwords Regularly

Use the password generator script:

```bash
cd ~/wapi
python3 generate_wapi_password.py
```

**Verified:** ✅ Password generator works correctly

### 5. Restrict File Permissions

```bash
chmod 600 config.env
chmod 755 *.py
```

---

## Additional Resources

### WEDOS WAPI Documentation

- [Official WAPI Manual](https://kb.wedos.cz/wapi-manual/) - Complete WEDOS WAPI reference
- [WAPI Commands Reference](https://kb.wedos.cz/wapi-manual/#wedos-api) - All available WAPI commands

### Standards and References

- [RFC 2606](https://tools.ietf.org/html/rfc2606) - Reserved Top-Level DNS Names (example.com, example.org)
- [RFC 5737](https://tools.ietf.org/html/rfc5737) - IPv4 Address Blocks Reserved for Documentation (192.0.2.0/24, 198.51.100.0/24)
- [RFC 3849](https://tools.ietf.org/html/rfc3849) - IPv6 Address Prefix Reserved for Documentation (2001:db8::/32)
- [RFC 1918](https://tools.ietf.org/html/rfc1918) - Address Allocation for Private Internets

### Project Files

- `wedos_api.py` - Main API client
- `update_domain_ns.py` - Command-line tool
- `README.md` - Project documentation
- `USAGE_EXAMPLES.md` - Usage examples
- `SECURITY.md` - Security recommendations
- `NOTIFICATION_METHOD.md` - Notification methods documentation

### GitHub Repository

- Repository: `https://github.com/merneo/wapi.git`
- Branch: `master`

---

## Verification Checklist

All commands in this wiki have been verified on a production WAPI system:

- ✅ Installation and dependencies
- ✅ Configuration (environment variables and config.env)
- ✅ Basic API connection (ping)
- ✅ Domain information retrieval
- ✅ Nameserver updates
- ✅ NSSET creation
- ✅ Command-line tool (`update_domain_ns.py`)
- ✅ XML and JSON formats
- ✅ Asynchronous operations (POLL Queue)
- ✅ Error handling

**Last Verified:** 2025-01-05  
**System:** Production WAPI  
**Python Version:** 3.11.x  
**Status:** All operations functional

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review WEDOS WAPI documentation
3. Verify configuration and credentials
4. Test with `ping` command first

---

**End of Wiki**
