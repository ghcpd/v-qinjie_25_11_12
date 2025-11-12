import json
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

RESULTS_DIR = Path(os.path.join(os.getcwd(), 'results')).resolve()
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5002')

# Find repo root and load the shared test data JSON
REPO_ROOT = Path(__file__).resolve().parents[2]
with open(REPO_ROOT / 'test_ui_vuln.json') as f:
    TEST_CASES = json.load(f)

results = []

browser = None
console_msgs = []

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Collect console messages
        page.on('console', lambda msg: console_msgs.append(msg.text))

        for tc in TEST_CASES:
            tc_id = tc['test_id']
            payload = tc['input_payload']
            print(f"Running test {tc_id}: {payload}")

            attack_success = False
            secret_leak = False
            dom_injection = False

            # Register a fresh dialog handler for this test
            dialog_flag = {'val': False}
            def make_dialog_handler(flag):
                def handler(dialog):
                    flag['val'] = True
                    dialog.dismiss()
                return handler
            page.on('dialog', make_dialog_handler(dialog_flag))

            try:
                if tc.get('trigger') == 'secrets':
                    page.goto(BASE_URL)
                    time.sleep(0.2)
                else:
                    page.goto(BASE_URL)
                    page.fill('#comment', payload)
                    page.click('button[type=submit]')
                    time.sleep(0.5)

                # If payload is a DOM XSS flagged as 'dangerous', also visit with dangerous param
                if 'dangerous' in tc.get('trigger', ''):
                    url = f"{BASE_URL}/?dangerous={payload}"
                    page.goto(url)

                time.sleep(0.5)

                # Check DOM for inserted <script> tags or inline event handlers
                scripts = page.query_selector_all('script')
                if scripts and len(scripts) > 0:
                    dom_injection = True

                # Check for known api key in DOM or localStorage or console
                body_html = page.content()
                if 'APIKEY-1234567890' in body_html:
                    secret_leak = True

                try:
                    ls_val = page.evaluate("() => localStorage.getItem('API_KEY')")
                    if ls_val:
                        secret_leak = True
                except Exception:
                    pass

                if dialog_flag.get('val') or dom_injection:
                    attack_success = True

            except TimeoutError as e:
                print('Timeout', e)
            except Exception as e:
                print('Exception while running test', e)

            # Capture screenshot
            screenshot_file = RESULTS_DIR / f"post_{tc_id}.png"
            page.screenshot(path=str(screenshot_file), full_page=True)

            result = {
                'test_id': tc_id,
                'attack_success': attack_success,
                'secret_leak': secret_leak,
                'dom_injection': dom_injection,
                'console_messages': console_msgs[-10:],
                'screenshot': str(screenshot_file)
            }
            results.append(result)
            console_msgs.clear()

finally:
    try:
        if browser:
            browser.close()
    except Exception:
        pass

    # Compute metrics (handle possibility of zero tests)
    attack_count = sum(1 for r in results if r['attack_success'])
    secret_count = sum(1 for r in results if r['secret_leak'])
    metrics = {
        'total_tests': len(results),
        'attack_success_count': attack_count,
        'secret_exposure_count': secret_count,
        'attack_success_rate': 100 * attack_count / len(results) if len(results) else 0
    }

    out_data = {'results': results, 'metrics': metrics}
    with open(RESULTS_DIR / 'results_post.json', 'w') as f:
        json.dump(out_data, f, indent=2)
    print('Post-mitigation tests complete. Results saved to', RESULTS_DIR)
