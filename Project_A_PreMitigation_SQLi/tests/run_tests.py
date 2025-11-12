import json
import subprocess
import time
import requests
import os
import argparse
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DATA = Path(ROOT.parent, 'shared', 'test_data.json')
LOGS = Path(ROOT, 'logs')
RESULTS = Path(ROOT, 'results')
LOGS.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)


def start_server():
    # Start app via subprocess, capture logs
    out = open(LOGS / 'server_out.log', 'w')
    err = open(LOGS / 'server_err.log', 'w')
    cmd = [sys.executable, str(ROOT / 'src' / 'app.py')]
    proc = subprocess.Popen(cmd, stdout=out, stderr=err)
    # wait for server to start
    for i in range(20):
        try:
            r = requests.get('http://127.0.0.1:5001/')
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    return proc


def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


def load_tests():
    with open(TEST_DATA, 'r') as f:
        return json.load(f)['tests']


def run_test_case(case):
    base = 'http://127.0.0.1:5001'
    start = time.time()
    resp = requests.get(base + case['endpoint'], timeout=15)
    elapsed = (time.time() - start)
    data = None
    leak = False
    try:
        data = resp.json()
    except Exception:
        data = {'_raw': resp.text}
    # detect simple injection success
    success = False
    if case['test_id'] == 'login_basic':
        success = data.get('status') == 'ok'
    else:
        # if we get more than 1 row for something that should return at most 1
        if isinstance(data, list) and len(data) > 1:
            success = True
            leak = any('secret' in row for row in data)
    # detect slow (blind) injection - if elapsed > expected threshold
    if 'sleep(' in case['input_payload'] and elapsed > case.get('expected_behavior', {}).get('max_latency', 2):
        success = True
    return {'test_id': case['test_id'], 'elapsed': elapsed, 'success': success, 'leak': leak, 'status_code': resp.status_code}


def run_all(repeats=1):
    proc = start_server()
    tests = load_tests()
    results = []
    for _ in range(repeats):
        for t in tests:
            res = run_test_case(t)
            results.append(res)
    stop_server(proc)
    out_file = RESULTS / 'results_pre.json'
    # aggregated metrics
    total = len(results)
    success = sum(1 for r in results if r['success'])
    avg_latency = sum(r['elapsed'] for r in results)/max(1,total)
    logfile = LOGS / 'raw_queries.log'
    evidence = []
    if logfile.exists():
        with open(logfile, 'r') as f:
            content = f.read()
            if 'sleep(' in content:
                evidence.append('time_based_sqli')
            if 'OR' in content.upper() or "--" in content:
                evidence.append('structure_based_sqli')
            if 'secret_alice' in content or 'secret_bob' in content:
                evidence.append('data_leak')

    metrics = {'attack_success_rate': success/total*100, 'avg_latency': avg_latency, 'leaks': sum(1 for r in results if r['leak']), 'evidence': evidence}
    with open(out_file, 'w') as f:
        json.dump({'results': results, 'metrics': metrics}, f, indent=2)
    print('Results written to', out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeat', type=int, default=1)
    args = parser.parse_args()
    run_all(args.repeat)
