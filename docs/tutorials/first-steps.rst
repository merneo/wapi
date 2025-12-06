First Steps Tutorial
====================

This tutorial will guide you through your first steps with WAPI CLI.

Step 1: Installation
--------------------

Install WAPI CLI:

.. code-block:: bash

   pip install wapi-cli

Step 2: Configuration
---------------------

Create a configuration file:

.. code-block:: bash

   cp config.env.example config.env
   # Edit config.env with your credentials
   chmod 600 config.env

Step 3: Test Connection
------------------------

Verify your installation and credentials:

.. code-block:: bash

   wapi auth ping

You should see: ``Connection successful``

Step 4: List Domains
---------------------

View all domains in your account:

.. code-block:: bash

   wapi domain list

Step 5: Get Domain Information
-------------------------------

Get detailed information about a domain:

.. code-block:: bash

   wapi domain info example.com

Step 6: Explore Commands
-------------------------

Get help for any command:

.. code-block:: bash

   wapi --help
   wapi domain --help
   wapi dns --help

Next Steps
----------

* Read the :doc:`../commands/index` reference
* Try the :doc:`domain-management` tutorial
* Check out :doc:`../examples` for more examples
