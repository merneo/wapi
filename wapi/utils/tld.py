"""
Top-Level Domain (TLD) utilities for WAPI CLI

Provides TLD validation and lists of supported TLDs by WEDOS.
"""

from typing import List, Optional, Set, Tuple

from .logger import get_logger

# WEDOS supported TLDs - comprehensive list
# Based on common TLDs supported by European registrars

# Primary TLDs (most commonly used)
PRIMARY_TLDS: Set[str] = {
    # Czech and Slovak
    'cz', 'sk',
    # Common gTLDs
    'com', 'net', 'org', 'info', 'biz', 'name', 'pro',
    # European
    'eu',
}

# Country Code TLDs (ccTLD)
COUNTRY_CODE_TLDS: Set[str] = {
    # European
    'at', 'be', 'bg', 'ch', 'de', 'dk', 'es', 'fi', 'fr', 'gr',
    'hu', 'ie', 'it', 'li', 'lu', 'nl', 'no', 'pl', 'pt', 'ro',
    'se', 'uk',
    # Other regions
    'us', 'ca', 'au', 'jp', 'cn', 'ru',
}

# Special/Modern TLDs
SPECIAL_TLDS: Set[str] = {
    'co', 'io', 'tv', 'me', 'xyz', 'online', 'site', 'store',
    'tech', 'cloud', 'app', 'dev',
}

# Multi-level TLDs (second-level domains)
MULTI_LEVEL_TLDS: Set[str] = {
    'co.uk', 'org.uk', 'me.uk',
    'com.au', 'com.br', 'com.mx',
}

# Combined set of all supported TLDs
ALL_SUPPORTED_TLDS: Set[str] = (
    PRIMARY_TLDS |
    COUNTRY_CODE_TLDS |
    SPECIAL_TLDS |
    MULTI_LEVEL_TLDS
)


def extract_tld(domain: str) -> Optional[str]:
    """
    Extract TLD from a domain name.
    
    Handles both single-level (e.g., 'example.com' -> 'com')
    and multi-level TLDs (e.g., 'example.co.uk' -> 'co.uk').
    
    Args:
        domain: Domain name (e.g., 'example.com', 'example.co.uk')
        
    Returns:
        TLD string or None if domain is invalid
        
    Examples:
        >>> extract_tld('example.com')
        'com'
        >>> extract_tld('example.co.uk')
        'co.uk'
        >>> extract_tld('invalid')
        None
    """
    if not domain or '.' not in domain:
        return None
    
    domain_lower = domain.lower().strip()
    
    # Check for multi-level TLDs first (e.g., co.uk, com.au)
    for multi_tld in sorted(MULTI_LEVEL_TLDS, key=len, reverse=True):
        if domain_lower.endswith(f'.{multi_tld}'):
            return multi_tld
    
    # Extract single-level TLD
    parts = domain_lower.split('.')
    # Note: After checking for '.' on line 76, split('.') will always
    # return at least 2 parts, so len(parts) < 2 should never be true.
    # However, we keep this check for defensive programming and edge cases.
    if len(parts) < 2:  # pragma: no cover
        return None
    
    return parts[-1]


def is_tld_supported(tld: str) -> bool:
    """
    Check if a TLD is supported by WEDOS.
    
    Args:
        tld: TLD to check (e.g., 'com', 'cz', 'co.uk')
        
    Returns:
        True if TLD is supported, False otherwise
        
    Examples:
        >>> is_tld_supported('com')
        True
        >>> is_tld_supported('cz')
        True
        >>> is_tld_supported('invalid')
        False
    """
    if not tld:
        return False
    
    tld_lower = tld.lower().strip()
    return tld_lower in ALL_SUPPORTED_TLDS


def validate_tld(domain: str, strict: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate that a domain's TLD is supported by WEDOS.
    
    Args:
        domain: Domain name to validate
        strict: If True, only allow supported TLDs. If False, allow any valid TLD format.
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Examples:
        >>> validate_tld('example.com', strict=True)
        (True, None)
        >>> validate_tld('example.invalid', strict=True)
        (False, 'TLD "invalid" is not supported by WEDOS')
        >>> validate_tld('example.xyz', strict=False)
        (True, None)
    """
    logger = get_logger('utils.tld')
    
    if not domain:
        return False, "Domain name cannot be empty"
    
    tld = extract_tld(domain)
    if not tld:
        return False, "Could not extract TLD from domain"
    
    if strict:
        if not is_tld_supported(tld):
            logger.debug(f"TLD validation failed: {tld} is not supported")
            return False, f'TLD "{tld}" is not supported by WEDOS'
    
    logger.debug(f"TLD validation passed: {tld}")
    return True, None


def get_supported_tlds() -> List[str]:
    """
    Get a sorted list of all supported TLDs.
    
    Returns:
        List of supported TLD strings
        
    Examples:
        >>> tlds = get_supported_tlds()
        >>> 'com' in tlds
        True
        >>> 'cz' in tlds
        True
    """
    return sorted(ALL_SUPPORTED_TLDS)


def get_tld_category(tld: str) -> Optional[str]:
    """
    Get the category of a TLD.
    
    Args:
        tld: TLD to categorize
        
    Returns:
        Category name ('primary', 'country', 'special', 'multi-level') or None
        
    Examples:
        >>> get_tld_category('com')
        'primary'
        >>> get_tld_category('cz')
        'primary'
        >>> get_tld_category('co.uk')
        'multi-level'
    """
    tld_lower = tld.lower().strip()
    
    if tld_lower in PRIMARY_TLDS:
        return 'primary'
    elif tld_lower in COUNTRY_CODE_TLDS:
        return 'country'
    elif tld_lower in SPECIAL_TLDS:
        return 'special'
    elif tld_lower in MULTI_LEVEL_TLDS:
        return 'multi-level'
    
    return None
