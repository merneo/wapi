"""
Configuration management for WAPI CLI

Handles loading configuration from config.env file and environment variables.
"""

import os
from typing import Optional, Dict, Tuple
from pathlib import Path


def load_config(config_file: str = "config.env") -> Dict[str, str]:
    """
    Load configuration from file and environment variables.
    
    Environment variables take precedence over config file.
    
    Args:
        config_file: Path to configuration file (default: config.env)
        
    Returns:
        Dictionary with configuration values
        
    Example:
        >>> config = load_config()
        >>> print(config.get('WAPI_USERNAME'))
        user@example.com
    """
    config = {}
    
    # Try to load from file
    config_path = Path(config_file)
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY="VALUE" or KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        config[key] = value
        except Exception as e:
            print(f"Warning: Could not read config file {config_file}: {e}")
    
    # Override with environment variables
    env_vars = ['WAPI_USERNAME', 'WAPI_PASSWORD', 'WAPI_BASE_URL']
    for var in env_vars:
        env_value = os.getenv(var)
        if env_value:
            config[var] = env_value
    
    return config


def get_config(key: str, default: Optional[str] = None, config_file: str = "config.env") -> Optional[str]:
    """
    Get a specific configuration value.
    
    Args:
        key: Configuration key
        default: Default value if not found
        config_file: Path to configuration file
        
    Returns:
        Configuration value or default
    """
    # Check environment variable first
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # Check config file
    config = load_config(config_file)
    return config.get(key, default)


def validate_config(config_file: str = "config.env") -> Tuple[bool, Optional[str]]:
    """
    Validate that required configuration is present.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    username = get_config('WAPI_USERNAME', config_file=config_file)
    password = get_config('WAPI_PASSWORD', config_file=config_file)
    
    if not username:
        return False, "WAPI_USERNAME not set (check config.env or environment variables)"
    
    if not password:
        return False, "WAPI_PASSWORD not set (check config.env or environment variables)"
    
    return True, None
