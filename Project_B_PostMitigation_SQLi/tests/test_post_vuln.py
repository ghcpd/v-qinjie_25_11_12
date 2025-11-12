import json
import subprocess
import time
import requests
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
LOGS = ROOT / 'logs'
RESULTS = ROOT / 'results'
TEST_DATA = ROOT.parent / 'test_data.json'

LOGS.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)


def load_json_file(path):
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'gbk', 'latin-1']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                return json.load(f)
        except Exception:
            pass
    raise UnicodeDecodeError('utf-8', b'', 0, 1, 'Unable to decode file using tried encodings')


SERVER_CMD = ['python', '-m', 'src.app']
BASE_URL = 'http://127.0.0.1:5002'


def start_server():
    # start server
    return subprocess.Popen(SERVER_CMD, cwd=ROOT)


def wait_for_server(timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(BASE_URL + '/search')
            if r.status_code in (200, 400, 404):
                return True
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError('Server did not start in time')


def run_test_case(test_case):
    payload = test_case['input_payload']
    expected = test_case['expected_behavior']
    result = {
        'test_id': test_case['test_id'],
        'input_payload': payload,
        'attack_succeeded': False,
        'latency_ms': None,
        'resp': None,
        'evidence': []
    }
    endpoint = payload.pop('endpoint', '/search')
    params = payload.get('params', {})
    url = BASE_URL + endpoint
    t0 = time.time()
    try:
        r = requests.get(url, params=params, timeout=10)
        latency = (time.time()-t0)*1000
        result['latency_ms'] = latency
        result['resp'] = r.json() if 'application/json' in r.headers.get('Content-Type','') else r.text
        # Patch expectations: test should pass if no injection possible
        # Check logs for evidence of unsafe raw SQL logging (should NOT exist)
        try:
            logs_text = open(ROOT / 'logs' / 'server.log','r',encoding='utf-8').read()
            if 'RAW_SQL' in logs_text or 'RAW_AUTH_SQL' in logs_text:
                result['attack_succeeded'] = True
                result['evidence'].append('raw_sql_in_logs')
        except Exception:
            pass
        if expected.get('inject_expectation') == 'stored_data_leak':
            # No extra rows should be returned for injection attempts
            data = result['resp']
            if isinstance(data, dict) and 'results' in data:
                if len(data['results']) > 1:
                    result['attack_succeeded'] = True
                    result['evidence'].append('multiple_rows_returned')
                else:
                    result['attack_succeeded'] = False
            else:
                result['passes'] = True
        elif expected.get('inject_expectation') == 'auth_bypass':
            if isinstance(result['resp'], dict) and result['resp'].get('auth') == 'ok':
                result['attack_succeeded'] = True
                result['evidence'].append('auth_bypassed')
            else:
                result['attack_succeeded'] = False
        elif expected.get('inject_expectation') == 'no_injection':
            if isinstance(result['resp'], dict) and 'error' in result['resp']:
                result['attack_succeeded'] = True
                result['evidence'].append('error_leaked')
            else:
                result['attack_succeeded'] = False
        elif expected.get('inject_expectation') == 'timedelay':
            if latency > (expected.get('threshold_ms', 2000)):
                result['attack_succeeded'] = True
                result['evidence'].append('timedelay_detected')
            else:
                result['attack_succeeded'] = False
        else:
            result['passes'] = True
    except Exception as e:
        result['attack_succeeded'] = True
        result['evidence'].append(str(e))
    return result


def run_all_tests():
    tests = load_json_file(TEST_DATA)
    p = start_server()
    try:
        wait_for_server(5)
        res = []
        for t in tests:
            r = run_test_case(t)
            res.append(r)
            print(f"Test {t['test_id']}: attack_succeeded={r['attack_succeeded']}, latency={r['latency_ms']:.2f}ms, evidence={r['evidence']}")
        with open(RESULTS / 'results_post.json', 'w') as out:
            json.dump(res, out, indent=2)
    finally:
        p.terminate()


if __name__ == '__main__':
    run_all_tests()
