# Makefile for WAPI CLI development tasks

.PHONY: help install install-dev format lint test test-cov clean build dist check

help:
	@echo "WAPI CLI Development Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development dependencies"
	@echo "  format        - Format code with black and isort"
	@echo "  lint          - Run linters (flake8, mypy)"
	@echo "  test          - Run tests"
	@echo "  test-cov      - Run tests with coverage"
	@echo "  clean         - Clean build artifacts"
	@echo "  pre-commit    - Install pre-commit hooks"
	@echo "  build         - Build distribution packages"
	@echo "  dist          - Build and check distribution packages"
	@echo "  check         - Check package metadata and distribution"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

format:
	black --line-length=100 wapi/ tests/
	isort --profile=black --line-length=100 wapi/ tests/

lint:
	flake8 --max-line-length=100 --extend-ignore=E203,W503 wapi/ tests/
	mypy --ignore-missing-imports wapi/

test:
	pytest -v

test-cov:
	pytest --cov=wapi --cov-report=html --cov-report=term

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/

pre-commit:
	pre-commit install

build:
	python -m pip install --upgrade pip build
	python -m build

dist: build
	python -m pip install --upgrade pip twine
	twine check dist/*

check:
	python -m pip install --upgrade pip twine
	python setup.py check --metadata
	twine check dist/* || echo "No dist/ directory found. Run 'make build' first."
