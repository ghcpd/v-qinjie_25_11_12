#!/usr/bin/env bash
set -e
ROOT=$(pwd)
# Run pre-mitigation
cd "${ROOT}/Project_A_PreMitigation_SQLi"
./run_tests.sh --repeat 1
cd "${ROOT}/Project_B_PostMitigation_SQLi"
./run_tests.sh --repeat 1
# Generate compare report
python - <<'PY'
import json, pathlib
root=pathlib.Path('.').resolve()
pre=json.loads((root/'Project_A_PreMitigation_SQLi'/'results'/'results_pre.json').read_text())
post=json.loads((root/'Project_B_PostMitigation_SQLi'/'results'/'results_post.json').read_text())
# fetch metrics
pa = pre.get('metrics', {})
pb = post.get('metrics', {})
# security score (naive): 100 - preSuccess% + (preLatency - postLatency)% penalty
score_pre = max(0, 100 - pa['success_rate'])
latency_penalty = max(0, (pb['avg_latency'] - pa['avg_latency'])/max(0.001, pa['avg_latency']) * 100)
score_post = max(0, score_pre - latency_penalty)
report=f"""# Comparison Report

|Metric|Pre-Mitigation|Post-Mitigation|Delta|
|---|---:|---:|---:|
|Attack success %|{pa['success_rate']:.2f}|{pb['success_rate']:.2f}|{pa['success_rate']-pb['success_rate']:.2f}|
|Average Latency (s)|{pa['avg_latency']:.3f}|{pb['avg_latency']:.3f}|{pb['avg_latency']-pa['avg_latency']:.3f}|
|Leaks (count)|{pa['leaks']}|{pb['leaks']}|{pa['leaks']-pb['leaks']}|

**Security score (0-100)**
- Pre: {score_pre:.1f}
- Post: {score_post:.1f}
"""
(root/'compare_report.md').write_text(report)
print(report)
PY
