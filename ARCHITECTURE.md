# Architecture & Design Document

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Test Orchestration Layer                     │
│                     (run_all_ui.py)                             │
└────────────────┬────────────────────────────────┬───────────────┘
                 │                                │
    ┌────────────▼──────────────┐    ┌───────────▼──────────────┐
    │  Project A: Vulnerable    │    │  Project B: Secure       │
    │  (Flask on 5000)          │    │  (Flask on 5001)         │
    ├───────────────────────────┤    ├──────────────────────────┤
    │ • No input sanitization   │    │ • Bleach sanitization    │
    │ • innerHTML usage         │    │ • Safe textContent       │
    │ • Hardcoded secrets       │    │ • Env variables for keys │
    │ • No CSP headers          │    │ • Strict CSP headers     │
    │ • Direct eval()           │    │ • No eval() execution    │
    └────────────┬──────────────┘    └──────────────┬───────────┘
                 │                                   │
    ┌────────────▼──────────────┐    ┌──────────────▼──────────┐
    │ Test Suite: test_pre_ui.py│    │ test_post_ui.py         │
    │                           │    │                         │
    │ • Detects vulnerabilities │    │ • Validates mitigations │
    │ • Runs 8 test scenarios   │    │ • Runs 8 test scenarios │
    │ • Measures attack success │    │ • Measures block rates   │
    │ • Detects secrets         │    │ • Verifies secrets safe  │
    └────────────┬──────────────┘    └──────────────┬──────────┘
                 │                                   │
                 └────────────────┬──────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │  Comparison Report Gen     │
                    │  (generate_comparison_    │
                    │   report())               │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │ Output: Markdown Report    │
                    │ + JSON Results             │
                    │ + Security Metrics         │
                    └────────────────────────────┘
```

## Test Execution Flow

```
START
  │
  ├─► Install Dependencies
  │    └─► pip install -r requirements.txt
  │
  ├─► Start Project A Server (Port 5000)
  │    └─► python Project_A_PreMitigation_UI/src/app.py
  │
  ├─► Start Project B Server (Port 5001)
  │    └─► python Project_B_PostMitigation_UI/src/app.py
  │
  ├─► Run Pre-Mitigation Tests
  │    ├─► TEST_001: Normal Input
  │    ├─► TEST_002: Reflected XSS
  │    ├─► TEST_003: DOM XSS
  │    ├─► TEST_004: Secrets Exposure
  │    ├─► TEST_005: Edge Cases
  │    ├─► TEST_006: Event Handlers
  │    ├─► TEST_007: Data Exfiltration
  │    └─► TEST_008: SVG XSS
  │
  ├─► Run Post-Mitigation Tests
  │    ├─► TEST_001-008 (Same scenarios)
  │    └─► Verify all mitigations work
  │
  ├─► Generate Comparison Report
  │    ├─► Load both result sets
  │    ├─► Calculate metrics
  │    └─► Generate Markdown report
  │
  ├─► Stop Servers
  │    ├─► Terminate Project A
  │    └─► Terminate Project B
  │
  └─► END
```

## Vulnerability Detection Logic

### XSS Detection Algorithm

```python
def detect_xss(payload):
    1. Send payload to vulnerable endpoint
    2. Check for JavaScript alert() execution
    3. If alert triggers:
       ├─ XSS_SUCCESSFUL = True
       ├─ Log severity: CRITICAL
       └─ Mark test as FAILED
    4. Else:
       ├─ XSS_BLOCKED = True
       └─ Mark test as PASSED
```

### Secrets Detection Algorithm

```python
def detect_secrets(page_source, console_logs):
    secrets_patterns = {
        'api_key': ['sk-', 'api_key', 'api-key'],
        'db_password': ['admin_db_password', 'db_password'],
        'jwt_token': ['eyjaalgcihsijin', 'jwt_secret'],
        'session': ['sess_prod_secret', 'session_id']
    }
    
    for pattern in secrets_patterns:
        if pattern in (page_source.lower() or console_logs.lower()):
            ├─ SECRET_EXPOSED = True
            ├─ Log: Information Disclosure vulnerability
            └─ Mark test as FAILED
    
    if not secrets_found:
        └─ SECRETS_PROTECTED = True
```

## Security Mitigation Strategy

### Layer 1: Input Validation
```python
def validate_input(user_input):
    ├─ Check type: must be string
    ├─ Check length: max 5000 chars
    ├─ Check for null bytes
    └─ Check for excessive nesting
```

### Layer 2: Sanitization
```python
def sanitize_input(user_input):
    ├─ Use Bleach library
    ├─ Define whitelist of allowed tags: b, i, u, p, br, a
    ├─ Define allowed attributes: a[href, title]
    ├─ Strip unknown tags instead of escaping
    └─ Return sanitized output
