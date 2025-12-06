Examples
========

This page provides practical examples of using WAPI CLI for common tasks.

Domain Management
-----------------

List all domains:

.. code-block:: bash

   wapi domain list

Get domain information:

.. code-block:: bash

   wapi domain info example.com

Update nameservers:

.. code-block:: bash

   wapi domain update-ns example.com \
     --nameserver ns1.example.com:192.0.2.1:2001:db8::1 \
     --nameserver ns2.example.com:192.0.2.2:2001:db8::2

DNS Management
--------------

List DNS records:

.. code-block:: bash

   wapi dns records example.com

Add A record:

.. code-block:: bash

   wapi dns add example.com \
     --name "@" \
     --type A \
     --value "192.0.2.1" \
     --ttl 3600

Add MX record:

.. code-block:: bash

   wapi dns add example.com \
     --name "@" \
     --type MX \
     --value "10 mail.example.com" \
     --ttl 3600

Delete DNS record:

.. code-block:: bash

   wapi dns delete example.com \
     --id 12345

NSSET Operations
----------------

Get NSSET information:

.. code-block:: bash

   wapi nsset info NS-EXAMPLE-123456

Create NSSET:

.. code-block:: bash

   wapi nsset create NS-EXAMPLE-123456 \
     --nameserver ns1.example.com:192.0.2.1:2001:db8::1 \
     --nameserver ns2.example.com:192.0.2.2:2001:db8::2

Output Formats
--------------

JSON output:

.. code-block:: bash

   wapi domain list --format json

YAML output:

.. code-block:: bash

   wapi domain info example.com --format yaml

XML output:

.. code-block:: bash

   wapi domain list --format xml

Scripting Examples
------------------

Bash script to update nameservers:

.. code-block:: bash

   #!/bin/bash
   DOMAIN="example.com"
   wapi domain update-ns "$DOMAIN" \
     --nameserver ns1.example.com:192.0.2.1 \
     --nameserver ns2.example.com:192.0.2.2

Python script using WAPI CLI:

.. code-block:: python

   import subprocess
   import json

   # Get domain list as JSON
   result = subprocess.run(
       ['wapi', 'domain', 'list', '--format', 'json'],
       capture_output=True,
       text=True
   )
   domains = json.loads(result.stdout)
   print(f"Found {len(domains)} domains")
