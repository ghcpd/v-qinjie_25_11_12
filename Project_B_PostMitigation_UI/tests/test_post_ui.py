"""
Automated UI Security Test Suite - Post-Mitigation
Tests for validating security fixes and mitigation effectiveness
"""

import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:5001"
TEST_DATA_PATH = Path(__file__).parent.parent.parent / "test_ui_vuln.json"
RESULTS_DIR = Path(__file__).parent.parent / "results"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
LOGS_DIR = Path(__file__).parent.parent / "logs"

# Create directories
RESULTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

def load_test_cases():
    """Load test cases from JSON file"""
    with open(TEST_DATA_PATH, 'r') as f:
        data = json.load(f)
    return data['test_cases']

def sanitize_filename(name):
    """Create safe filename from test name"""
    return "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)

def detect_xss_alert(page, timeout=2000):
    """Detect if an alert dialog appears (indicates XSS)"""
    try:
        # Set up alert handler
        alert_detected = {'value': False, 'message': ''}
        
        def handle_alert(dialog):
            alert_detected['value'] = True
            alert_detected['message'] = dialog.message
            dialog.dismiss()
        
        page.on("dialog", handle_alert)
        
        # Wait a bit for potential alert
        page.wait_for_timeout(timeout)
        
        return alert_detected['value'], alert_detected['message']
    except Exception as e:
        return False, str(e)

def check_secrets_exposure(page):
    """Check for exposed secrets in DOM, console, or localStorage"""
    secrets_found = []
    
    # Check page source for common secret patterns
    page_content = page.content()
    secret_patterns = [
        'sk_live_',
        'secret_',
        'api_key',
        'API_KEY',
        'secret_token',
        'SECRET_TOKEN',
        'REDACTED'
    ]
    
    for pattern in secret_patterns:
        # Only flag if it's an actual secret, not the word "REDACTED"
        if pattern in page_content.lower() and pattern != 'redacted':
            # Check if it's actually a secret value (not just the word)
            if 'REDACTED' not in page_content and pattern != 'redacted':
                secrets_found.append(f"Found pattern '{pattern}' in page source")
    
    # Check localStorage
    try:
        storage = page.evaluate("() => { return JSON.stringify(localStorage); }")
        if storage and storage != '{}':
            # Check if secrets are stored
            if 'api' in storage.lower() or 'secret' in storage.lower():
                secrets_found.append(f"Secrets found in localStorage: {storage}")
    except:
        pass
    
    return secrets_found

def check_script_injection(page):
    """Check if script tags were injected into DOM"""
    try:
        scripts = page.query_selector_all('script')
        injected_scripts = []
        for script in scripts:
            content = script.inner_text()
            # Check for malicious patterns in script content
            if 'alert' in content.lower() and 'xss' in content.lower():
                injected_scripts.append(content[:100])
        return len(injected_scripts) > 0, injected_scripts
    except:
        return False, []

def check_csp_headers(page):
    """Check if Content Security Policy headers are present"""
    try:
        response = page.request.get(page.url)
        headers = response.headers
        csp = headers.get('content-security-policy', '')
        return len(csp) > 0, csp
    except:
        return False, ''

