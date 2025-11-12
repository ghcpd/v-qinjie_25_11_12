import json
import os
import subprocess
import time
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'test_ui_vuln.json'))

PROG = 'python'
SERVER_CMD = [PROG, 'src/app.py']
HOST = 'http://127.0.0.1:5000'

# Start the server

def start_server():
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    # Redirect stdout/stderr to files for easier debugging
    out_path = os.path.join(ROOT, 'results', 'server_stdout.log')
    err_path = os.path.join(ROOT, 'results', 'server_stderr.log')
    out_f = open(out_path, 'wb')
    err_f = open(err_path, 'wb')
    proc = subprocess.Popen(SERVER_CMD, cwd=ROOT, stdout=out_f, stderr=err_f)
    return proc


def wait_server_available(timeout=30.0):
    import requests
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(HOST, timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.5)
    return False


def run_tests(repeat=1, browser_name='chromium', override_viewport=None):
    with open(TEST_DATA, 'r', encoding='utf-8') as fh:
        cases = json.load(fh)

    results = []
    summary = { 'total': 0, 'xss_success': 0, 'secrets_exposed': 0 }

    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=True)
        for i in range(repeat):
            for case in cases:
                summary['total'] += 1
                start_time = time.time()
                test_id = case['test_id']
                payload = case['input_payload']
                env = case['env']
                expected = case['expected_behavior']

                details = {'test_id': test_id, 'payload': payload, 'expected': expected, 'result': 'fail', 'error': None}

                try:
                    # Use override viewport if provided; else case viewport
                    if override_viewport:
                        width, height = map(int, override_viewport.split('x'))
                    else:
                        width, height = map(int, env['viewport'].split('x'))

                    page = browser.new_page(viewport={ 'width': width, 'height': height })
                    # Listen to console messages for secrets leakage
                    leaked_console = []
                    page.on('console', lambda msg: leaked_console.append(msg.text))

                    # Install a sentinel variable watcher to detect alerts
                    page.evaluate('() => { window.__XSS_REFLECTED = false; window.__XSS_DOM = false; window.alert = function(){ window.__alert_called = true; } }')

                    # Prepare query param for reflected test
                    url = HOST + '/?comment=' + payload
                    page.goto(url, timeout=60000)

                    # For reflected test, page loaded with comment as parameter
                    reflected_var = page.evaluate('() => window.__XSS_REFLECTED')
                    # Are script tags executed? In this app, it would execute the script payload if the payload includes script tags (Reflected)
                    # To detect this, our payload set a marker window.__XSS_REFLECTED - captured via payload
                    reflected_exec = page.evaluate('() => typeof window.__XSS_REFLECTED !== "undefined" && window.__XSS_REFLECTED')

                    # DOM insertion test: type payload into form, click 'Insert' to trigger innerHTML update
                    page.fill('#comment', payload)
                    page.click('#insert-dom')
                    # wait a small while
                    page.wait_for_timeout(300)
                    dom_exec = page.evaluate('() => typeof window.__XSS_DOM !== "undefined" && window.__XSS_DOM')

                    # Secrets: check DOM text for the fake API key or debug panel
                    page_content = page.content()
                    api_key_present = 'FAKE-SECRET-ABC-123' in page_content
                    local_secret = page.evaluate('() => window.localStorage.getItem("api_key")')

                    # Determine outcomes
                    xss_found = reflected_exec or dom_exec
                    secret_leaked = api_key_present or (local_secret is not None and 'FAKE-SECRET' in local_secret) or any('FAKE-SECRET' in str(x) for x in leaked_console)

                    # Save screenshot for evidence
                    screenshot_path = os.path.join(ROOT, 'results', f'{test_id}_iteration{i}.png')
                    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                    page.screenshot(path=screenshot_path, full_page=True)

                    # Determine pass/fail for this case (vulnerable app expect vulnerabilities)
                    if case['test_id'] == 'normal-01':
                        passed = not xss_found and not secret_leaked
                    elif case['test_id'] in ('reflected-xss-01', 'dom-xss-01'):
                        passed = xss_found  # In vulnerable app we expect vulnerabilities
                    elif case['test_id'] == 'secrets-exposure-01':
                        passed = secret_leaked
                    else:
                        passed = not xss_found and not secret_leaked

                    details['result'] = 'pass' if passed else 'fail'
                    details['elapsed_ms'] = int((time.time() - start_time) * 1000)
                    details['xss_found'] = bool(xss_found)
                    details['secret_leaked'] = bool(secret_leaked)

                    if xss_found:
                        summary['xss_success'] += 1
                    if secret_leaked:
                        summary['secrets_exposed'] += 1

                    results.append(details)
                    try:
                        page.close()
                    except Exception:
                        pass

                except Exception as ex:
                    details['error'] = str(ex)
                    results.append(details)

        browser.close()

    # Summary metrics
    total = summary['total']
    xss_success_pct = (summary['xss_success'] / total) * 100 if total else 0.0
    secrets_exposed_pct = (summary['secrets_exposed'] / total) * 100 if total else 0.0

    summary_payload = {
        'total_tests': total,
        'xss_success_count': summary['xss_success'],
        'secrets_exposed_count': summary['secrets_exposed'],
        'xss_success_pct': xss_success_pct,
        'secrets_exposed_pct': secrets_exposed_pct,
        'security_score': max(0, int(100 - (xss_success_pct + secrets_exposed_pct)))
    }

    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    with open(os.path.join(ROOT, 'results_pre.json'), 'w', encoding='utf-8') as fh:
        json.dump({'summary': summary_payload, 'tests': results}, fh, indent=2)

    return summary_payload


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--browser', choices=['chromium','firefox','webkit'], default='chromium')
    parser.add_argument('--viewport', type=str, default=None, help='Override viewport e.g. 1024x768')
    args = parser.parse_args()

    proc = start_server()
    try:
        if not wait_server_available(10.0):
            print('Server not responding on', HOST)
            proc.kill()
            raise SystemExit(1)
        print('Server started; running tests...')
        summary = run_tests(repeat=args.repeat, browser_name=args.browser, override_viewport=args.viewport)
        print('Finished tests; summary:', summary)
    finally:
        print('Stopping server')
        proc.terminate()
        proc.wait(timeout=5)

