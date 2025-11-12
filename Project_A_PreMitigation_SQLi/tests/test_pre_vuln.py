import subprocess
import requests
import time
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_FILE = os.path.join(ROOT, 'test_data.json')
RESULTS_DIR = os.path.join(PROJECT_DIR, 'results')
LOG_FILE = os.path.join(PROJECT_DIR, 'logs', 'sql.log')
DB_SETUP = os.path.join(PROJECT_DIR, 'setup_db.py')

os.makedirs(RESULTS_DIR, exist_ok=True)

with open(DATA_FILE) as f:
    tests = json.load(f)

SERVER_CMD = [sys.executable, '-m', 'src.app']

p = None
try:
    # Setup DB
    subprocess.check_call([sys.executable, DB_SETUP])

    # Start server (run module in project dir so relative imports work)
    p = subprocess.Popen(SERVER_CMD, cwd=PROJECT_DIR)

    # Wait for server to be ready
    base = 'http://127.0.0.1:5000'
    for _ in range(30):
        try:
            r = requests.get(base + '/health', timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)

    results = []
    success_count = 0
    total_latency = 0.0

    repeat = int(os.environ.get('REPEAT', '1'))
    for t in tests:
        payload = t['input_payload']
        params = {'query': payload}
        test_success = 0
        test_latency = 0.0
        test_leak = 0
        results_count = 0
        body = {}
        r = None

        for _ in range(repeat):
            start = time.time()
            try:
                r = requests.get(base + '/search', params=params, timeout=20)
                latency = time.time() - start
                total_latency += latency
                test_latency += latency
                body = r.json() if r.text else {}

                leak_flag = False
                if r.status_code == 500 and 'error' in body:
                    # check for 'sqlite' or exception text
                    if 'sqlite' in body.get('error', '').lower() or 'traceback' in body.get('error', '').lower():
                        leak_flag = True

                if leak_flag:
                    test_leak += 1

                results_count = len(body.get('results', [])) if isinstance(body.get('results', []), list) else 0

                # detection heuristics for SQLi
                s = False
                if t['test_id'] in ('basic_injection', 'encoded_injection'):
                    # if admin present or unexpectedly many results
                    admin_present = any(r.get('username', '').lower() == 'admin' for r in body.get('results', []) if isinstance(r, dict))
                    if admin_present or results_count > 2:
                        s = True
                elif t['test_id'] == 'blind_injection':
                    if latency >= 3.5:  # sleep 4s expected
                        s = True
                elif t['test_id'] == 'malformed_input':
                    if leak_flag:
                        s = True  # indicates vulnerability caused leakage
                    else:
                        s = False
                else:
                    # normal query - expect <=2 matches
                    if results_count >= 1:
                        s = False

                if s:
                    test_success += 1

            except Exception as e:
                results.append({
                    'test_id': t['test_id'],
                    'error': str(e),
                    'latency': time.time() - start,
                })

        avg_latency = test_latency / repeat if repeat else 0
        results.append({
            'test_id': t['test_id'],
            'status_code': r.status_code if 'r' in locals() else 0,
            'latency': avg_latency,
            'results_count': results_count,
            'leak_flag': bool(test_leak),
            'sqli_detected': test_success > 0,
            'response_body': body
        })

        if test_success > 0:
            success_count += 1

    metrics = {
        'total_tests': len(tests),
        'attack_success_count': success_count,
        'attack_success_rate': round(success_count / len(tests) * 100, 2),
        'avg_latency': round(total_latency / len(tests), 3)
    }

    # Security score: simple metric 0-100
    metrics['security_score'] = round(100 - metrics['attack_success_rate'], 2)

    # Leakage count: how many tests exposed potential errors
    leakage_count = sum(1 for r in results if r.get('leak_flag'))
    metrics['leakage_count'] = leakage_count

    output = {'results': results, 'metrics': metrics}
    with open(os.path.join(RESULTS_DIR, 'results_pre.json'), 'w') as f:
        json.dump(output, f, indent=2)

    # Copy log if present
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as lf:
            logs = lf.read()
        with open(os.path.join(RESULTS_DIR, 'sql.log'), 'w') as outl:
            outl.write(logs)

finally:
    if p:
        p.terminate()
        p.wait()
