import json
import os
import time
import subprocess
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT.parent / 'shared_artifacts' / 'test_ui_vuln.json'

with open(SHARED, 'r', encoding='utf-8') as f:
    TESTS = json.load(f)

RESULTS_FILE = ROOT / 'results' / 'results_pre.json'
RESULTS_FILE.parent.mkdir(exist_ok=True)

SERVER_CMD = ['python', 'src/app.py']

server_process = None

def start_server():
    global server_process
    server_process = subprocess.Popen(SERVER_CMD, cwd=str(ROOT))
    # wait for server port to open
    import socket
    deadline = time.time() + 5.0
    while time.time() < deadline:
        try:
            s = socket.create_connection(('127.0.0.1', 8000), timeout=0.5)
            s.close()
            break
        except OSError:
            time.sleep(0.1)


def stop_server():
    global server_process
    if server_process:
        server_process.terminate()
        server_process.wait()


def run_tests(repeat=1,browser_name='chromium',viewport='1024x768'):
    results = []
    import argparse

    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=True)
        w,h = list(map(int,viewport.split('x')))
        context = browser.new_context(viewport={"width":w,"height":h})

        page = context.new_page()

        for _ in range(repeat):
            for t in TESTS:
                test_id = t['test_id']
                res = {'test_id': test_id, 'pass': False, 'details': {}, 'duration_ms': None}
                start = time.time()
                # capture console messages per test
                console_entries = []
                page.on('console', lambda msg: console_entries.append(msg.text))
                try:
                if test_id == 'TC01_normal_input' or test_id == 'TC02_reflected_xss' or test_id == 'TC05_malformed_edge':
                    page.goto('http://127.0.0.1:8000')
                    # submit comment
                    page.fill('#commentInput', t['input_payload'].get('comment', ''))
                    # watch for dialogs
                    dialog_seen = {'ok': False}
                    def on_dialog(dialog):
                        dialog_seen['ok'] = True
                        dialog.dismiss()
                    page.on('dialog', on_dialog)
                    page.click('text=Submit')
                    page.wait_for_selector('#comments .comment')

                    # verify if innerHTML contains <script>
                    comments_html = page.inner_html('#comments')
                    res['details']['html'] = comments_html
                    # define pass: no dialog, content does not execute script
                    res['pass'] = (not dialog_seen['ok'])
                    if test_id == 'TC05_malformed_edge':
                        res['details']['len'] = len(page.inner_text('#comments'))

                    # if test failed then screenshot
                    if not res['pass']:
                        screenshot_path = ROOT / 'results' / f"{test_id}.png"
                        page.screenshot(path=str(screenshot_path))
                        res['details']['screenshot'] = str(screenshot_path)

                elif test_id == 'TC03_dom_xss':
                    payload = t['input_payload']['hash']
                    page.goto('http://127.0.0.1:8000/hash#' + payload)
                    # check for dialog
                    dialog_seen = {'ok': False}
                    page.on('dialog', lambda d: dialog_seen.update({'ok': True}) or d.dismiss())
                    time.sleep(0.6)
                    html = page.inner_html('#hashArea')
                    res['details']['html'] = html
                    res['pass'] = (not dialog_seen['ok'])

                elif test_id == 'TC04_secrets_exposure':
                    page.goto('http://127.0.0.1:8000')
                    time.sleep(0.2)
                    # check DOM secret
                    dom_secret = page.inner_text('#api-key')
                    # read window variable
                    try:
                        window_secret = page.evaluate('window.PUBLIC_API_KEY')
                    except Exception:
                        window_secret = None
                    # check console logs for secret
                    secret_in_console = any('PUBLIC KEY' in c or 'API_KEY' in c or 'APIKEY' in c for c in console_entries)

                    res['details'] = {'dom_secret': dom_secret, 'window_secret': window_secret, 'secret_in_console': secret_in_console, 'console_entries': console_entries}
                    res['pass'] = (dom_secret == '' or dom_secret is None) or not window_secret
                    if not res['pass']:
                        screenshot_path = ROOT / 'results' / f"{test_id}.png"
                        page.screenshot(path=str(screenshot_path))
                        res['details']['screenshot'] = str(screenshot_path)

            except Exception as e:
                res['details']['error'] = str(e)
                res['pass'] = False
            finally:
                res['duration_ms'] = int((time.time() - start) * 1000)
                results.append(res)

        browser.close()

    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--browser', choices=['chromium','firefox','webkit'], default='chromium')
    parser.add_argument('--viewport', default='1024x768')
    args = parser.parse_args()

    try:
        start_server()
        run_tests(repeat=args.repeat, browser_name=args.browser, viewport=args.viewport)
    finally:
        stop_server()

if __name__ == '__main__':
    main()
