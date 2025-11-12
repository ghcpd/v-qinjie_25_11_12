# Project B - Post-Mitigation (Patched)

This project contains a Flask service that is patched against SQL injection by using parameterized queries, input validation, and a simple WAF middleware.

## Test Scenario ✅
- Endpoint: `GET /search?query=` — uses parameterized queries and WAF middleware to block suspicious tokens like `SLEEP`, `UNION`, `OR`, and comment sequences.
- Expected: `GET /search?query=' OR '1'='1` should not return all users; rather, it should be blocked or return safe results.

## Acceptance Criteria (post)
- All SQL inputs are parameterized and sanitized.
- Injection payloads return safe error or empty result.
- No data leakage or stack trace exposure in logs.
- Average response time increased by ≤ 10%.

## Running tests
Windows PowerShell:
1. `.un_tests.ps1` (optionally pass `REPEAT` and `DB_SIZE` args)

Unix-like:
1. `./run_tests.sh` (optionally pass `REPEAT` and `DB_SIZE` args)

To run the server directly (not recommended for tests) use module invocation to avoid relative import issues:
- `python -m src.app` (from the `Project_B_PostMitigation_SQLi` project directory)

Artifacts are written to `results/results_post.json` and `logs/`.

## Interpreting Results ✅
- `results/results_post.json` contains per-test info and `metrics.attack_success_rate`.
- `logs/access.log` records sanitized query metadata but not payloads.