"""
Comprehensive tests for wapi/api/auth.py
"""
import pytest
import hashlib
import sys
from unittest.mock import MagicMock, patch
from datetime import datetime

from wapi.api.auth import (
    get_prague_hour,
    calculate_auth,
    validate_credentials
)

class TestGetPragueHour:
    def test_with_pytz(self):
        with patch('wapi.api.auth.pytz') as mock_pytz:
            mock_tz = MagicMock()
            mock_pytz.timezone.return_value = mock_tz
            
            # Mock datetime.now to return a specific time
            mock_now = MagicMock()
            mock_now.strftime.return_value = "14"
            
            # We need to mock datetime.now() on the module level where it is imported or used
            # In auth.py: from datetime import datetime
            with patch('wapi.api.auth.datetime') as mock_dt:
                mock_dt.now.return_value = mock_now
                
                hour = get_prague_hour()
                
                assert hour == "14"
                mock_pytz.timezone.assert_called_with('Europe/Prague')
                mock_dt.now.assert_called_with(mock_tz)

    def test_without_pytz(self):
        # Simulate pytz import error by patching the module-level variable 'pytz' in wapi.api.auth
        with patch('wapi.api.auth.pytz', None):
            with patch('wapi.api.auth.datetime') as mock_dt:
                # Mock UTC time where hour is 10
                mock_now = MagicMock()
                mock_now.hour = 10
                mock_dt.now.return_value = mock_now
                
                hour = get_prague_hour()
                
                # Fallback logic is (hour + 1) % 24 -> 11
                assert hour == "11"


class TestCalculateAuth:
    def test_auth_calculation(self):
        username = "user@test.com"
        password = "password123"
        
        # Expected calculation:
        # 1. SHA1(password)
        pass_hash = hashlib.sha1(password.encode()).hexdigest()
        
        # 2. Hour (mocked)
        mock_hour = "10"
        
        # 3. SHA1(user + pass_hash + hour)
        final_str = f"{username}{pass_hash}{mock_hour}"
        expected_hash = hashlib.sha1(final_str.encode()).hexdigest()
        
        with patch('wapi.api.auth.get_prague_hour', return_value=mock_hour):
            result = calculate_auth(username, password)
            assert result == expected_hash


class TestValidateCredentials:
    def test_valid(self):
        valid, msg = validate_credentials("me@test.com", "pass123")
        assert valid is True
        assert msg is None

    def test_empty_username(self):
        valid, msg = validate_credentials("", "pass")
        assert valid is False
        assert "Username cannot be empty" in msg

    def test_invalid_email(self):
        valid, msg = validate_credentials("user_no_at", "pass")
        assert valid is False
        assert "email address" in msg

    def test_empty_password(self):
        valid, msg = validate_credentials("me@test.com", "")
        assert valid is False
        assert "Password cannot be empty" in msg

    def test_password_too_long(self):
        valid, msg = validate_credentials("me@test.com", "a" * 16)
        assert valid is False
        assert "maximum 15 characters" in msg
