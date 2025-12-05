"""
Configuration management commands for WAPI CLI

Handles CLI configuration operations.
"""

import sys
import os
from pathlib import Path
from ..config import load_config, validate_config, get_config
from ..utils.formatters import format_output


def cmd_config_show(args, client=None) -> int:
    """Handle config show command"""
    logger = get_logger('commands.config')
    logger.debug(f"Showing configuration from: {args.config}")
    
    config = load_config(args.config)
    
    # Filter sensitive data
    filtered_config = {}
    for key, value in config.items():
        if 'PASSWORD' in key.upper():
            filtered_config[key] = '[HIDDEN]'
        else:
            filtered_config[key] = value
    
    print(format_output(filtered_config, args.format))
    return 0


def cmd_config_validate(args, client=None) -> int:
    """Handle config validate command"""
    logger = get_logger('commands.config')
    logger.debug(f"Validating configuration from: {args.config}")
    
    is_valid, error = validate_config(args.config)
    
    if is_valid:
        logger.info("Configuration validation passed")
        print("✅ Configuration is valid")
        username = get_config('WAPI_USERNAME', config_file=args.config)
        if username:
            print(f"   Username: {username[:10]}...")
        return 0
    else:
        logger.error(f"Configuration validation failed: {error}")
        print(f"❌ Configuration error: {error}", file=sys.stderr)
        return 1


def cmd_config_set(args, client=None) -> int:
    """Handle config set command"""
    config_file = Path(args.config)
    
    # Read existing config
    config = {}
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
    
    # Update value
    config[args.key] = args.value
    
    # Write back
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            for key, value in config.items():
                if 'PASSWORD' in key.upper():
                    f.write(f'{key}="[HIDDEN]"\n')
                else:
                    f.write(f'{key}="{value}"\n')
        print(f"✅ Set {args.key} in {args.config}")
        return 0
    except Exception as e:
        print(f"Error: Could not write to {args.config}: {e}", file=sys.stderr)
        return 1
