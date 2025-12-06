"""
Minimal stub of ``dns.resolver`` for tests.

This is intentionally small: it exposes the symbols the test suite patches or
references without requiring the external dnspython dependency.
"""


class _BaseResolverError(Exception):
    """Base class for resolver stubs."""


class Timeout(_BaseResolverError):
    pass


class NXDOMAIN(_BaseResolverError):
    pass


class NoAnswer(_BaseResolverError):
    pass


class NoNameservers(_BaseResolverError):
    pass


class Resolver:
    def __init__(self):
        self.timeout = None
        self.lifetime = None
        # Tests patch resolve, so keep it simple.

    def resolve(self, *_args, **_kwargs):
        return []

