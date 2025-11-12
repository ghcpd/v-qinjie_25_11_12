# Project A - Pre-Mitigation UI (Vulnerable)

This project intentionally contains front-end/UI vulnerabilities to be used for automated testing:

- Reflected XSS via unsanitized comment rendering (`{{ c|safe }}` used on templates).
- DOM-based XSS via `innerHTML` on the hash-based demo (`/hash#payload`).
- Secrets exposed: `window.PUBLIC_API_KEY` and debug API key appear in the DOM and console.

Run tests:
- Linux/macOS: ./run_ui_tests.sh
- PowerShell: ./run_ui_tests.ps1

Results appear in `results/results_pre.json`. Screenshots are captured for failures.
