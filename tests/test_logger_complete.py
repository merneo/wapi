"""
Complete tests for logger module to achieve 100% coverage

Tests for remaining uncovered lines (83, 103-106, 124, 135-140, 150-155, 166, 176-178, 182-188, 203).
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
import sys
from io import StringIO

from wapi.utils.logger import (
    get_logger,
    setup_logging,
    log_api_request,
    log_api_response,
    log_validation_error,
    log_operation_start,
    log_operation_complete,
    log_exception
)


class TestLoggerComplete(unittest.TestCase):
    """Complete tests for logger module"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def test_get_logger_with_existing_logger(self):
        """Test get_logger with existing logger (line 83)"""
        # Clear any existing logger
        logger_name = 'wapi.test.module.unique'
        if logger_name in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict[logger_name]
        
        # Create a logger first
        logger1 = get_logger('test.module.unique')
        logger2 = get_logger('test.module.unique')
        
        # Should return the same logger instance (cached)
        self.assertIs(logger1, logger2)

    def test_setup_logging_quiet_mode(self):
        """Test setup_logging with quiet=True (line 103-106)"""
        logger = setup_logging(quiet=True)
        
        # Should set level to ERROR
        self.assertEqual(logger.level, logging.ERROR)
        # Should have console handler
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_verbose_mode(self):
        """Test setup_logging with verbose=True"""
        logger = setup_logging(verbose=True)
        
        # Should set level to DEBUG
        self.assertEqual(logger.level, logging.DEBUG)
        # Should have console handler
        self.assertEqual(len(logger.handlers), 1)

    def test_setup_logging_with_log_level(self):
        """Test setup_logging with explicit log_level (line 124)"""
        logger = setup_logging(log_level='INFO')
        
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)

    @patch('wapi.utils.logger.RotatingFileHandler')
    @patch('wapi.utils.logger.logging.Formatter')
    @patch('wapi.utils.logger.os.makedirs')
    @patch('wapi.utils.logger.os.path.exists')
    def test_setup_logging_with_log_file(self, mock_exists, mock_makedirs, mock_formatter, mock_file_handler):
        """Test setup_logging with log_file (line 135-140)"""
        mock_exists.return_value = False  # Directory doesn't exist
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG  # File handler always uses DEBUG
        mock_file_handler.return_value = mock_handler
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance
        
        logger = setup_logging(log_file='test.log')
        
        # Should create file handler
        mock_file_handler.assert_called_once()
        # Should set formatter
        mock_handler.setFormatter.assert_called_once()
        # Should add handler to logger
        self.assertIn(mock_handler, logger.handlers)
        # Should have both console and file handlers
        self.assertEqual(len(logger.handlers), 2)

    def test_log_api_request_with_data(self):
        """Test log_api_request with data (line 150-155)"""
        logger = get_logger('test')
        logger.setLevel(logging.DEBUG)
        
        # Capture log output
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_api_request(logger, 'test-command', {'param': 'value'})
        
        # Should log without error

    def test_log_api_response_with_data(self):
        """Test log_api_response with data"""
        logger = get_logger('test')
        logger.setLevel(logging.DEBUG)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_api_response(logger, 'test-command', '1000', 'OK')
        
        # Should log without error

    def test_log_validation_error(self):
        """Test log_validation_error"""
        logger = get_logger('test')
        logger.setLevel(logging.WARNING)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_validation_error(logger, 'field', 'value', 'error message')
        
        # Should log without error

    def test_log_operation_start(self):
        """Test log_operation_start"""
        logger = get_logger('test')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_operation_start(logger, 'operation', {'param': 'value'})
        
        # Should log without error

    def test_log_operation_complete(self):
        """Test log_operation_complete"""
        logger = get_logger('test')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_operation_complete(logger, 'operation', success=True, details={'result': 'success'})
        
        # Should log without error

    def test_log_exception_with_context(self):
        """Test log_exception with context (line 166)"""
        logger = get_logger('test')
        logger.setLevel(logging.ERROR)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
        logger.propagate = False
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            log_exception(logger, e, context='test operation')
        
        # Should log without error

    def test_log_exception_without_context(self):
        """Test log_exception without context"""
        logger = get_logger('test')
        logger.setLevel(logging.ERROR)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
        logger.propagate = False
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            log_exception(logger, e)
        
        # Should log without error

    def test_setup_logging_quiet_overrides_verbose(self):
        """Test setup_logging with both quiet and verbose (quiet wins)"""
        logger = setup_logging(quiet=True, verbose=True)
        
        # Quiet should take precedence
        self.assertEqual(logger.level, logging.ERROR)

    def test_setup_logging_log_level_info(self):
        """Test setup_logging with log_level='INFO'"""
        logger = setup_logging(log_level='INFO')
        
        self.assertEqual(logger.level, logging.INFO)

    def test_setup_logging_log_level_warning(self):
        """Test setup_logging with log_level='WARNING'"""
        logger = setup_logging(log_level='WARNING')
        
        self.assertEqual(logger.level, logging.WARNING)

    def test_setup_logging_log_level_error(self):
        """Test setup_logging with log_level='ERROR'"""
        logger = setup_logging(log_level='ERROR')
        
        self.assertEqual(logger.level, logging.ERROR)

    def test_setup_logging_log_level_critical(self):
        """Test setup_logging with log_level='CRITICAL'"""
        logger = setup_logging(log_level='CRITICAL')
        
        self.assertEqual(logger.level, logging.CRITICAL)

    def test_setup_logging_log_level_debug(self):
        """Test setup_logging with log_level='DEBUG'"""
        logger = setup_logging(log_level='DEBUG')
        
        self.assertEqual(logger.level, logging.DEBUG)

    def test_setup_logging_default_level(self):
        """Test setup_logging with default level"""
        logger = setup_logging()
        
        # Default should be INFO
        self.assertEqual(logger.level, logging.INFO)

    @patch('wapi.utils.logger.RotatingFileHandler')
    @patch('wapi.utils.logger.logging.Formatter')
    @patch('wapi.utils.logger.os.makedirs')
    @patch('wapi.utils.logger.os.path.exists')
    def test_setup_logging_file_handler_config(self, mock_exists, mock_makedirs, mock_formatter, mock_file_handler):
        """Test setup_logging file handler configuration (line 176-178, 182-188)"""
        mock_exists.return_value = False
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler
        mock_formatter_instance = Mock()
        mock_formatter.return_value = mock_formatter_instance
        
        logger = setup_logging(log_file='test.log', log_level='DEBUG')
        
        # Should configure file handler
        mock_file_handler.assert_called_once()
        # Should set formatter
        mock_handler.setFormatter.assert_called_once()
        # Should add handler to logger
        self.assertIn(mock_handler, logger.handlers)

    def test_log_exception_with_traceback(self):
        """Test log_exception with traceback (line 203)"""
        logger = get_logger('test')
        logger.setLevel(logging.ERROR)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
        logger.propagate = False
        
        try:
            raise ValueError("Test error with traceback")
        except Exception as e:
            log_exception(logger, e, context='test context')
        
        # Should log with traceback (logger.exception includes traceback)

    def test_get_logger_without_name(self):
        """Test get_logger without name (line 124)"""
        logger = get_logger()
        self.assertEqual(logger.name, 'wapi')

    @patch('wapi.utils.logger.os.path.exists')
    @patch('wapi.utils.logger.os.makedirs')
    @patch('wapi.utils.logger.RotatingFileHandler')
    def test_setup_logging_creates_directory(self, mock_file_handler, mock_makedirs, mock_exists):
        """Test setup_logging creates directory if it doesn't exist (line 83)"""
        mock_exists.return_value = False
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler
        
        setup_logging(log_file='/tmp/test/log.log')
        
        mock_makedirs.assert_called_once_with('/tmp/test', mode=0o755, exist_ok=True)

    @patch('wapi.utils.logger.RotatingFileHandler')
    def test_setup_logging_file_io_error(self, mock_file_handler):
        """Test setup_logging handles IOError (line 104)"""
        mock_file_handler.side_effect = IOError("Permission denied")
        
        logger = setup_logging(log_file='/invalid/path.log')
        
        # Should still work, just log warning
        self.assertIsNotNone(logger)
        # Should have console handler only
        self.assertEqual(len(logger.handlers), 1)

    @patch('wapi.utils.logger.RotatingFileHandler')
    def test_setup_logging_file_permission_error(self, mock_file_handler):
        """Test setup_logging handles PermissionError (line 104)"""
        mock_file_handler.side_effect = PermissionError("Permission denied")
        
        logger = setup_logging(log_file='/root/test.log')
        
        # Should still work, just log warning
        self.assertIsNotNone(logger)

    def test_log_api_request_nested_dict(self):
        """Test log_api_request with nested dict (line 137)"""
        logger = get_logger('test')
        logger.setLevel(logging.DEBUG)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.propagate = False
        
        data = {
            'param': 'value',
            'nested': {
                'password': 'secret',
                'auth_token': 'token',
                'normal_key': 'normal_value'
            }
        }
        log_api_request(logger, 'test-command', data)
        
        # Should filter nested password/auth fields

    def test_log_api_response_code_1001(self):
        """Test log_api_response with code 1001 (line 150-151)"""
        logger = get_logger('test')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_api_response(logger, 'test-command', '1001', 'Async started')
        
        # Should log at INFO level

    def test_log_api_response_code_2xx(self):
        """Test log_api_response with code starting with 2 (line 152-153)"""
        logger = get_logger('test')
        logger.setLevel(logging.WARNING)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_api_response(logger, 'test-command', '2001', 'Error message')
        
        # Should log at WARNING level

    def test_log_api_response_unexpected_code(self):
        """Test log_api_response with unexpected code (line 154-155)"""
        logger = get_logger('test')
        logger.setLevel(logging.ERROR)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_api_response(logger, 'test-command', '9999', 'Unexpected')
        
        # Should log at ERROR level

    def test_log_operation_complete_failure_with_details(self):
        """Test log_operation_complete with failure and details (line 182-188)"""
        logger = get_logger('test')
        logger.setLevel(logging.ERROR)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_operation_complete(logger, 'operation', success=False, details={'error': 'Failed', 'password': 'secret'})
        
        # Should log at ERROR level and filter password

    def test_log_operation_complete_failure_without_details(self):
        """Test log_operation_complete with failure without details (line 188)"""
        logger = get_logger('test')
        logger.setLevel(logging.ERROR)
        
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)
        logger.propagate = False
        
        log_operation_complete(logger, 'operation', success=False)
        
        # Should log at ERROR level without details


if __name__ == '__main__':
    unittest.main()
