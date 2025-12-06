# Restructuring Audit & Plan

## Goals
- Reduce duplication in commands (async/polling patterns).
- Simplify and share test fixtures for repeated mocks.
- Consider CI matrix/job simplification.
- Review utils packaging for clarity.
- Keep repository documentation aligned with implemented phases.

## Methodology & References (best practices)
- Refactoring in small, behavior-preserving steps (Fowler mindset).
- TDD-style guardrails: fast, isolated tests around risky changes.
- CI slimming guided by DORA/Accelerate: remove redundant stages, keep feedback fast.
- Documentation: Keep a Changelog plus concise architectural notes; prefer clarity over verbosity.

## Current State
- 100% tests passing (864), 100% coverage.
- Dev pins: pytest 9.0.1, pytest-cov 7.0.0, Sphinx 7.3.7, urllib3 2.6.0.
- CI: Python 3.10, 3.11, 3.13 matrix; coverage runs inside the test job; outdated report; safety + pip-audit.
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
### Status
- **Completed**: helper created and applied to DNS/Domain commands; stderr timeout messaging preserved.

## Phase 2: Tests – Shared Fixtures
### Observations
- Repeated mocks for `poll_until_complete`, WHOIS sockets, DNS rows (list vs dict).
### Plan
- Add `tests/conftest.py` fixtures:
  - poll_success/poll_timeout/poll_warning side-effect helpers.
  - WHOIS socket fixture (connect/recv/timeout patterns).
  - Normalizers for rows/servers where needed.
- Refactor DNS/Domain/Search/DNS lookup tests to use fixtures; preserve coverage.
### Status
- **Completed**: fixtures added; DNS lookup tests migrated to shared socket fixture; coverage intact.

## Phase 3: CI Slimming (Optional)
### Observations
- Matrix trimmed to 3.10/3.11/3.13; separate coverage job removed; security + outdated jobs exist.
### Decisions
- Coverage runs inside test jobs with Codecov/artifact upload; reduced duplication.
- Coverage uploads/artifacts now restricted to Python 3.11 to cut CI time; matrix tests still run on 3.10/3.11/3.13.
### Next adjustments (if needed)
- If further runtime cuts are desired, consider trimming to two versions (e.g., 3.11 + 3.13) or caching wheels.

## Phase 4: Utils Packaging (Optional)
### Observations
- Flat `wapi/utils` works; only DNS lookup and formatters are larger.
### Option
- Defer; consider `utils/dns/lookup.py` and `utils/formatting/` only if import churn acceptable.
### Guidance
- Follow least-surprise imports; reorganize only when a cohesive subdomain emerges.

## Phase 5: Documentation Hygiene
- Keep CHANGELOG current for CI/test/process changes (done for CI slimming).
- Add short rationale notes when refactors alter surfaces (captured for polling helper).
- Prefer lightweight architecture notes over long narratives; update when modules move.

## Phase 6: Secrets Scanning
### Plan
- Add a dedicated CI job running gitleaks (fail on detect) with repository-wide scan (full history).
- Provide a minimal allowlist for known placeholders to reduce false positives.
### Status
- **Completed**: gitleaks job added to CI with `.gitleaks.toml` allowlisting common placeholders.

## Phase 7: Supply-Chain Tightening
### Plan
- Make safety/pip-audit blocking in CI (no `|| true`); allow explicit allowlist if needed.
- Add automated dependency update checks.
### Status
- **Completed**: safety/pip-audit now fail on findings; Dependabot scheduled weekly for pip and GitHub Actions.

## Phase 8: SAST (Bandit)
### Plan
- Add a Bandit job to surface Python security lint findings.
- Keep it non-blocking initially to avoid CI friction; review findings periodically.
### Status
- **Completed**: Bandit job added (informational) on Python 3.11.

## Phase 9: Logging & Timeouts Audit
### Plan
- Verify logging paths redact sensitive fields (password/auth/token/key/secret).
- Ensure network calls specify timeouts to avoid hangs.
### Status
- **Completed**: Existing logging helpers mask sensitive keys; WHOIS/DNS lookups and polling already enforce timeouts. No code changes required.

## Next Steps
1) (Done) Polling helper + DNS/Domain refactor.
2) (Done) Shared fixtures + DNS lookup refactor to fixtures.
3) (Done) CI matrix reduction and coverage job merge; optionally scope uploads to one version.
4) (Pending) Re-evaluate utils structure when a new subdomain emerges.
5) (Ongoing) Keep docs (CHANGELOG + this plan) aligned with each phase.
