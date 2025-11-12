# Project B - Post-Mitigation (Patched UI)

This demo app demonstrates mitigations:

- Server-side escaping of user comments (html.escape).
- CSP headers to prevent inline script execution.
- No exposed secrets (masked API key only).
- Safe DOM updates using `textContent` instead of `innerHTML`.

How to run:
- ./run_ui_tests.sh (Linux)
- ./run_ui_tests.ps1 (Windows)

What to look for:
- The `results/results_post.json` file contains per-test detection of attacks and evidence (screenshots, console messages).
- Screen captures in `results/` show no XSS or secret exposure.