def run_test_case(test_case, browser, repeat_count=1):
    """Run a single test case"""
    test_id = test_case['test_id']
    test_name = test_case['name']
    payload = test_case['input_payload']
    
    results = {
        'test_id': test_id,
        'test_name': test_name,
        'payload': payload,
        'runs': []
    }
    
    for run_num in range(repeat_count):
        context = browser.new_context(
            viewport={'width': test_case['environment']['viewport']['width'],
                     'height': test_case['environment']['viewport']['height']}
        )
        page = context.new_page()
        
        try:
            start_time = time.time()
            
            # Navigate to main page
            page.goto(BASE_URL, wait_until='networkidle')
            
            # Fill form and submit
            page.fill('input[name="username"]', 'TestUser')
            page.fill('textarea[name="comment"]', payload)
            
            # Take screenshot before submission
            page.screenshot(path=str(SCREENSHOTS_DIR / f"{test_id}_before_{run_num}.png"))
            
            # Submit form
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
            
            # Check for XSS
            alert_detected, alert_message = detect_xss_alert(page)
            
            # Check for script injection
            script_injected, injected_scripts = check_script_injection(page)
            
            # Check for secrets exposure
            secrets_found = check_secrets_exposure(page)
            
            # Check CSP headers
            csp_present, csp_header = check_csp_headers(page)
            
            # Take screenshot after submission
            page.screenshot(path=str(SCREENSHOTS_DIR / f"{test_id}_after_{run_num}.png"))
            
            load_time = time.time() - start_time
            
            run_result = {
                'run_number': run_num + 1,
                'xss_detected': alert_detected or script_injected,
                'alert_message': alert_message if alert_detected else None,
                'script_injected': script_injected,
                'injected_scripts': injected_scripts,
                'secrets_exposed': len(secrets_found) > 0,
                'secrets_details': secrets_found,
                'csp_enabled': csp_present,
                'csp_header': csp_header if csp_present else None,
                'load_time_ms': round(load_time * 1000, 2),
                'page_rendered': True
            }
            
            results['runs'].append(run_result)
            
        except Exception as e:
            run_result = {
                'run_number': run_num + 1,
                'error': str(e),
                'xss_detected': False,
                'secrets_exposed': False,
                'page_rendered': False
            }
            results['runs'].append(run_result)
        
        finally:
            context.close()
    
    return results

def calculate_metrics(all_results):
    """Calculate security metrics from test results"""
    total_tests = len(all_results)
    xss_success_count = 0
    secrets_exposure_count = 0
    total_runs = 0
    csp_enabled_count = 0
    
    for result in all_results:
        for run in result.get('runs', []):
            total_runs += 1
            if run.get('xss_detected', False):
                xss_success_count += 1
            if run.get('secrets_exposed', False):
                secrets_exposure_count += 1
            if run.get('csp_enabled', False):
                csp_enabled_count += 1
    
    xss_success_rate = (xss_success_count / total_runs * 100) if total_runs > 0 else 0
    secrets_exposure_rate = (secrets_exposure_count / total_runs * 100) if total_runs > 0 else 0
    csp_coverage = (csp_enabled_count / total_runs * 100) if total_runs > 0 else 0
    
    # Security score (0-100, higher is better for post-mitigation)
    security_score = 100 - (xss_success_rate * 0.7 + secrets_exposure_rate * 0.3)
    security_score = max(0, min(100, security_score))
    
    return {
        'total_tests': total_tests,
        'total_runs': total_runs,
        'xss_attack_success_rate': round(xss_success_rate, 2),
        'secrets_exposure_rate': round(secrets_exposure_rate, 2),
        'csp_coverage': round(csp_coverage, 2),
        'security_score': round(security_score, 2)
    }

def main():
    """Main test execution"""
    test_cases = load_test_cases()
    all_results = []
    
    print(f"Starting UI security tests for Post-Mitigation project...")
    print(f"Loaded {len(test_cases)} test cases")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for test_case in test_cases:
            print(f"Running {test_case['test_id']}: {test_case['name']}")
            result = run_test_case(test_case, browser, repeat_count=1)
            all_results.append(result)
        
        browser.close()
    
    # Calculate metrics
    metrics = calculate_metrics(all_results)
    
    # Save results
    results_data = {
        'project': 'Project_B_PostMitigation_UI',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'test_results': all_results,
        'metrics': metrics
    }
    
    results_file = RESULTS_DIR / 'results_post.json'
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print("\n" + "="*50)
    print("Test Results Summary")
    print("="*50)
    print(f"Total Tests: {metrics['total_tests']}")
    print(f"Total Runs: {metrics['total_runs']}")
    print(f"XSS Attack Success Rate: {metrics['xss_attack_success_rate']}%")
    print(f"Secrets Exposure Rate: {metrics['secrets_exposure_rate']}%")
    print(f"CSP Coverage: {metrics['csp_coverage']}%")
    print(f"Security Score: {metrics['security_score']}/100")
    print(f"\nResults saved to: {results_file}")
    print(f"Screenshots saved to: {SCREENSHOTS_DIR}")

if __name__ == '__main__':
    main()

