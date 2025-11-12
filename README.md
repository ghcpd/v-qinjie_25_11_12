# SQL Injection Vulnerability Detection & Mitigation

## Overview

This project demonstrates vulnerability detection, exploitation, and mitigation in a controlled environment. It consists of two parallel Flask-based web services:

- **Project A (Pre-Mitigation):** Intentionally vulnerable application exposing SQL injection vulnerabilities
- **Project B (Post-Mitigation):** Hardened version implementing security best practices

Both projects are tested against identical attack vectors to quantitatively measure security improvements.

## Project Structure

```
├── README.md                              # This file
├── run_all.py                             # Root orchestration script
├── run_helper.py                          # Helper for virtual environment management
├── shared_resources/
│   └── test_data.json                     # Shared test cases (6 test vectors)
├── results/
│   ├── compare_report.md                  # Generated comparison report
│   ├── results_pre.json                   # Pre-mitigation metrics
│   └── results_post.json                  # Post-mitigation metrics
├── Project_A_PreMitigation_SQLi/
│   ├── src/
│   │   ├── app.py                         # Vulnerable Flask application
│   │   └── init_db.py                     # Database initialization
│   ├── data/
│   │   └── vulnerable.db                  # SQLite database (auto-created)
│   ├── tests/
│   │   └── test_pre_vuln.py               # Test harness for vulnerabilities
│   ├── logs/                              # Application and test logs
│   ├── results/
│   │   └── results_pre.json               # Test results
│   ├── requirements.txt
│   ├── run_tests.ps1                      # Windows test runner
│   └── run_tests.sh                       # Linux/Mac test runner
└── Project_B_PostMitigation_SQLi/
    ├── src/
    │   ├── app.py                         # Patched Flask application
    │   └── init_db.py                     # Database initialization
    ├── data/
    │   └── patched.db                     # SQLite database (auto-created)
    ├── tests/
    │   └── test_post_vuln.py              # Test harness for mitigations
    ├── logs/                              # Application and test logs
    ├── results/
    │   └── results_post.json              # Test results
    ├── requirements.txt
    ├── run_tests.ps1                      # Windows test runner
    └── run_tests.sh                       # Linux/Mac test runner
```

## Quick Start

### One-Command Execution

Run all tests and generate comparison report:

```bash
# Windows (PowerShell)
python run_all.py

# Linux/Mac
python run_all.py
```

This command will:
1. Execute Project A tests (vulnerable application)
2. Execute Project B tests (patched application)
3. Generate `compare_report.md` in the `results/` directory
4. Create `results_pre.json` and `results_post.json` with detailed metrics

### Individual Project Execution

Run individual project tests:

**Project A (Vulnerable):**
```bash
# Windows
cd Project_A_PreMitigation_SQLi
powershell -ExecutionPolicy Bypass -File run_tests.ps1

# Linux/Mac
cd Project_A_PreMitigation_SQLi
bash run_tests.sh
```

**Project B (Patched):**
```bash
# Windows
cd Project_B_PostMitigation_SQLi
powershell -ExecutionPolicy Bypass -File run_tests.ps1

# Linux/Mac
cd Project_B_PostMitigation_SQLi
bash run_tests.sh
```

## Requirements

- Python 3.8+
- Flask 2.3.3
- requests 2.31.0
- pytest 7.4.0
- SQLite3 (included with Python)

### Installation

The test runners automatically create virtual environments and install dependencies. No manual setup required.

Optional manual installation:
```bash
pip install flask requests pytest pytest-asyncio
```

## Test Scenario

### Vulnerability: SQL Injection via User Input

**Endpoint:** `/search?query=<user_input>`

**Vulnerable Code (Project A):**
```python
vulnerable_sql = f"SELECT * FROM users WHERE name LIKE '%{query_param}%'"
cursor.execute(vulnerable_sql)
```

**Patched Code (Project B):**
```python
secure_sql = "SELECT * FROM users WHERE name LIKE ?"
cursor.execute(secure_sql, (f'%{query_param}%',))
```

## Test Cases

The test suite includes 6 comprehensive test cases designed to expose and validate SQLi protections:

### TC001_NORMAL_QUERY
- **Description:** Normal safe query returning valid results
- **Payload:** `john`
- **Type:** Baseline (not an injection)
- **Expected Pre:** Returns matching user records
- **Expected Post:** Returns matching user records
- **Purpose:** Verify legitimate functionality preserved

