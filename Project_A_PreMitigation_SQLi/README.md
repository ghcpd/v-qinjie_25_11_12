# Project A - Pre-Mitigation (Vulnerable)

This project contains a vulnerable Flask service with an input sanitization flaw (SQL injection).

## Vulnerability Test Scenario ⚠️
- Endpoint: `GET /search?query=` — builds raw SQL using the query string without parameterization.
- Example: `GET /search?query=' OR '1'='1` -> returns all users (including `admin`).
- Blind injection simulation: `SLEEP(4)` triggers server-side `time.sleep(4)` (vulnerable test path).

## Acceptance Criteria (pre)
- SQLi succeeds for basic and encoded payloads; blind injection increases latency; logs contain raw SQL.

## Overview
- Endpoint: `/search?query=` — vulnerable to SQL injection because the server concatenates the query into raw SQL.
- Database: SQLite (data/app.db) with a sample `users` table that includes `admin`.
- Logs: `logs/sql.log` records raw SQL statements (vulnerable behavior for testing).

## Running tests
Windows PowerShell:
1. `.un_tests.ps1` (optionally pass `REPEAT` and `DB_SIZE` args)

Unix-like:
1. `./run_tests.sh` (optionally pass `REPEAT` and `DB_SIZE` args)

To run the server directly (not recommended for tests) use module invocation to avoid relative import issues:
- `python -m src.app` (from the `Project_A_PreMitigation_SQLi` project directory)

Artifacts are written to `results/results_pre.json` and `logs/`.