```

### Layer 3: Encoding
```python
def encode_output(text):
    ├─ Use MarkupSafe.escape()
    ├─ Convert special chars: &, <, >, ", '
    └─ Return HTML-safe string
```

### Layer 4: DOM Manipulation
```javascript
// UNSAFE (Pre-Mitigation)
element.innerHTML = user_input;  // ❌

// SAFE (Post-Mitigation)
element.textContent = user_input;  // ✓
// OR
const node = document.createElement('div');
node.textContent = user_input;
element.appendChild(node);  // ✓
```

### Layer 5: Content Security Policy
```
Content-Security-Policy:
  ├─ default-src 'self'
  ├─ script-src 'self'
  ├─ style-src 'self' 'unsafe-inline'
  ├─ img-src 'self' data:
  ├─ font-src 'self'
  ├─ connect-src 'self'
  └─ frame-ancestors 'none'
```

## Test Case Design

### Test Structure
```json
{
  "test_id": "TEST_002",
  "test_name": "Reflected XSS - Script Alert",
  "category": "reflected_xss",
  "input_payload": "<script>alert('XSS_VULNERABILITY_DETECTED')</script>",
  "input_field": "comment_box",
  "environment": {
    "browser": "chrome",
    "js_enabled": true,
    "viewport": "1920x1080"
  },
  "expected_behavior": "Script should NOT execute",
  "pass_criteria": [
    "No alert() dialog appears",
    "Script tag visible as escaped text",
    "No JavaScript execution",
    "HTML special characters are escaped"
  ]
}
```

### Test Execution Steps
1. Navigate to application URL
2. Locate input element by ID
3. Send payload (malicious string)
4. Submit form
5. Wait for response
6. Check for alert() execution
7. Check page source for secrets
8. Log results
9. Move to next test

## Metrics Calculation

### Security Score (Pre-Mitigation)
```
Security_Score = (Vulnerabilities_Found / Total_Tests) * 100

Example: 7/8 = 87.5% (Lower = More Vulnerable)
```

### Success Rate (Post-Mitigation)
```
Success_Rate = (Tests_Passed / Total_Tests) * 100

Example: 8/8 = 100.0% (Higher = More Secure)
```

### Attack Success Rate
```
Attack_Rate = (XSS_Successful + Secrets_Exposed + ...) / Total_Tests * 100
```

### Improvement Metric
```
Improvement = Post_Score - Pre_Score

Example: 100.0 - 12.5 = 87.5% improvement
```

## Database/State Management

### Pre-Mitigation Storage
```python
comments = []  # In-memory list

comment_entry = {
    'id': int,
    'text': str,        # UNSAFE: No sanitization
    'timestamp': str,
    'author': str       # UNSAFE: No sanitization
}
```

### Post-Mitigation Storage
```python
comments = []  # In-memory list

comment_entry = {
    'id': int,
    'text': str,        # SAFE: Bleach sanitized
    'timestamp': str,
    'author': str       # SAFE: Bleach sanitized
}
```

## Error Handling

### Pre-Mitigation (Minimal)
```python
try:
    # Direct operations, may fail silently
except:
    pass  # Errors not logged
```

### Post-Mitigation (Robust)
```python
try:
    # Validated operations
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    sanitized = sanitize_input(user_input)
    # Process sanitized data
    
except Exception as e:
    logger.error(f"Error: {e}")
    return jsonify({'error': 'Server error'}), 500
```

## Performance Considerations

### Pre-Mitigation
- No sanitization overhead
- Faster response times
- Memory: ~10KB per 100 comments

### Post-Mitigation
- Sanitization: 1-2ms per request
- CSP header parsing: <1ms
- Bleach processing: 0.5-1.5ms
- Total overhead: 2-4ms (negligible)
- Memory: ~10KB per 100 comments

## Security Checklist

✅ **Pre-Mitigation Issues**
- [ ] No input validation
- [ ] No output encoding
- [ ] innerHTML with user data
- [ ] Hardcoded secrets
- [ ] No security headers
- [ ] eval() usage
- [ ] Debug panel exposed
- [ ] No CSRF protection

✅ **Post-Mitigation Fixes**
- [x] Input sanitization (Bleach)
- [x] Output encoding (MarkupSafe)
- [x] Safe DOM updates (textContent)
- [x] Secrets in env variables
- [x] CSP and security headers
- [x] No eval() usage
- [x] No debug panel
- [x] Safe form handling

---

**Document Version:** 1.0
**Last Updated:** November 12, 2024