### TC002_BASIC_INJECTION
- **Description:** Basic SQL injection: OR 1=1 to bypass WHERE clause
- **Payload:** `' OR '1'='1`
- **Type:** Classic SQLi
- **Expected Pre:** Returns all users (injection successful)
- **Expected Post:** Returns empty/error (attack blocked)
- **Purpose:** Test basic SQLi prevention

### TC003_ENCODED_INJECTION
- **Description:** URL-encoded SQL injection to bypass simple filters
- **Payload:** `%27%20OR%20%271%27%3D%271` (URL-encoded)
- **Type:** Encoding bypass attempt
- **Expected Pre:** Decodes and executes injection
- **Expected Post:** Safe handling, blocked
- **Purpose:** Test encoding bypass prevention

### TC004_BLIND_INJECTION
- **Description:** Time-based blind SQL injection with SLEEP
- **Payload:** `test' AND SLEEP(3)--`
- **Type:** Blind time-based SQLi
- **Expected Pre:** Response delayed ~3 seconds (confirms execution)
- **Expected Post:** Fast response, injection blocked
- **Purpose:** Test blind injection prevention via parameterization

### TC005_MALFORMED_INPUT
- **Description:** UNION-based injection for information_schema extraction
- **Payload:** `' UNION SELECT * FROM information_schema.tables--`
- **Type:** Advanced SQLi with schema extraction
- **Expected Pre:** May leak schema information
- **Expected Post:** Safe error, no leakage
- **Purpose:** Test schema protection

### TC006_UNION_BASED_INJECTION
- **Description:** Direct UNION injection with explicit column count
- **Payload:** `' UNION SELECT 1,2,3,4--`
- **Type:** Union-based SQLi
- **Expected Pre:** Unexpected columns returned
- **Expected Post:** Blocked with error
- **Purpose:** Test UNION injection prevention

## Test Metrics

The test suite measures the following security metrics:

### Key Metrics

| Metric | Description |
|--------|-------------|
| **Injection Success Rate** | % of injection attacks that succeeded |
| **Average Response Time** | Mean response time across all tests (ms) |
| **Information Leakage** | Presence of stack traces or sensitive data in errors |
| **Security Score** | 0-100 scale based on success criteria |

### Success Criteria

- **SQLi Success Rate Reduction ≥ 95%:** Attack success drops from high % to nearly 0%
- **Average Latency Increase ≤ 10%:** Security measures don't significantly slow performance
- **No Information Leakage:** No stack traces or database errors exposed to users

## Output

### Results JSON Format

**results_pre.json / results_post.json:**
```json
{
  "project": "Project_A_PreMitigation_SQLi",
  "timestamp": "2024-01-15T10:30:45.123456",
  "test_results": [
    {
      "test_id": "TC001_NORMAL_QUERY",
      "description": "...",
      "payload": "john",
      "is_injection": false,
      "status_code": 200,
      "response_time_ms": 45.23,
      "data_returned": true,
      "injection_successful": false,
      "leakage_detected": false,
      "passed": true
    }
  ],
  "metrics": {
    "total_tests": 6,
    "passed_tests": 4,
    "failed_tests": 2,
    "injection_success_count": 5,
    "injection_success_rate": 83.33,
    "avg_response_time_ms": 52.15,
    "leakage_detected": true,
    "security_score": 16
  }
}
```

### Comparison Report

**compare_report.md:** Comprehensive markdown report including:
- Executive summary
- Side-by-side metrics comparison
- Success criteria evaluation (✓ PASS / ✗ FAIL)
- Detailed test results table
- Vulnerabilities found and mitigations applied
- Production recommendations
- Limitations and future work
- Security improvement analysis

### Log Files

- **logs/app_output.log:** Flask application stdout
- **logs/app_error.log:** Flask application stderr
- **logs/test.log:** Test execution log with debug information

## Vulnerabilities Detected & Mitigations

### Vulnerability 1: Direct SQL String Concatenation

**Issue:** Queries constructed via string concatenation allow attacker-controlled input to modify query logic.

**Mitigation:** Replace with parameterized queries using placeholder syntax.

```python
# VULNERABLE
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# SECURE
cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))
```

