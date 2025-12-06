Authentication Commands
========================

The ``auth`` module provides commands for testing authentication and connection to the WEDOS WAPI.

Ping
----

Test the connection to WEDOS WAPI:

.. code-block:: bash

   wapi auth ping

**Example output:**

.. code-block:: text

   Connection successful

Login
-----

Interactive login to save credentials:

.. code-block:: bash

   wapi auth login

Or provide credentials directly:

.. code-block:: bash

   wapi auth login --username your-email@example.com --password your-password

Logout
------

Clear saved credentials:

.. code-block:: bash

   wapi auth logout

Status
------

Check authentication status:

.. code-block:: bash

   wapi auth status

**Example output:**

.. code-block:: text

   Authenticated as: your-email@example.com
   Connection: OK
