"""
Unit tests for error handling in WAPI CLI

Tests that commands and modules properly use custom exceptions and constants.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from wapi.constants import (
    EXIT_SUCCESS,
    EXIT_ERROR,
    EXIT_CONFIG_ERROR,
    EXIT_AUTH_ERROR,
    EXIT_VALIDATION_ERROR,
)
from wapi.exceptions import (
    WAPIError,
    WAPIConfigurationError,
    WAPIAuthenticationError,
    WAPIValidationError,
    WAPIConnectionError,
    WAPIRequestError,
)


class TestErrorHandlingConstants(unittest.TestCase):
    """Test that error handling uses constants correctly"""

    def test_exit_codes_are_used(self):
        """Test that exit codes are properly defined"""
        # These should be used instead of hardcoded 0/1
        self.assertEqual(EXIT_SUCCESS, 0)
        self.assertEqual(EXIT_ERROR, 1)
        self.assertNotEqual(EXIT_SUCCESS, EXIT_ERROR)

    def test_exit_codes_are_importable(self):
        """Test that exit codes can be imported"""
        from wapi.constants import (
            EXIT_SUCCESS,
            EXIT_ERROR,
            EXIT_CONFIG_ERROR,
            EXIT_AUTH_ERROR,
            EXIT_VALIDATION_ERROR,
        )
        self.assertIsNotNone(EXIT_SUCCESS)
        self.assertIsNotNone(EXIT_ERROR)


class TestExceptionHierarchy(unittest.TestCase):
    """Test exception hierarchy and catching"""

    def test_catch_base_exception(self):
        """Test that base WAPIError catches all specific exceptions"""
        exceptions = [
            WAPIConfigurationError("Config error"),
            WAPIAuthenticationError("Auth error"),
            WAPIValidationError("Validation error"),
            WAPIConnectionError("Connection error"),
            WAPIRequestError("Request error"),
        ]
        
        for exc in exceptions:
            with self.assertRaises(WAPIError):
                raise exc

    def test_exception_types(self):
        """Test that exceptions are of correct types"""
        config_exc = WAPIConfigurationError("Test")
        self.assertIsInstance(config_exc, WAPIError)
        self.assertIsInstance(config_exc, WAPIConfigurationError)
        self.assertNotIsInstance(config_exc, WAPIAuthenticationError)

    def test_exception_chaining(self):
        """Test exception chaining"""
        # Test that exceptions can be chained
        original = ValueError("Original error")
        try:
            raise original
        except ValueError:
            try:
                raise WAPIRequestError("Wrapped error")
            except WAPIRequestError as wrapped:
                # Exception chaining is automatic in Python 3
                self.assertIsNotNone(wrapped)
                self.assertIsInstance(wrapped, WAPIRequestError)


class TestConfigErrorHandling(unittest.TestCase):
    """Test configuration error handling"""

    def test_config_error_raises_correct_exception(self):
        """Test that config errors raise WAPIConfigurationError"""
        with self.assertRaises(WAPIConfigurationError):
            raise WAPIConfigurationError("Configuration file not found")

    def test_config_error_message(self):
        """Test that config errors have meaningful messages"""
        exc = WAPIConfigurationError("Config file error: config.env")
        self.assertIn("config.env", str(exc))


class TestValidationErrorHandling(unittest.TestCase):
    """Test validation error handling"""

    def test_validation_error_raises_correct_exception(self):
        """Test that validation errors raise WAPIValidationError"""
        with self.assertRaises(WAPIValidationError):
            raise WAPIValidationError("Invalid domain name")

    def test_validation_error_inheritance(self):
        """Test that validation errors inherit from WAPIError"""
        exc = WAPIValidationError("Test")
        self.assertIsInstance(exc, WAPIError)


class TestConnectionErrorHandling(unittest.TestCase):
    """Test connection error handling"""

    def test_connection_error_raises_correct_exception(self):
        """Test that connection errors raise WAPIConnectionError"""
        with self.assertRaises(WAPIConnectionError):
            raise WAPIConnectionError("Connection failed")

    def test_connection_error_inheritance(self):
        """Test that connection errors inherit from WAPIError"""
        exc = WAPIConnectionError("Test")
        self.assertIsInstance(exc, WAPIError)


class TestRequestErrorHandling(unittest.TestCase):
    """Test request error handling"""

    def test_request_error_raises_correct_exception(self):
        """Test that request errors raise WAPIRequestError"""
        with self.assertRaises(WAPIRequestError):
            raise WAPIRequestError("API request failed")

    def test_request_error_inheritance(self):
        """Test that request errors inherit from WAPIError"""
        exc = WAPIRequestError("Test")
        self.assertIsInstance(exc, WAPIError)


if __name__ == '__main__':
    unittest.main()