### Vulnerability 2: No Input Validation

**Issue:** Application accepts any input without length limits or content validation.

**Mitigation:** Implement input validation decorators with:
- Maximum length enforcement
- SQL keyword detection and rejection
- Pattern-based validation

```python
@validate_input('query', max_length=100)
def search():
    # Input automatically validated before reaching this point
```

### Vulnerability 3: Information Leakage

**Issue:** Exception details and SQL errors exposed in HTTP responses.

**Mitigation:** Return generic error messages; log details securely server-side.

```python
# VULNERABLE
return jsonify({'error': str(database_error)}), 500

# SECURE
logger.error(f"Database error: {database_error}")
return jsonify({'error': 'An error occurred'}), 500
```

## Interpreting Results

### Security Score Interpretation

- **0-25:** Highly vulnerable, immediate action required
- **25-50:** Significant vulnerabilities present
- **50-75:** Some protections present, improvements needed
- **75-100:** Well-protected, minimal injection risk

### Injection Success Rate

- **> 80%:** Critical - application is vulnerable
- **50-80%:** Severe - multiple injection vectors successful
- **20-50%:** Significant - basic protections bypassed
- **0-20%:** Good - most attacks blocked
- **0%:** Excellent - all injection attempts blocked

### Information Leakage

- **Detected:** Application leaks sensitive information (database errors, stack traces)
- **Not Detected:** Application properly handles errors without information exposure

## Performance Impact

The patched application should show minimal performance degradation:

```
Typical latency comparison:
- Pre-Mitigation:  45-55 ms average
- Post-Mitigation: 48-58 ms average
- Overhead:        ~5-10% (acceptable for security benefit)
```

## Production Recommendations

### Immediate Actions

1. **Deploy Patched Version**
   - Use Project B code as baseline
   - Comprehensive code review before deployment
   - Staged rollout with monitoring

2. **Implement WAF**
   - Deploy Web Application Firewall (ModSecurity, AWS WAF, etc.)
   - Configure for OWASP Top 10
   - Monitor and alert on blocked requests

3. **Enable Logging & Monitoring**
   - Centralized security event logging
   - Alert on multiple failed authentication attempts
   - Monitor for SQL injection patterns

### Short-term (1-3 months)

1. **Security Testing**
   - Integrate this test suite into CI/CD pipeline
   - Run automated tests on every deployment
   - Add additional test cases for new features

2. **Code Review Process**
   - Implement security-focused code reviews
   - Require review of all database operations
   - Use static analysis tools (Bandit, SAST)

3. **Database Hardening**
   - Implement least-privilege database accounts
   - Disable dangerous SQL functions
   - Enable database audit logging

### Long-term (3-12 months)

1. **Advanced Security**
   - Implement WAF machine learning rules
   - Conduct penetration testing
   - Database activity monitoring
   - Incident response procedures

2. **Development Practices**
   - Security training for developers
   - Secure coding guidelines
   - Threat modeling for new features
   - Security champions program

3. **Continuous Improvement**
   - Monthly security audits
   - Vulnerability scanning
   - Penetration testing (quarterly)
   - Incident post-mortems

## Limitations

### Current Scope

- **Simplified Environment:** Single SQLite database vs. enterprise databases
- **Limited Scenarios:** Focused on SQLi; other vulnerabilities not tested
- **Basic Authentication:** No OAuth, JWT, or SSO testing
- **Single-threaded:** Flask development server; production uses WSGI servers
- **Small Dataset:** 5 users vs. enterprise-scale data

### Not Covered

- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Authentication bypass (beyond SQLi)
- Authorization issues
- Rate limiting/DoS
- Cryptographic vulnerabilities
- Session management flaws

### Database Support

Currently tested on SQLite only. Future versions should test:
- PostgreSQL
- MySQL/MariaDB
- SQL Server
- Oracle

## Troubleshooting

### Issue: "Address already in use"

**Cause:** Flask port still in use from previous run
**Solution:**
```bash
# Windows
Get-Process -Name python | Stop-Process -Force

# Linux/Mac
pkill -f "flask" || pkill -f "python app.py"
```

### Issue: "Module not found" errors

**Cause:** Virtual environment not created or dependencies not installed
**Solution:** Delete venv directory and re-run tests (auto-reinstalls)
```bash
rm -rf */venv  # Linux/Mac
rmdir /s /q venv  # Windows
```

