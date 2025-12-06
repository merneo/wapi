# Restructuring Audit & Plan

## Goals
- Reduce duplication in commands (async/polling patterns).
- Simplify and share test fixtures for repeated mocks.
- Consider CI matrix/job simplification.
- Review utils packaging for clarity.

## Current State
- 100% tests passing (864), 100% coverage.
- Dev pins: pytest 9.0.1, pytest-cov 7.0.0, Sphinx 7.3.7, urllib3 2.6.0.
- CI: Python 3.8–3.13 matrix; outdated report; safety + pip-audit.
- Docs updated with venv guidance and test counts.

## Phase 1: Commands – Async/Polling Duplication
### Observations
- `wapi/commands/dns.py`: async branches in record add/update/delete share the same pattern (call → code 1001 → check_* → poll_until_complete).
- `wapi/commands/domain.py`: similar polling in update-ns/create/renew/update.
- Output/log/timeout handling duplicated across commands.

### Plan
- Add helper in `wapi/commands/helpers.py`:
  - `poll_and_check(client, command, params, is_complete, args, success_msg, timeout_error_msg=None, formatter=None)`
  - Optional formatter callback for printing/logging responses.
- Normalize list/dict handling for rows/servers in check functions.
- Keep behavior unchanged (messages, return codes, exceptions).

## Phase 2: Tests – Shared Fixtures
### Observations
- Repeated mocks for `poll_until_complete`, WHOIS sockets, DNS rows (list vs dict).
### Plan
- Add `tests/conftest.py` fixtures:
  - poll_success/poll_timeout/poll_warning side-effect helpers.
  - WHOIS socket fixture (connect/recv/timeout patterns).
  - Normalizers for rows/servers where needed.
- Refactor DNS/Domain/Search/DNS lookup tests to use fixtures; preserve coverage.

## Phase 3: CI Slimming (Optional)
### Observations
- Matrix 3.8–3.13; separate coverage job; security + outdated jobs exist.
### Options
- Keep compatibility: keep matrix.
- Faster CI: limit to 3.10 & 3.13, merge coverage into main test job, drop extra coverage job if acceptable.

## Phase 4: Utils Packaging (Optional)
### Observations
- Flat `wapi/utils` works; only DNS lookup and formatters are larger.
### Option
- Defer; consider `utils/dns/lookup.py` and `utils/formatting/` only if import churn acceptable.

## Next Steps
1) Implement Phase 1 helper and refactor DNS/Domain polling code.
2) Implement Phase 2 fixtures and refactor tests.
3) Decide on CI slimming (Phase 3).
4) Re-evaluate utils structure (Phase 4) after above.
