# Project A - Pre-Mitigation (Vulnerable UI)

This demo app intentionally contains UI vulnerabilities for educational/testing purposes:

- Reflected XSS via unescaped comment rendering (server uses Markup).
- DOM-based XSS via innerHTML assignment to `commentZone` using `dangerous` query parameter.
- Secrets exposed in DOM and console: `APIKEY-1234567890-UNMASKED` displayed and written to localStorage.

How to run:
- ./run_ui_tests.sh (Linux)
- ./run_ui_tests.ps1 (Windows)

What to look for:
- The `results/results_pre.json` file contains per-test detection of attacks and evidence (screenshots, console messages).
- Screen captures in `results/` show XSS execution or DOM injection.
