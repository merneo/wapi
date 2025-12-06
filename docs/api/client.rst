API Client
==========

.. automodule:: wapi.api.client
   :members:
   :undoc-members:
   :show-inheritance:

WedosAPIClient
--------------

.. autoclass:: wapi.api.client.WedosAPIClient
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from wapi.api.client import WedosAPIClient

   # Initialize client
   client = WedosAPIClient(
       username="your-email@example.com",
       password="your-password",
       use_json=True
   )

   # Make API call
   response = client.call("ping", {})

   # Check response
   if response.get('response', {}).get('code') == '1000':
       print("Connection successful")
