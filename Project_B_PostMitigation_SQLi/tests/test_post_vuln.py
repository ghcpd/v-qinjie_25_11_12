import os
import subprocess
import json
from pathlib import Path

def test_run_post_mitigation():
    root = Path(__file__).resolve().parents[1]
    subprocess.call(['python', 'src/db_setup.py'])
    subprocess.call(['python', 'tests/run_tests.py'])
    res = json.loads((root/'results'/'results_post.json').read_text())
    # Expect no successful attacks in patched environment
    assert sum(1 for e in res['results'] if e['success']) == 0
    # Expect no data leaks
    assert res.get('metrics', {}).get('leaks', 0) == 0