### Issue: Permission denied on run_tests.sh

**Cause:** Script not executable
**Solution:**
```bash
chmod +x Project_*/run_tests.sh
```

### Issue: Tests timeout or hang

**Cause:** Flask app didn't start properly
**Solution:**
```bash
# Check if Flask is running
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Kill and restart
```

## File Modifications Guide

### To Add New Test Cases

Edit `shared_resources/test_data.json`:
```json
{
  "test_id": "TC007_CUSTOM_TEST",
  "description": "Description of test",
  "input_payload": "test payload",
  "is_injection": true,
  "environment": {
    "db_load": "normal",
    "network_latency_ms": 5
  },
  "expected_behavior": "Expected outcome",
  "pass_criteria": {
    "status_code": 400,
    "injection_successful": false
  }
}
```

### To Modify Vulnerable Application

Edit `Project_A_PreMitigation_SQLi/src/app.py`:
- Keep vulnerabilities intentional for demonstration
- Do not add patches here
- Document vulnerabilities clearly

### To Modify Patched Application

Edit `Project_B_PostMitigation_SQLi/src/app.py`:
- Implement additional security measures
- Add new validation rules
- Update error handling

## API Documentation

### Project A & B Common Endpoints

#### GET /search
Search for users by name (vulnerable to SQLi in Project A)

**Request:**
```
GET /search?query=john
```

**Response:**
```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "id": 2,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user"
    }
  ]
}
```

#### POST /login
Authenticate user (vulnerable to SQLi in Project A)

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Authentication successful",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

#### GET /health
Health check

**Response:**
```json
{
  "status": "healthy",
  "service": "vulnerable-api"
}
```

## Sample Test Execution

```bash
$ python run_all.py

======================================================================
SQL Injection Vulnerability Detection & Mitigation
Root Orchestration Script
======================================================================

======================================================================
Running Project A (Pre-Mitigation)...
======================================================================

========================================
Project A: Pre-Mitigation Tests
========================================

Initializing database...
Database initialized at: .../Project_A_PreMitigation_SQLi/data/vulnerable.db
Sample users: 5

Starting Flask application...
Flask app started with PID: 12345
Running tests...
Testing TC001_NORMAL_QUERY: john...
Testing TC002_BASIC_INJECTION: ' OR '1'='1...
Testing TC003_ENCODED_INJECTION: %27%20OR%20%271%27%3D%271...
Testing TC004_BLIND_INJECTION: test' AND SLEEP(3)--...
Testing TC005_MALFORMED_INPUT: ' UNION SELECT * FROM information_schema.tables--...
Testing TC006_UNION_BASED_INJECTION: ' UNION SELECT 1,2,3,4--...

Vulnerability Test Summary (Pre-Mitigation):
  Total Tests: 6
  Passed: 1
  Failed: 5
  Injection Success Rate: 83.33%
  Avg Response Time: 287.45ms
  Leakage Detected: True
  Security Score: 16/100

========================================
Test Run Completed
Results: .../results/results_pre.json
Logs: .../logs
========================================

[Similar output for Project B...]

======================================================================
Generating Comparison Report...
======================================================================

Comparison report generated: .../results/compare_report.md

======================================================================
SUCCESS: All tests completed and report generated
======================================================================

Key Results:
  Pre-Mitigation Injection Rate: 83.33%
  Post-Mitigation Injection Rate: 0.00%
  Improvement: 83.33%

Report Location: .../results/compare_report.md
Results Directory: .../results
```

## References & Standards

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **CWE-89: SQL Injection:** https://cwe.mitre.org/data/definitions/89.html
- **OWASP SQL Injection:** https://owasp.org/www-community/attacks/SQL_Injection
- **OWASP Testing Guide:** https://owasp.org/www-project-web-security-testing-guide/

## License

This project is provided for educational and security testing purposes.

## Support

For issues, questions, or contributions:
1. Check the Troubleshooting section
2. Review test output logs in `*/logs/` directories
3. Verify Python version: `python --version` (requires 3.8+)

---

**Project:** SQL Injection Vulnerability Detection & Mitigation  
**Version:** 1.0  
**Last Updated:** 2024-01-15  
**Status:** Production Ready
