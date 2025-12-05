"""
Logging configuration for WAPI CLI

Provides centralized logging configuration with support for:
- Console output (stdout/stderr)
- File logging (optional)
- Verbose/quiet modes
- Different log levels
"""

import logging
import sys
import os
from typing import Optional
from logging.handlers import RotatingFileHandler


# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: Optional[str] = None,
    log_level: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration for WAPI CLI
    
    Args:
        verbose: Enable verbose (DEBUG) logging
        quiet: Enable quiet mode (ERROR only)
        log_file: Optional path to log file
        log_level: Optional log level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    global _logger
    
    # Determine log level
    if quiet:
        level = logging.ERROR
    elif verbose or log_level == 'DEBUG':
        level = logging.DEBUG
    elif log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        level = logging.INFO
    
    # Create logger
    logger = logging.getLogger('wapi')
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler (stderr for errors, stdout for info)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    
    # Format for console
    if verbose:
        console_format = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_format = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
    
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            # Create directory if needed
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, mode=0o755, exist_ok=True)
            
            # Rotating file handler (10MB max, 5 backups)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            
            # Detailed format for file
            file_format = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s:%(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
    
    _logger = logger
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Optional logger name (default: 'wapi')
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f'wapi.{name}')
    return logging.getLogger('wapi')


def log_api_request(logger: logging.Logger, command: str, data: dict = None):
    """Log API request"""
    if data:
        # Filter sensitive data
        safe_data = {}
        for k, v in data.items():
            if any(sensitive in k.lower() for sensitive in ['password', 'auth', 'token', 'key', 'secret']):
                safe_data[k] = '[HIDDEN]'
            elif isinstance(v, dict):
                # Recursively filter nested dicts
                safe_data[k] = {nk: '[HIDDEN]' if any(s in nk.lower() for s in ['password', 'auth']) else nv 
                               for nk, nv in v.items()}
            else:
                safe_data[k] = v
        logger.debug(f"API Request: {command} with data: {safe_data}")
    else:
        logger.debug(f"API Request: {command}")


def log_api_response(logger: logging.Logger, command: str, code: int, result: str = None):
    """Log API response"""
    if code == 1000 or code == '1000':
        logger.debug(f"API Response: {command} - Success (code: {code})")
    elif code == 1001 or code == '1001':
        logger.info(f"API Response: {command} - Async operation started (code: {code})")
    elif code and str(code).startswith('2'):
        logger.warning(f"API Response: {command} - Error (code: {code}): {result}")
    else:
        logger.error(f"API Response: {command} - Unexpected code: {code}, result: {result}")


def log_validation_error(logger: logging.Logger, field: str, value: str, error: str):
    """Log validation error"""
    logger.warning(f"Validation error for {field}='{value}': {error}")


def log_operation_start(logger: logging.Logger, operation: str, details: dict = None):
    """Log operation start"""
    if details:
        logger.info(f"Starting {operation}: {details}")
    else:
        logger.info(f"Starting {operation}")


def log_operation_complete(logger: logging.Logger, operation: str, success: bool = True, details: dict = None):
    """Log operation completion"""
    if success:
        if details:
            # Filter sensitive data from details
            safe_details = {k: '[HIDDEN]' if any(s in k.lower() for s in ['password', 'auth', 'token']) else v 
                          for k, v in details.items()}
            logger.info(f"Completed {operation}: {safe_details}")
        else:
            logger.info(f"Completed {operation}")
    else:
        if details:
            # Filter sensitive data from details
            safe_details = {k: '[HIDDEN]' if any(s in k.lower() for s in ['password', 'auth', 'token']) else v 
                          for k, v in details.items()}
            logger.error(f"Failed {operation}: {safe_details}")
        else:
            logger.error(f"Failed {operation}")


def log_exception(logger: logging.Logger, exception: Exception, context: str = None):
    """
    Log exception with context
    
    Args:
        logger: Logger instance
        exception: Exception object
        context: Optional context string
    """
    if context:
        logger.exception(f"Exception in {context}: {exception}")
    else:
        logger.exception(f"Exception: {exception}")
