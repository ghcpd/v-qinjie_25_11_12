# Project A — Pre-Mitigation (Vulnerable UI)

This project demonstrates front-end UI vulnerabilities: reflected XSS, DOM-based XSS, and secrets exposure via debug panel and localStorage.

Setup & Run (PowerShell):
> Set-Location Project_A_PreMitigation_UI
> ./run_ui_tests.ps1

What this will do:
- Install dependencies from requirements.txt
- Install Playwright browsers
- Start Flask app on port 5000
- Run automated Playwright test harness (tests/test_pre_ui.py)
- Produce `results_pre.json` and screenshots in `results/` folder

Expected behavior (as the app is intentionally vulnerable):
- XSS payloads in `test_ui_vuln.json` should execute for reflected and DOM payload tests
- The debug panel exposes a fake API key text in the DOM

You can explore the app at `http://127.0.0.1:5000/` while the server is running.
