"""
Unit tests for wapi.utils.logger module

Tests for logging functionality, setup, and configuration.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
import tempfile
import os

from wapi.utils.logger import (
    get_logger,
    setup_logging,
    log_api_request,
    log_api_response,
    log_validation_error,
    log_operation_start,
    log_operation_complete,
    log_exception,
)


class TestGetLogger(unittest.TestCase):
    """Test get_logger function"""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance"""
        logger = get_logger('test.module')
        
        self.assertIsInstance(logger, logging.Logger)
        # get_logger adds 'wapi.' prefix to the name
        self.assertEqual(logger.name, 'wapi.test.module')

    def test_get_logger_same_name_returns_same_logger(self):
        """Test that get_logger returns same logger for same name"""
        # Clear any existing loggers to ensure clean state
        logging.getLogger('wapi.test.module').handlers.clear()
        
        logger1 = get_logger('test.module')
        logger2 = get_logger('test.module')
        
        # Python's logging.getLogger returns the same instance for same name
        self.assertEqual(logger1.name, logger2.name)
        # They should be the same object
        self.assertIs(logger1, logger2)

    def test_get_logger_different_names_return_different_loggers(self):
        """Test that get_logger returns different loggers for different names"""
        logger1 = get_logger('test.module1')
        logger2 = get_logger('test.module2')
        
        self.assertIsNot(logger1, logger2)
        self.assertNotEqual(logger1.name, logger2.name)


class TestSetupLogging(unittest.TestCase):
    """Test setup_logging function"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def test_setup_logging_default(self):
        """Test setup_logging with default parameters"""
        logger = setup_logging()
        
        self.assertIsNotNone(logger)
        self.assertEqual(logger.level, logging.INFO)

    def test_setup_logging_verbose(self):
        """Test setup_logging with verbose=True"""
        logger = setup_logging(verbose=True)
        
        self.assertIsNotNone(logger)
        # Verify DEBUG level was set
        self.assertEqual(logger.level, logging.DEBUG)

    def test_setup_logging_quiet(self):
        """Test setup_logging with quiet=True"""
        logger = setup_logging(quiet=True)
        
        self.assertIsNotNone(logger)
        # Verify ERROR level was set
        self.assertEqual(logger.level, logging.ERROR)

    def test_setup_logging_log_level(self):
        """Test setup_logging with explicit log_level"""
        logger = setup_logging(log_level='ERROR')
        
        self.assertIsNotNone(logger)
        # Verify ERROR level was set
        self.assertEqual(logger.level, logging.ERROR)

    def test_setup_logging_with_log_file(self):
        """Test setup_logging with log_file parameter"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp:
            tmp_path = tmp.name
        
        try:
            logger = setup_logging(log_file=tmp_path)
            
            self.assertIsNotNone(logger)
            # Verify file handler was added
            file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
            self.assertGreater(len(file_handlers), 0)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_setup_logging_verbose_takes_precedence(self):
        """Test that verbose takes precedence over log_level"""
        # Note: In actual code, verbose=True sets DEBUG level regardless of log_level
        logger = setup_logging(verbose=True, log_level='ERROR')
        
        self.assertIsNotNone(logger)
        # Verify DEBUG level was set (verbose takes precedence)
        self.assertEqual(logger.level, logging.DEBUG)

    def test_setup_logging_quiet_takes_precedence(self):
        """Test that quiet takes precedence over log_level"""
        # Note: In actual code, quiet=True always sets ERROR level (first if condition)
        logger = setup_logging(quiet=True, log_level='DEBUG')
        
        self.assertIsNotNone(logger)
        # Verify ERROR level was set (quiet takes precedence - checked first)
        self.assertEqual(logger.level, logging.ERROR)


class TestLoggerHelperFunctions(unittest.TestCase):
    """Test logger helper functions"""

    def test_log_api_request(self):
        """Test log_api_request function"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        
        log_api_request(logger, 'test-command', {'key': 'value'})
        
        output = log_capture.getvalue()
        self.assertIn('test-command', output)

    def test_log_api_request_filters_password(self):
        """Test that log_api_request filters passwords"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        
        log_api_request(logger, 'test-command', {'password': 'secret123'})
        
        output = log_capture.getvalue()
        self.assertIn('[HIDDEN]', output)
        self.assertNotIn('secret123', output)

    def test_log_api_response_success(self):
        """Test log_api_response for success"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        
        log_api_response(logger, 'test-command', 1000)
        
        output = log_capture.getvalue()
        self.assertIn('Success', output)

    def test_log_validation_error(self):
        """Test log_validation_error function"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
        
        log_validation_error(logger, 'field', 'value', 'error message')
        
        output = log_capture.getvalue()
        self.assertIn('Validation error', output)
        self.assertIn('field', output)

    def test_log_operation_start(self):
        """Test log_operation_start function"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        log_operation_start(logger, 'test-operation')
        
        output = log_capture.getvalue()
        self.assertIn('Starting test-operation', output)

    def test_log_operation_complete(self):
        """Test log_operation_complete function"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        log_operation_complete(logger, 'test-operation', success=True)
        
        output = log_capture.getvalue()
        self.assertIn('Completed test-operation', output)

    def test_log_exception(self):
        """Test log_exception function"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        logger.propagate = False
        
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            log_exception(logger, e, "test context")
        
        output = log_capture.getvalue()
        self.assertIn('Exception', output)
        self.assertIn('test context', output)


class TestLoggerIntegration(unittest.TestCase):
    """Test logger integration with actual logging"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def test_logger_logs_messages(self):
        """Test that logger actually logs messages"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        logger.info("Test message")
        
        output = log_capture.getvalue()
        self.assertIn("Test message", output)

    def test_logger_respects_level(self):
        """Test that logger respects log level"""
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('wapi.test')
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        
        output = log_capture.getvalue()
        self.assertNotIn("Debug message", output)
        self.assertNotIn("Info message", output)
        self.assertIn("Warning message", output)


if __name__ == '__main__':
    unittest.main()
