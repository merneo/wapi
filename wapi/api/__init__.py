"""
WAPI API Client Package

This package contains the core API client for communicating with WEDOS WAPI.
"""

from .client import WedosAPIClient
from .auth import calculate_auth, validate_credentials, get_prague_hour

__all__ = [
    'WedosAPIClient',
    'calculate_auth',
    'validate_credentials',
    'get_prague_hour',
]
