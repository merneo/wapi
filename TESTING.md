# Testing Guide for WAPI CLI

**Last Updated:** 2025-12-06

## Overview

WAPI CLI uses `pytest` for testing. The test suite includes unit tests for core functionality, error handling, and validation.

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_constants.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=wapi --cov-report=term-missing --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_constants.py::TestConstants::test_exit_codes_values -v
```

## Test Structure

### Test Files

1. **`test_constants.py`** - Tests for `wapi.constants` (7 tests)
   - Exit code constants
   - API response codes
   - Default values
   - Logging constants

2. **`test_exceptions.py`** - Tests for `wapi.exceptions` (7 tests)
   - Exception hierarchy
   - Exception instantiation
   - Exception catching

3. **`test_error_handling.py`** - Tests for error handling patterns (13 tests)
   - Error handling constants
   - Exception hierarchy
   - Specific exception types

4. **`test_config_error_handling.py`** - Tests for configuration error handling (6 tests)
   - Missing credentials
   - File I/O errors
   - Config validation

5. **`test_api_client.py`** - Tests for API client (14 tests)
   - Client initialization
   - Error handling (connection, timeout, request errors)
   - Polling functionality
   - API methods

6. **`test_commands_error_handling.py`** - Tests for command error handling (10 tests)
   - Domain command errors
   - DNS command errors
   - Constants usage

7. **`test_cli.py`** - Tests for CLI (10 tests)
   - Client creation
   - Error handling (config, auth, connection, timeout, keyboard interrupt)
   - Command routing

8. **`test_dns_lookup.py`** - Tests for DNS lookup (14 tests)
   - IPv6 discovery
   - Nameserver enhancement
   - Error handling

9. **`test_commands_operations.py`** - Tests for command operations (14 tests)
   - Successful domain commands
   - Successful DNS commands
   - Successful NSSET commands
   - Output formatting

10. **`test_auth_commands.py`** - Tests for auth commands (11 tests)
   - Login, logout, status commands
   - Authentication handling

11. **`test_config_commands.py`** - Tests for config commands (10 tests)
   - Config show, validate, set commands
   - Configuration management

12. **`test_logger.py`** - Tests for logger utility (19 tests)
   - get_logger function tests
   - setup_logging function tests
   - Logger helper functions tests
   - Logger integration tests

13. **`test_validators.py`** - Tests for input validation (12 tests)
   - Domain validation
   - IP address validation
   - Nameserver validation
   - Email validation

15. **`test_formatters.py`** - Tests for output formatting (8 tests)
   - Table formatting
   - JSON formatting
   - XML formatting
   - YAML formatting

## Test Statistics

- **Total Test Files:** 37
- **Total Test Cases:** 789
- **All Tests Passing:** ✅ 789/789 (100%)
- **Test Coverage:** 98% overall ⬆️ 🎉
  - All modules have ~95-100% coverage
  - Critical paths fully covered
  - Error handling fully covered

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test
```python
import unittest
from wapi.constants import EXIT_SUCCESS

class TestConstants(unittest.TestCase):
    def test_exit_success_value(self):
        """Test that EXIT_SUCCESS is 0"""
        self.assertEqual(EXIT_SUCCESS, 0)
```

### Testing Exceptions
```python
from wapi.exceptions import WAPIValidationError

def test_validation_error(self):
    """Test that validation errors raise WAPIValidationError"""
    with self.assertRaises(WAPIValidationError):
        raise WAPIValidationError("Invalid input")
```

### Testing with Mocks
```python
from unittest.mock import patch, Mock

@patch('wapi.config.get_config')
def test_config_loading(self, mock_get_config):
    """Test config loading with mocked get_config"""
    mock_get_config.return_value = 'test_value'
    # ... test code
```

## Test Coverage Goals

- **Current Coverage:** 98%
- **Target Coverage:** 100% (Achieved for most modules)
- **Status:** ✅ **Goal Met**
- **Verification:** Run `make test-cov` to verify.

## Continuous Integration

Tests should be run before committing:
```bash
# Run all tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=wapi --cov-report=term

# Run with linting
make lint
make test
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Test Naming**: Use descriptive test names
3. **Test Coverage**: Aim for high coverage of critical paths
4. **Mock External Dependencies**: Use mocks for API calls, file I/O
5. **Test Error Cases**: Test both success and error scenarios
6. **Documentation**: Add docstrings to test methods

## Future Test Improvements

- [ ] Add integration tests
- [ ] Add API client mocking tests
- [ ] Add command execution tests
- [ ] Add end-to-end tests
- [ ] Add performance tests
- [ ] Add security tests
