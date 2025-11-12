import json
import os
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT.parent / 'shared_artifacts' / 'test_ui_vuln.json'

with open(SHARED, 'r', encoding='utf-8') as f:
    TESTS = json.load(f)

RESULTS_FILE = ROOT / 'results' / 'results_post.json'
RESULTS_FILE.parent.mkdir(exist_ok=True)

SERVER_CMD = ['python', 'src/app.py']
server_process = None

import subprocess, time

def start_server():
    global server_process
    server_process = subprocess.Popen(SERVER_CMD, cwd=str(ROOT))
    # wait for server port to open
    import socket
    deadline = time.time() + 5.0
    while time.time() < deadline:
        try:
            s = socket.create_connection(('127.0.0.1', 8001), timeout=0.5)
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
    with sync_playwright() as p:
        browser = getattr(p,(browser_name)).launch(headless=True)
        w,h = list(map(int,viewport.split('x')))
        context = browser.new_context(viewport={"width":w,"height":h})
        context.set_default_navigation_timeout(5000)

        page = context.new_page()

        for _ in range(repeat):
            for t in TESTS:
                test_id = t['test_id']
                res = {'test_id': test_id, 'pass': False, 'details': {}, 'duration_ms': None}
                start = time.time()
            console_entries = []
            page.on('console', lambda msg: console_entries.append(msg.text))
            if test_id in ['TC01_normal_input','TC02_reflected_xss','TC05_malformed_edge']:
                page.goto('http://127.0.0.1:8001')
                page.fill('#commentInput', t['input_payload'].get('comment', ''))
                dialog_seen = {'ok': False}
                page.on('dialog', lambda d: dialog_seen.update({'ok':True}) or d.dismiss())
                page.click('text=Submit')
                page.wait_for_selector('#comments .comment')
                comments_html = page.inner_html('#comments')
                res['details']['html'] = comments_html
                res['pass'] = (not dialog_seen['ok'])
                if not res['pass']:
                    s = ROOT / 'results' / f"{test_id}.png"
                    page.screenshot(path=str(s))
                    res['details']['screenshot'] = str(s)

            elif test_id == 'TC03_dom_xss':
                payload = t['input_payload']['hash']
                page.goto('http://127.0.0.1:8001/hash#' + payload)
                dialog_seen = {'ok': False}
                page.on('dialog', lambda d: dialog_seen.update({'ok':True}) or d.dismiss())
                time.sleep(0.6)
                html = page.inner_html('#hashArea')
                res['details']['html'] = html
                # ensures that no '<img' present
                res['pass'] = ('<' not in html) and (not dialog_seen['ok'])

            elif test_id == 'TC04_secrets_exposure':
                page.goto('http://127.0.0.1:8001')
                dom_secret = page.inner_text('#api-key')
                try:
                    window_secret = page.evaluate('window.PUBLIC_API_KEY')
                except Exception:
                    window_secret = None
                # ensure CSP header also set
                resp = context.request.get('http://127.0.0.1:8001')
                csp_header = resp.headers.get('content-security-policy', '')
                res['details'] = {'dom_secret': dom_secret, 'window_secret': window_secret, 'console_entries': console_entries, 'csp': csp_header}
                res['pass'] = (dom_secret == '*******') and (window_secret is None) and ('default-src' in csp_header)
                if not res['pass']:
                    s = ROOT / 'results' / f"{test_id}.png"
                    page.screenshot(path=str(s))
                    res['details']['screenshot'] = str(s)

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
