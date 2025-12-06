"""
Unit tests for wapi.exceptions module

Tests for custom exception classes.
"""

import unittest

from wapi.exceptions import (
    WAPIError,
    WAPIConfigurationError,
    WAPIAuthenticationError,
    WAPIValidationError,
    WAPIConnectionError,
    WAPIRequestError,
    WAPITimeoutError,
    WAPIDNSLookupError,
)


class TestExceptions(unittest.TestCase):
    """Test cases for custom exceptions"""

    def test_wapi_error_is_base_exception(self):
        """Test that WAPIError is a base exception"""
        self.assertTrue(issubclass(WAPIError, Exception))
        
        # Test that it can be raised and caught
        with self.assertRaises(WAPIError):
            raise WAPIError("Test error")

    def test_wapi_error_inheritance(self):
        """Test that all exceptions inherit from WAPIError"""
        exceptions = [
            WAPIConfigurationError,
            WAPIAuthenticationError,
            WAPIValidationError,
            WAPIConnectionError,
            WAPIRequestError,
            WAPITimeoutError,
            WAPIDNSLookupError,
        ]
        
        for exc_class in exceptions:
            self.assertTrue(issubclass(exc_class, WAPIError),
                          f"{exc_class.__name__} should inherit from WAPIError")
            self.assertTrue(issubclass(exc_class, Exception),
                          f"{exc_class.__name__} should inherit from Exception")

    def test_exception_instantiation(self):
        """Test that all exceptions can be instantiated"""
        exceptions = [
            WAPIConfigurationError,
            WAPIAuthenticationError,
            WAPIValidationError,
            WAPIConnectionError,
            WAPIRequestError,
            WAPITimeoutError,
            WAPIDNSLookupError,
        ]
        
        for exc_class in exceptions:
            exc = exc_class("Test message")
            self.assertIsInstance(exc, WAPIError)
            self.assertEqual(str(exc), "Test message")

    def test_exception_message(self):
        """Test that exceptions preserve messages"""
        message = "Custom error message"
        exc = WAPIError(message)
        self.assertEqual(str(exc), message)
        
        exc = WAPIConfigurationError(message)
        self.assertEqual(str(exc), message)

    def test_exception_catching(self):
        """Test that exceptions can be caught by base class"""
        exceptions = [
            WAPIConfigurationError("Config error"),
            WAPIAuthenticationError("Auth error"),
            WAPIValidationError("Validation error"),
            WAPIConnectionError("Connection error"),
            WAPIRequestError("Request error"),
            WAPITimeoutError("Timeout error"),
            WAPIDNSLookupError("DNS error"),
        ]
        
        for exc in exceptions:
            # Should be catchable as WAPIError
            with self.assertRaises(WAPIError):
                raise exc
            
            # Should be catchable as Exception
            with self.assertRaises(Exception):
                raise exc

    def test_exception_hierarchy(self):
        """Test exception hierarchy"""
        # All specific exceptions should be WAPIError
        self.assertTrue(issubclass(WAPIConfigurationError, WAPIError))
        self.assertTrue(issubclass(WAPIAuthenticationError, WAPIError))
        self.assertTrue(issubclass(WAPIValidationError, WAPIError))
        self.assertTrue(issubclass(WAPIConnectionError, WAPIError))
        self.assertTrue(issubclass(WAPIRequestError, WAPIError))
        self.assertTrue(issubclass(WAPITimeoutError, WAPIError))
        self.assertTrue(issubclass(WAPIDNSLookupError, WAPIError))
        
        # But not each other
        self.assertFalse(issubclass(WAPIConfigurationError, WAPIAuthenticationError))
        self.assertFalse(issubclass(WAPIAuthenticationError, WAPIValidationError))

    def test_exception_with_context(self):
        """Test that exceptions can carry context"""
        exc = WAPIError("Base error")
        self.assertEqual(str(exc), "Base error")
        
        exc = WAPIConfigurationError("Config file not found: config.env")
        self.assertIn("config.env", str(exc))


if __name__ == '__main__':
    unittest.main()
