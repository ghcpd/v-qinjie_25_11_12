import os
import subprocess
import json
from pathlib import Path

def test_run_pre_mitigation():
    root = Path(__file__).resolve().parents[1]
    subprocess.call(['python', 'src/db_setup.py'])
    subprocess.call(['python', 'tests/run_tests.py'])
    res = json.loads((root/'results'/'results_pre.json').read_text())
    # Expect at least one test to mark success in pre-mitigation
    assert any(e['success'] for e in res['results'])
    # Expect evidence of SQLi in logs
    assert 'structure_based_sqli' in res.get('metrics', {}).get('evidence', []) or res.get('metrics', {}).get('leaks', 0) > 0
