# Project B — Post-Mitigation (Patched UI)

This project demonstrates mitigations for front-end UI vulnerabilities: input sanitization, Content Security Policy (CSP), safe DOM updates via textContent, and secret masking.

Setup & Run (PowerShell):
> Set-Location Project_B_PostMitigation_UI
> ./run_ui_tests.ps1

What this will do:
- Install dependencies (including bleach for sanitization)
- Install Playwright browsers
- Start Flask app on port 5001
- Run the Playwright test harness (tests/test_post_ui.py)
- Produce `results_post.json` and screenshots in `results/` folder

Expected behavior:
- XSS payloads should not be executed (reflected nor DOM XSS should be prevented)
- Secrets should be masked or not present in the DOM/localStorage/console

Security features implemented:
- Input sanitization with bleach and default Jinja2 escaping
- CSP header denying inline scripts and remote sources
- DOM updates via `textContent` to avoid innerHTML evaluations
- No secrets stored in localStorage; API key masked in UI
