"""
Custom exceptions for WAPI CLI

Provides standardized exception classes for better error handling.
"""


class WAPIError(Exception):
    """Base exception for all WAPI CLI errors"""
    pass


class WAPIConfigurationError(WAPIError):
    """Raised when configuration is invalid or missing"""
    pass


class WAPIAuthenticationError(WAPIError):
    """Raised when authentication fails"""
    pass


class WAPIValidationError(WAPIError):
    """Raised when input validation fails"""
    pass


class WAPIConnectionError(WAPIError):
    """Raised when API connection fails"""
    pass


class WAPIRequestError(WAPIError):
    """Raised when API request fails"""
    pass


class WAPITimeoutError(WAPIError):
    """Raised when operation times out"""
    pass


class WAPIDNSLookupError(WAPIError):
    """Raised when DNS lookup fails"""
    pass
