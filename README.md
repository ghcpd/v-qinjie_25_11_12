# UI Security Demo — Pre/Post Mitigation Projects

This workspace includes two Flask-based UI demo projects: a vulnerable pre-mitigation project and a patched post-mitigation project. Each project is self-contained and includes Playwright-based tests to validate XSS and secrets exposure scenarios.

Folders:
- `Project_A_PreMitigation_UI/`: Vulnerable app with reflected and DOM XSS and debug secrets.
- `Project_B_PostMitigation_UI/`: Patched app with sanitization, CSP, and secret masking.
- `test_ui_vuln.json`: Input payloads and metadata used for tests.
- `run_all_ui.sh`: Runs both projects’ tests and creates `compare_ui_security_report.md` for comparison.

Requirements:
- Python 3.8+ with virtual environment recommendation
- Playwright browsers: installed with `python -m playwright install`

Quick start (PowerShell):
> cd Project_A_PreMitigation_UI; ./run_ui_tests.ps1
> cd Project_B_PostMitigation_UI; ./run_ui_tests.ps1
> cd ..; ./run_all_ui.ps1

Optional parameters (to tune tests):
- Use `--repeat <N>` to repeat tests (default: 1)
- Use `--browser chromium|firefox|webkit` to switch browser (default chromium)
- Use `--viewport WIDTHxHEIGHT` to override viewport size

Examples:
> ./run_ui_tests.ps1 --repeat 3 --browser firefox --viewport 1280x720

Results will be in `Project_*/results_*.json` and artifacts under each project `results/` folder (screenshots & logs).

Limitations & Notes:
- This demo uses Playwright headless chromium. You can configure other browsers using `test_ui_vuln.json`.
- CSP is set in the patched app; the demo uses external JS rather than inline JS.

Security Checks & Acceptance:
- XSS attack success is detected by listening for certain global markers or DOM modifications (e.g., window.__XSS_REFLECTED or window.__XSS_DOM).
- Secrets exposures are detected by checking if `FAKE-SECRET-ABC-123` appears in DOM, console, or localStorage.

If you need a Dockerfile or additional CI we can add it; for now run in local Python environment.
