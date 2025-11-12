# Vulnerability Detection & Mitigation: SQLi Demo

This repository contains two self-contained Flask projects demonstrating SQL injection vulnerability and its mitigation: `Project_A_PreMitigation_SQLi` (vulnerable) and `Project_B_PostMitigation_SQLi` (patched).

## Overview
- Project A contains raw SQL string concatenation and is intentionally vulnerable.
- Project B uses parameterized queries and a simple WAF to block injection patterns.
- Shared test cases in `shared/test_data.json` exercise normal queries, basic SQLi, encoded payloads, blind time-based SQLi (via a user-defined sleep function in SQLite), and malformed input.

## Quick start
PowerShell (Windows):
- First run `./setup.ps1` to create virtual environment and install dependencies.
- Run `./run_all.ps1` to run both tests and generate `compare_report.md`.

Command Prompt (Windows CMD):
- First run `setup.bat` to create virtual environment and install dependencies.
- Then run `run_all.ps1` in PowerShell (recommended) or call tests directly via `python Project_A_PreMitigation_SQLi/tests/run_tests.py`.

Bash (Linux/macOS):
- Run `./setup.sh` to create venv and install dependencies.
- Run `./run_all.sh` to run tests and generate `compare_report.md`.

The `run_all` scripts will run tests for both projects and write `results_pre.json` and `results_post.json` plus the final `compare_report.md`.

`results_pre.json` and `results_post.json` contain per-test entries and aggregated `metrics` fields with:
- `attack_success_rate` (percentage)
- `avg_latency` (seconds)
- `leaks` (count of leakage incidents)
- `evidence` (list of log-based detections)

## Acceptance criteria
- All SQL inputs are parameterized and sanitized in `Project_B_PostMitigation_SQLi`.
- Injection payloads return safe responses (403 from WAF, empty result, or non-sensitive error messages).
- Average response latency impact <= 10% between pre and post mitigation.
- SQLi success rate should reduce by >= 95% after mitigation.

## Test scenarios
- `/search?query=` – search endpoint exposing SQLi via LIKE in `Project_A`.
- `/login?username=&password=` – authentication where SQLi can be used to bypass authentication.

Expected inputs & outputs (examples):
- `{"query":"1 OR 1=1"}` — In pre-mitigation this may return ALL users; in post-mitigation it should be blocked or sanitized.
- `"' OR '1'='1"` — Should not authenticate in post-mitigation.
- `"%27%20OR%201%3D1"` — encoded injection should be detected and blocked.
- `"SLEEP(5)"` — Blind/time-based injection should cause latency in pre-mitigation only.
- Malformed / binary input — should not reveal stack traces. 

## Limitations
- This demo uses SQLite and a simple WAF; real-world environments need dedicated WAFs and more complex sanitization.
- The sleep-based blind injection is simulated by a user-defined function in SQLite and only for testing.

## Next steps
- Integrate with CI, scan tools, and real DBs (Postgres/MySQL) for more realistic tests.
