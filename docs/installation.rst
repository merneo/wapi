Installation
============

Prerequisites
-------------

* Python 3.6 or higher
* pip (Python package manager)
* WEDOS account with WAPI access enabled

Install from PyPI
-----------------

The recommended way to install WAPI CLI is using pip:

.. code-block:: bash

   pip install wapi-cli

Install from Source
-------------------

To install from source:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/merneo/wapi.git
   cd wapi

   # Install the package
   pip install -e .

   # Or install dependencies only
   pip install -r requirements.txt

Install with DNS Support
------------------------

To install with optional DNS support (for IPv6 auto-discovery):

.. code-block:: bash

   pip install wapi-cli[dns]

Install Development Dependencies
--------------------------------

For development:

.. code-block:: bash

   pip install -r requirements-dev.txt

Configuration
-------------

Create a ``config.env`` file in your home directory or project root:

.. code-block:: bash

   WAPI_USERNAME="your-email@example.com"
   WAPI_PASSWORD="your-wapi-password"
   WAPI_BASE_URL="https://api.wedos.com/wapi/json"

Or use environment variables:

.. code-block:: bash

   export WAPI_USERNAME="your-email@example.com"
   export WAPI_PASSWORD="your-wapi-password"
   export WAPI_BASE_URL="https://api.wedos.com/wapi/json"

Secure the configuration file:

.. code-block:: bash

   chmod 600 config.env

Verify Installation
-------------------

Test the installation:

.. code-block:: bash

   wapi auth ping

You should see a success message if the installation is correct.
