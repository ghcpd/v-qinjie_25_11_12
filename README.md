# UI Vulnerability Detection & Mitigation (Pre/Post)

This repository contains two Flask-based example projects to evaluate UI/front-end vulnerabilities, specifically XSS and secrets exposure. It contains automated Playwright tests that exercise the web UI with malicious inputs and record whether vulnerabilities execute, and a comparison report generator.

Folders:
- Project_A_PreMitigation_UI: Vulnerable UI (reflected XSS, DOM XSS, secret exposure)
- Project_B_PostMitigation_UI: Patched UI (input sanitization, CSP, safe DOM updates, secret masking)
- shared_artifacts: test cases and compare report generator

How to run (Linux/macOS/WLS):
1. Install Python 3.10+ and Git.
2. Run `./run_all_ui.sh` (this installs dependencies, starts both servers, runs tests, and writes `shared_artifacts/compare_ui_security_report.md`).

On Windows PowerShell:
1. Run `.













Recommendations included in the generated report and README in each project.- Playwright installs browser binaries during test setup.- This is a simplified demo for testing XSS and front-end secret exposure; not a production app.Limitations:- shared_artifacts/generate_compare_report.py: generates `compare_ui_security_report.md`- Project_B_PostMitigation_UI/tests/test_post_ui.py: Playwright tests for patched app- Project_A_PreMitigation_UI/tests/test_pre_ui.py: Playwright tests for vulnerable app- shared_artifacts/test_ui_vuln.json: structured test casesFiles:un_all_ui.sh` in Git Bash or `.
un_all_ui.ps1` in PowerShell, depending on preferences.