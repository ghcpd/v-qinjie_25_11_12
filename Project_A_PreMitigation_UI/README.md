# Project A - Pre-Mitigation UI (Vulnerable)

This project demonstrates **vulnerable UI/frontend security** issues including XSS attacks and secrets exposure.

## Vulnerabilities Demonstrated

1. **Reflected XSS**: User input in comment forms is directly rendered without sanitization
2. **DOM-based XSS**: Unsafe use of `innerHTML` allows script injection
3. **Secrets Exposure**: API keys and tokens are exposed in:
   - HTML templates
   - JavaScript code
   - Console logs
   - localStorage
   - Debug panels

## Setup

### Prerequisites
- Python 3.8+
- pip
- bash (or Git Bash on Windows)

### Installation

```bash
cd Project_A_PreMitigation_UI
pip install -r requirements.txt
playwright install chromium
```

## Running the Application

### Start the server manually:
```bash
python src/app.py
```

The application will be available at `http://localhost:5000`

### Run automated tests:
```bash
chmod +x run_ui_tests.sh
./run_ui_tests.sh
```

Or with custom parameters:
```bash
./run_ui_tests.sh [repeat_count] [browser_type] [viewport_width] [viewport_height]
```

## Test Scenarios

The application includes the following vulnerable endpoints:

1. **`/`** - Main page with comment form (exposes API key in debug panel)
2. **`/comment`** - Comment submission endpoint (vulnerable to reflected XSS)
3. **`/api/user-info`** - API endpoint exposing sensitive user data
4. **`/search`** - Search results page (vulnerable to reflected XSS)

## Expected Vulnerabilities

When running tests, you should observe:

- **XSS Success Rate**: High (vulnerabilities are present)
- **Secrets Exposure Rate**: 100% (API keys visible in multiple locations)
- **Security Score**: Low (indicating poor security posture)

## Test Results

After running tests, check:
- `results/results_pre.json` - Detailed test results and metrics
- `screenshots/` - Screenshots of test execution
- `logs/server.log` - Server logs

## Limitations

This is a simplified demonstration application. Real-world applications may have:
- More complex attack vectors
- Additional security layers (WAF, rate limiting)
- More sophisticated XSS payloads
- Multiple entry points for attacks

## Security Recommendations

See Project B (Post-Mitigation) for proper security implementations:
- Input sanitization and validation
- Content Security Policy (CSP) headers
- Safe DOM manipulation (textContent instead of innerHTML)
- Secrets management (environment variables, not hardcoded)
- Debug mode disabled in production

