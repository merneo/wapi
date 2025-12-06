# WAPI CLI — Repository Overview

## What This Project Does
- Command-line interface for Wedos API (domains, DNS, NSSET, auth, search).
- End-to-end validated flows for domain lifecycle (create, transfer, renew, delete, update).
- DNS record management with async polling support.
- WHOIS-based domain availability search with fallbacks and safe timeouts.
- Comprehensive validation, logging, and formatting utilities.

## Getting Started
1) Install dependencies:
   - `pip install -r requirements.txt`
   - `pip install -r requirements-dev.txt` for tests/coverage.
2) Run the CLI:
   - `python -m wapi --help`
   - Examples:
     - `python -m wapi auth login`
     - `python -m wapi domain info example.com`
     - `python -m wapi dns records example.com`
3) Configuration:
   - Set `WAPI_USERNAME` and `WAPI_PASSWORD` (env or config file).
   - Use `wapi --wizard` for guided setup.

## Testing & Quality
- Full suite: `pytest --maxfail=1 --cov=wapi --cov-report=term-missing`
- Coverage: 100% across all modules (864 tests).
- Linting (if enabled locally): `flake8` / `pre-commit run --all-files`.

## Key Modules
- `wapi/commands/`: CLI command handlers (auth, domain, dns, nsset, search).
- `wapi/api/client.py`: Wedos API client with polling helpers.
- `wapi/utils/`: validators, logging, formatting, DNS lookup, interactive shell.
- `tests/`: comprehensive coverage for commands, utils, API, and edge cases.

## Notable Behaviors
- Async operations (domain/dns) include `--wait` handling with polling and timeouts.
- WHOIS lookups use default servers per TLD and fallback to IANA discovery.
- Input validation defends against invalid domains, IPs, nameservers, and emails.
- Defensive branches are marked with `# pragma: no cover` only when truly unreachable.

## Contributing
- Keep new code covered by tests; maintain 100% coverage.
- Follow existing patterns for command handlers and validators.
- Update `CHANGELOG.md` and `COVERAGE_STATUS.md` when behavior or coverage changes.
