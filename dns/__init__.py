"""
Lightweight stub of the ``dns`` package used in tests.

Provides just enough surface to allow patching ``dns.resolver.Resolver`` and
importing common resolver exceptions when the external ``dnspython`` dependency
is not installed in the test environment.
"""

from . import resolver  # re-export resolver module

