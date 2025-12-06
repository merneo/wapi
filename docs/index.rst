WAPI CLI Documentation
======================

Welcome to the WAPI CLI documentation!

WAPI CLI is a command-line interface tool for managing WEDOS domains, NSSETs, contacts, and DNS records through the WEDOS WAPI. It provides a user-friendly interface for all common domain management operations.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   commands/index
   api/index
   tutorials/index
   examples
   troubleshooting
   contributing

Features
--------

* ✅ Complete domain management (list, info, update nameservers)
* ✅ NSSET operations (create, info)
* ✅ DNS record management (list, add, update, delete)
* ✅ Contact information retrieval
* ✅ Configuration management
* ✅ Multiple output formats (table, JSON, XML, YAML)
* ✅ Sensitive data filtering
* ✅ Async operation polling with ``--wait`` flag
* ✅ IPv6 auto-discovery for nameservers
* ✅ Production-ready, tested, and documented
* ✅ **100% test coverage** (517 tests, all passing)

Quick Start
-----------

Install the package:

.. code-block:: bash

   pip install wapi-cli

Configure your credentials:

.. code-block:: bash

   cp config.env.example config.env
   # Edit config.env with your WAPI username and password

Test your connection:

.. code-block:: bash

   wapi auth ping

List your domains:

.. code-block:: bash

   wapi domain list

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
