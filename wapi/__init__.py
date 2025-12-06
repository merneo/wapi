"""
WAPI CLI - WEDOS WAPI Command-Line Interface

A comprehensive CLI tool for managing WEDOS domains, NSSETs, and DNS operations.
"""

__version__ = "0.9.0"
__author__ = "WAPI CLI Team"
__license__ = "MIT"

# Main exports
from .api.client import WedosAPIClient
from .cli import main
from .exceptions import (
    WAPIError,
    WAPIConfigurationError,
    WAPIAuthenticationError,
    WAPIValidationError,
    WAPIConnectionError,
    WAPIRequestError,
    WAPITimeoutError,
    WAPIDNSLookupError,
)

__all__ = [
    '__version__',
    '__author__',
    '__license__',
    'WedosAPIClient',
    'main',
    'WAPIError',
    'WAPIConfigurationError',
    'WAPIAuthenticationError',
    'WAPIValidationError',
    'WAPIConnectionError',
    'WAPIRequestError',
    'WAPITimeoutError',
    'WAPIDNSLookupError',
]
