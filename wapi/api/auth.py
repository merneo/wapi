"""
Authentication utilities for WEDOS WAPI

Handles SHA1 hash calculation and timezone-aware authentication.
"""

import hashlib
from datetime import datetime
import pytz
from typing import str as StrType


def get_prague_hour() -> str:
    """
    Get current hour in Europe/Prague timezone.
    
    Returns:
        Current hour as two-digit string (00-23)
        
    Example:
        >>> hour = get_prague_hour()
        >>> len(hour)
        2
    """
    prague_tz = pytz.timezone('Europe/Prague')
    now = datetime.now(prague_tz)
    return now.strftime('%H')


def calculate_auth(username: str, password: str) -> str:
    """
    Calculate WEDOS WAPI authentication hash.
    
    Formula: SHA1(username + SHA1(password) + HH)
    where HH is current hour in Europe/Prague timezone.
    
    Args:
        username: WEDOS username (email)
        password: WAPI password (plain text)
        
    Returns:
        Authentication hash as hexadecimal string
        
    Example:
        >>> auth = calculate_auth('user@example.com', 'password')
        >>> len(auth)
        40  # SHA1 produces 40-character hex string
    """
    # Calculate SHA1 of password
    password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
    
    # Get current hour in Prague timezone
    hour = get_prague_hour()
    
    # Calculate: SHA1(username + SHA1(password) + HH)
    auth_string = f"{username}{password_hash}{hour}"
    auth_hash = hashlib.sha1(auth_string.encode('utf-8')).hexdigest()
    
    return auth_hash


def validate_credentials(username: str, password: str) -> tuple[bool, Optional[str]]:
    """
    Validate credential format (not authentication).
    
    Args:
        username: WEDOS username
        password: WAPI password
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if '@' not in username:
        return False, "Username should be an email address"
    
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) > 15:
        return False, "Password must be maximum 15 characters"
    
    return True, None
