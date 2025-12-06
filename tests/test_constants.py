"""
Unit tests for wapi.constants module

Tests for error code constants and default values.
"""

import unittest

from wapi.constants import (
    EXIT_SUCCESS,
    EXIT_ERROR,
    EXIT_CONFIG_ERROR,
    EXIT_AUTH_ERROR,
    EXIT_VALIDATION_ERROR,
    EXIT_CONNECTION_ERROR,
    EXIT_TIMEOUT_ERROR,
    API_SUCCESS,
    API_ASYNC,
    API_ERROR,
    DEFAULT_CONFIG_FILE,
    DEFAULT_TIMEOUT,
    DEFAULT_DNS_LOOKUP_TIMEOUT,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_MAX_POLL_ATTEMPTS,
    DEFAULT_LOG_LEVEL,
    MAX_LOG_FILE_SIZE,
    LOG_BACKUP_COUNT,
)


class TestConstants(unittest.TestCase):
    """Test cases for constants"""

    def test_exit_codes_are_integers(self):
        """Test that all exit codes are integers"""
        self.assertIsInstance(EXIT_SUCCESS, int)
        self.assertIsInstance(EXIT_ERROR, int)
        self.assertIsInstance(EXIT_CONFIG_ERROR, int)
        self.assertIsInstance(EXIT_AUTH_ERROR, int)
        self.assertIsInstance(EXIT_VALIDATION_ERROR, int)
        self.assertIsInstance(EXIT_CONNECTION_ERROR, int)
        self.assertIsInstance(EXIT_TIMEOUT_ERROR, int)

    def test_exit_codes_values(self):
        """Test that exit codes have correct values"""
        self.assertEqual(EXIT_SUCCESS, 0)
        self.assertEqual(EXIT_ERROR, 1)
        self.assertEqual(EXIT_CONFIG_ERROR, 2)
        self.assertEqual(EXIT_AUTH_ERROR, 3)
        self.assertEqual(EXIT_VALIDATION_ERROR, 4)
        self.assertEqual(EXIT_CONNECTION_ERROR, 5)
        self.assertEqual(EXIT_TIMEOUT_ERROR, 6)

    def test_exit_codes_are_unique(self):
        """Test that all exit codes are unique"""
        exit_codes = [
            EXIT_SUCCESS,
            EXIT_ERROR,
            EXIT_CONFIG_ERROR,
            EXIT_AUTH_ERROR,
            EXIT_VALIDATION_ERROR,
            EXIT_CONNECTION_ERROR,
            EXIT_TIMEOUT_ERROR,
        ]
        self.assertEqual(len(exit_codes), len(set(exit_codes)), "Exit codes must be unique")

    def test_api_response_codes(self):
        """Test API response code constants"""
        self.assertEqual(API_SUCCESS, "1000")
        self.assertEqual(API_ASYNC, "1001")
        self.assertEqual(API_ERROR, "2000")
        self.assertIsInstance(API_SUCCESS, str)
        self.assertIsInstance(API_ASYNC, str)
        self.assertIsInstance(API_ERROR, str)

    def test_default_values_are_valid(self):
        """Test that default values are valid"""
        self.assertIsInstance(DEFAULT_CONFIG_FILE, str)
        self.assertGreater(len(DEFAULT_CONFIG_FILE), 0)
        
        self.assertIsInstance(DEFAULT_TIMEOUT, int)
        self.assertGreater(DEFAULT_TIMEOUT, 0)
        
        self.assertIsInstance(DEFAULT_DNS_LOOKUP_TIMEOUT, int)
        self.assertGreater(DEFAULT_DNS_LOOKUP_TIMEOUT, 0)
        
        self.assertIsInstance(DEFAULT_POLL_INTERVAL, int)
        self.assertGreater(DEFAULT_POLL_INTERVAL, 0)
        
        self.assertIsInstance(DEFAULT_MAX_POLL_ATTEMPTS, int)
        self.assertGreater(DEFAULT_MAX_POLL_ATTEMPTS, 0)

    def test_logging_constants(self):
        """Test logging-related constants"""
        self.assertIsInstance(DEFAULT_LOG_LEVEL, str)
        self.assertIn(DEFAULT_LOG_LEVEL, ['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        
        self.assertIsInstance(MAX_LOG_FILE_SIZE, int)
        self.assertGreater(MAX_LOG_FILE_SIZE, 0)
        
        self.assertIsInstance(LOG_BACKUP_COUNT, int)
        self.assertGreaterEqual(LOG_BACKUP_COUNT, 0)

    def test_timeout_values_are_reasonable(self):
        """Test that timeout values are reasonable"""
        # DNS lookup timeout should be short (5 seconds is reasonable)
        self.assertLessEqual(DEFAULT_DNS_LOOKUP_TIMEOUT, 10)
        
        # API timeout should be reasonable (30 seconds is good)
        self.assertLessEqual(DEFAULT_TIMEOUT, 60)
        self.assertGreaterEqual(DEFAULT_TIMEOUT, 10)
        
        # Poll interval should be reasonable (10 seconds is good)
        self.assertLessEqual(DEFAULT_POLL_INTERVAL, 30)
        self.assertGreaterEqual(DEFAULT_POLL_INTERVAL, 1)


if __name__ == '__main__':
    unittest.main()
