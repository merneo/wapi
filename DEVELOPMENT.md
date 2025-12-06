# WAPI CLI Development Guide

**Last Updated:** 2025-01-05  
**Version:** 0.9.0+

## Development Setup

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)
- git

### Installation

```bash
# Clone repository
git clone https://github.com/merneo/wapi.git
cd wapi

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### Code Formatting

We use `black` for code formatting and `isort` for import sorting.

```bash
# Format all code
make format

# Or manually:
black --line-length=100 wapi/ tests/
isort --profile=black --line-length=100 wapi/ tests/
```

### Linting

We use `flake8` and `mypy` for code quality checks.

```bash
# Run all linters
make lint

# Or manually:
flake8 --max-line-length=100 --extend-ignore=E203,W503 wapi/ tests/
mypy --ignore-missing-imports wapi/
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/test_validators.py -v
```

### Pre-commit Hooks

Pre-commit hooks automatically format and lint code before commits.

```bash
# Install hooks
make pre-commit

# Run hooks manually
pre-commit run --all-files
```

## Code Style

### Python Style Guide

- Follow **PEP 8** style guide
- Use **black** formatter (line length: 100)
- Use **isort** for import sorting (black profile)
- Use type hints for all functions
- Write docstrings for all public functions/classes

### Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
import os
import sys
from pathlib import Path
from typing import Optional

import requests

from .api.client import WedosAPIClient
from .utils.logger import get_logger
```

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Variables**: `snake_case`
- **Private**: `_leading_underscore`

### Documentation

- Use Google-style docstrings
- Include Args, Returns, Raises sections
- Add examples for complex functions
- Document all public APIs

Example:
```python
def validate_domain(domain: str) -> Tuple[bool, Optional[str]]:
    """
    Validate domain name format.
    
    Args:
        domain: Domain name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Raises:
        None
        
    Example:
        >>> validate_domain('example.com')
        (True, None)
        >>> validate_domain('invalid..domain')
        (False, 'Contains consecutive dots')
    """
```

## Project Structure

```
wapi/
├── wapi/              # Main package
│   ├── __init__.py    # Package exports
│   ├── cli.py         # CLI entry point
│   ├── config.py      # Configuration management
│   ├── exceptions.py  # Custom exceptions
│   ├── api/           # API client
│   ├── commands/      # Command handlers
│   └── utils/         # Utility functions
├── tests/             # Test files
├── docs/              # Documentation (if added)
├── setup.py           # Package setup
├── requirements.txt   # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── pyproject.toml     # Tool configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
└── Makefile           # Development tasks
```

## Making Changes

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following style guide
- Add tests for new functionality
- Update documentation

### 3. Format and Lint

```bash
make format
make lint
```

### 4. Run Tests

```bash
make test
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: Add your feature description"
```

Pre-commit hooks will run automatically.

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

## Testing Guidelines

### Unit Tests

- Test all public functions
- Test edge cases
- Test error conditions
- Use descriptive test names

Example:
```python
def test_validate_domain_valid():
    """Test valid domain names"""
    assert validate_domain('example.com')[0] is True

def test_validate_domain_invalid():
    """Test invalid domain names"""
    assert validate_domain('invalid..domain')[0] is False
```

### Integration Tests

- Test complete workflows
- Test API interactions (with mocks)
- Test CLI commands

## Code Review Checklist

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No hardcoded credentials
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Type hints added
- [ ] Docstrings complete

## Release Process

1. Update version in `wapi/__init__.py` and `setup.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create git tag
5. Push to repository

## Troubleshooting

### Import Errors

```bash
# Reinstall in development mode
pip install -e .
```

### Pre-commit Hooks Not Running

```bash
# Reinstall hooks
pre-commit install
```

### Formatting Issues

```bash
# Auto-format code
make format
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment.

### Automated Checks

On every push and pull request, the following checks run automatically:

1. **Tests** - Runs pytest on Python 3.6-3.11
2. **Linting** - Validates code formatting (black, isort) and style (flake8, mypy)
3. **Coverage** - Enforces 100% test coverage threshold
4. **Security** - Scans for hardcoded secrets and known vulnerabilities
5. **Pre-commit** - Validates pre-commit hooks configuration

### Release Automation

When a version tag is pushed (e.g., `v1.0.0`), GitHub Actions automatically:

1. Runs full test suite
2. Generates release notes from git commits
3. Creates GitHub release with installation instructions

### Viewing CI/CD Status

- **GitHub Actions:** https://github.com/merneo/wapi/actions
- **Coverage Reports:** Available as artifacts in workflow runs
- **Codecov:** https://codecov.io/gh/merneo/wapi

For detailed CI/CD documentation, see `PHASE7_CI_CD.md`.

## Resources

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Black Formatter](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Hooks](https://pre-commit.com/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Questions?** Check `CODE_AUDIT.md` for detailed code analysis and improvement recommendations.
