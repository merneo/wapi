Troubleshooting
===============

Common Issues and Solutions
----------------------------

Connection Errors
~~~~~~~~~~~~~~~~~

**Problem:** ``Connection failed`` or ``WAPIConnectionError``

**Solutions:**

1. Check your internet connection
2. Verify WEDOS API is accessible: ``curl https://api.wedos.com/wapi/json``
3. Check firewall settings
4. Verify credentials in ``config.env``

Authentication Errors
~~~~~~~~~~~~~~~~~~~~~

**Problem:** ``Authentication failed`` or ``WAPIAuthenticationError``

**Solutions:**

1. Verify username and password in ``config.env``
2. Check that WAPI access is enabled in your WEDOS account
3. Ensure password is the WAPI password (not account password)
4. Test with: ``wapi auth ping``

Configuration Errors
~~~~~~~~~~~~~~~~~~~~

**Problem:** ``WAPIConfigurationError: Cannot read config file``

**Solutions:**

1. Ensure ``config.env`` exists in the current directory or home directory
2. Check file permissions: ``chmod 600 config.env``
3. Verify file format (KEY="VALUE" or KEY=VALUE)
4. Use environment variables as alternative

Validation Errors
~~~~~~~~~~~~~~~~~

**Problem:** ``WAPIValidationError: Invalid domain name``

**Solutions:**

1. Verify domain name format (e.g., ``example.com``)
2. Check for typos
3. Ensure domain is registered in your account
4. Use ``wapi domain list`` to see valid domains

Timeout Errors
~~~~~~~~~~~~~~

**Problem:** ``WAPITimeoutError: Operation timed out``

**Solutions:**

1. Check network connection
2. Increase timeout in configuration
3. Retry the operation
4. Use ``--wait`` flag for async operations

Getting Help
------------

* Check the :doc:`commands/index` for command-specific help
* Review :doc:`examples` for usage examples
* Open an issue on `GitHub <https://github.com/merneo/wapi/issues>`_
* Check the `WIKI.md <https://github.com/merneo/wapi/blob/master/WIKI.md>`_ for detailed documentation
