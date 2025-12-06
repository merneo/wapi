Quick Start Guide
=================

This guide will help you get started with WAPI CLI in just a few minutes.

Test Your Connection
--------------------

First, verify that your installation is working:

.. code-block:: bash

   wapi auth ping

If successful, you'll see a message confirming the connection.

List Your Domains
-----------------

View all domains in your account:

.. code-block:: bash

   wapi domain list

Get Domain Information
----------------------

Get detailed information about a specific domain:

.. code-block:: bash

   wapi domain info example.com

List DNS Records
----------------

View DNS records for a domain:

.. code-block:: bash

   wapi dns records example.com

Get NSSET Information
---------------------

View NSSET details:

.. code-block:: bash

   wapi nsset info NS-EXAMPLE-123456

Output Formats
--------------

WAPI CLI supports multiple output formats:

**Table format (default):**

.. code-block:: bash

   wapi domain list --format table

**JSON format:**

.. code-block:: bash

   wapi domain list --format json

**YAML format:**

.. code-block:: bash

   wapi domain list --format yaml

**XML format:**

.. code-block:: bash

   wapi domain list --format xml

Next Steps
----------

* Read the :doc:`commands/index` guide for detailed command documentation
* Check out :doc:`tutorials/index` for step-by-step tutorials
* See :doc:`examples` for more usage examples
* Review :doc:`troubleshooting` for common issues
