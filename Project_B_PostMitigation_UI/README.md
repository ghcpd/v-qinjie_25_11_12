# Project B - Post-Mitigation UI (Secure)

This project demonstrates **secure UI/frontend practices** with proper mitigation of XSS attacks and secrets exposure.

## Security Implementations

1. **Input Sanitization**: All user input is sanitized using `bleach` library
2. **Safe DOM Manipulation**: Uses `textContent` instead of `innerHTML`
3. **Content Security Policy**: CSP headers prevent inline script execution
4. **Secrets Management**: API keys stored in environment variables, not hardcoded
5. **No Debug Exposure**: Debug panels removed, no secrets in templates
6. **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection

## Setup

### Prerequisites
- Python 3.8+
- pip
- bash (or Git Bash on Windows)

### Installation

```bash
cd Project_B_PostMitigation_UI
pip install -r requirements.txt
playwright install chromium
```

### Environment Variables (Optional)

For production-like setup:
```bash
export API_KEY="your_api_key_here"
export SECRET_TOKEN="your_secret_token_here"
export DEBUG_MODE="False"
```

## Running the Application

### Start the server manually:
```bash
python src/app.py
```

The application will be available at `http://localhost:5001`

### Run automated tests:
```bash
chmod +x run_ui_tests.sh
./run_ui_tests.sh
```

Or with custom parameters:
```bash
./run_ui_tests.sh [repeat_count] [browser_type] [viewport_width] [viewport_height]
```

## Security Features

### 1. Input Sanitization
- All user inputs are sanitized using `bleach.clean()`
- Only safe HTML tags allowed: `p`, `br`, `strong`, `em`, `u`
- All script tags and event handlers are stripped

### 2. Content Security Policy
- CSP headers prevent inline script execution
- Only allows scripts from same origin
- Blocks `eval()` and inline event handlers

### 3. Safe DOM Updates
- Uses `textContent` instead of `innerHTML`
- Prevents DOM-based XSS attacks
- JSON serialization for safe data passing

### 4. Secrets Protection
- No API keys in templates or JavaScript
- Environment variables for sensitive data
- No secrets in localStorage or console logs

## Expected Security Metrics

When running tests, you should observe:

- **XSS Success Rate**: Low (0-5%) - vulnerabilities mitigated
- **Secrets Exposure Rate**: 0% - no secrets exposed
- **CSP Coverage**: 100% - all pages protected
- **Security Score**: High (90-100) - indicating good security posture

## Test Results

After running tests, check:
- `results/results_post.json` - Detailed test results and metrics
- `screenshots/` - Screenshots of test execution
- `logs/server.log` - Server logs

## Comparison with Pre-Mitigation

Key improvements:
- XSS attack success rate reduced by ≥95%
- Secrets exposure eliminated (100% reduction)
- CSP headers implemented
- Input validation and sanitization added
- Safe coding practices enforced

## Security Best Practices Applied

1. **Input Validation**: Validate and sanitize all user inputs
2. **Output Encoding**: Properly encode output before rendering
3. **CSP Headers**: Implement Content Security Policy
4. **Secrets Management**: Use environment variables, never hardcode
5. **Safe APIs**: Use `textContent` instead of `innerHTML`
6. **Security Headers**: Add security-related HTTP headers
7. **Debug Mode**: Disable debug mode in production

## Limitations

While this implementation addresses the demonstrated vulnerabilities:
- Real-world applications may require additional security layers
- Regular security audits and penetration testing recommended
- Keep dependencies updated for security patches
- Monitor for new attack vectors and update defenses accordingly

