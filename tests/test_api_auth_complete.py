"""
Complete tests for API auth module to achieve 100% coverage

Tests for remaining uncovered lines (13-15, 32-42, 45-76, 90-102).
"""

import unittest
from unittest.mock import Mock, patch

from wapi.api.auth import validate_credentials, calculate_auth
from wapi.exceptions import WAPIValidationError


class TestAPIAuthComplete(unittest.TestCase):
    """Complete tests for API auth module"""

    def test_validate_credentials_empty_username(self):
        """Test validate_credentials with empty username (line 13-15)"""
        is_valid, error = validate_credentials('', 'password')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_credentials_empty_password(self):
        """Test validate_credentials with empty password"""
        is_valid, error = validate_credentials('user@example.com', '')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_credentials_invalid_email(self):
        """Test validate_credentials with invalid email format (line 38-41)"""
        is_valid, error = validate_credentials('invalid-email', 'password')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_credentials_valid(self):
        """Test validate_credentials with valid credentials"""
        is_valid, error = validate_credentials('user@example.com', 'password123')
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_calculate_auth(self):
        """Test calculate_auth function (line 45-76)"""
        username = 'user@example.com'
        password = 'testpass'
        
        hash_result = calculate_auth(username, password)
        
        # Should return SHA1 hash
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 40)  # SHA1 is 40 hex chars

    def test_calculate_auth_different_inputs(self):
        """Test calculate_auth with different inputs"""
        username1 = 'user1@example.com'
        username2 = 'user2@example.com'
        password = 'testpass'
        
        hash1 = calculate_auth(username1, password)
        hash2 = calculate_auth(username2, password)
        
        # Different usernames should produce different hashes
        self.assertNotEqual(hash1, hash2)

    def test_calculate_auth_same_inputs(self):
        """Test calculate_auth produces same hash for same inputs (within same hour)"""
        username = 'user@example.com'
        password = 'testpass'
        
        hash1 = calculate_auth(username, password)
        hash2 = calculate_auth(username, password)
        
        # Same inputs within same hour should produce same hash
        self.assertEqual(hash1, hash2)

    def test_validate_credentials_none_username(self):
        """Test validate_credentials with None username"""
        is_valid, error = validate_credentials(None, 'password')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_credentials_none_password(self):
        """Test validate_credentials with None password"""
        is_valid, error = validate_credentials('user@example.com', None)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_credentials_password_too_long(self):
        """Test validate_credentials with password too long (line 99-100)"""
        long_password = 'a' * 16  # 16 characters, max is 15
        is_valid, error = validate_credentials('user@example.com', long_password)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn('15', error)
    
    @patch('wapi.api.auth.pytz', None)
    def test_get_prague_hour_fallback_no_pytz(self):
        """Test get_prague_hour fallback when pytz is not available (lines 38-41)"""
        from wapi.api.auth import get_prague_hour
        
        # When pytz is None, should use fallback
        hour = get_prague_hour()
        self.assertIsInstance(hour, str)
        self.assertEqual(len(hour), 2)
        # Should be a valid hour (00-23)
        hour_int = int(hour)
        self.assertGreaterEqual(hour_int, 0)
        self.assertLessEqual(hour_int, 23)
    
    @patch.dict('sys.modules', {'pytz': None})
    def test_pytz_import_error(self):
        """Test that ImportError for pytz is handled (lines 13-15)"""
        # Reload module to trigger ImportError handling
        import importlib
        import wapi.api.auth
        importlib.reload(wapi.api.auth)
        
        # pytz should be None after ImportError
        self.assertIsNone(wapi.api.auth.pytz)


if __name__ == '__main__':
    unittest.main()
