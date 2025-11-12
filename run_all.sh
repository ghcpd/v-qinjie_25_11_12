#!/usr/bin/env bash
set -e
ROOT=$(pwd)

# Run Project A Pre-mitigation
cd Project_A_PreMitigation_SQLi
if [ ! -d .venv ]; then
    bash setup.sh
fi
bash run_tests.sh
cd ..

# Run Project B Post-mitigation
cd Project_B_PostMitigation_SQLi
if [ ! -d .venv ]; then
    bash setup.sh
fi
bash run_tests.sh
cd ..

# Compare results
python - <<'PY'
import json
from pathlib import Path
root = Path('.')
resA = root / 'Project_A_PreMitigation_SQLi' / 'results' / 'results_pre.json'
resB = root / 'Project_B_PostMitigation_SQLi' / 'results' / 'results_post.json'
if not resA.exists() or not resB.exists():
    print('Missing result files, cannot compare')
    raise SystemExit(1)
pre = json.loads(resA.read_text())
post = json.loads(resB.read_text())

# Map results by test_id
pre_map = {r['test_id']: r for r in pre}
post_map = {r['test_id']: r for r in post}

# compute metrics

def compute_metrics(rmap):
    total = len(rmap)
    injection_tests = [r for r in rmap.values() if r['test_id'] != 'normal_query']
    success_count = 0
    total_latency = 0
    for r in rmap.values():
        total_latency += (r['latency_ms'] or 0)
    for r in injection_tests:
        if r.get('attack_succeeded'):
            success_count += 1
    attack_success_rate = (success_count/len(injection_tests))*100 if injection_tests else 0
    avg_latency = total_latency/total
    return {
        'attack_success_rate': attack_success_rate,
        'avg_latency': avg_latency,
        'total_tests': total,
        'injection_tests': len(injection_tests)
    }

metrics_pre = compute_metrics(pre_map)
metrics_post = compute_metrics(post_map)

improvement = metrics_pre['attack_success_rate'] - metrics_post['attack_success_rate']
latency_change = metrics_post['avg_latency'] - metrics_pre['avg_latency']
latency_pct_change = ((metrics_post['avg_latency'] - metrics_pre['avg_latency'])/metrics_pre['avg_latency']*100) if metrics_pre['avg_latency'] else 0

# Compute security score 0-100 (naive): 100 minus attack success rate and minus latency penalty above 10%

def security_score(attack_rate, latency_pct):
    score = 100 - attack_rate
    if latency_pct > 10:
        score -= (latency_pct - 10)
    return max(0, score)

score_pre = security_score(metrics_pre['attack_success_rate'], 0)
score_post = security_score(metrics_post['attack_success_rate'], latency_pct_change)

analysis = {
    'pre_attack_success': metrics_pre['attack_success_rate'],
    'post_attack_success': metrics_post['attack_success_rate'],
    'reduction_pct': improvement,
    'pre_avg_latency': metrics_pre['avg_latency'],
    'post_avg_latency': metrics_post['avg_latency'],
    'latency_change_ms': latency_change,
    'latency_pct_change': latency_pct_change,
    'score_pre': score_pre,
    'score_post': score_post
}

report = f"""# Compare Report

| Metric | Pre-mitigation | Post-mitigation | Change |
|---|---:|---:|---:|
| Attack success rate | {analysis['pre_attack_success']:.2f}% | {analysis['post_attack_success']:.2f}% | {analysis['reduction_pct']:.2f}% |
| Average latency (ms) | {analysis['pre_avg_latency']:.2f} | {analysis['post_avg_latency']:.2f} | {analysis['latency_change_ms']:.2f} ms ({analysis['latency_pct_change']:.2f}%) |
| Security Score (0-100) | {analysis['score_pre']:.2f} | {analysis['score_post']:.2f} | {(analysis['score_post']-analysis['score_pre']):+.2f} |

## Thresholds
- Required: Attack success rate reduction >= 95%: {analysis['reduction_pct'] >= 95}
- Required: Average latency increase <= 10%: {analysis['latency_pct_change'] <= 10}

Detailed JSON results are available in Project_A_PreMitigation_SQLi/results and Project_B_PostMitigation_SQLi/results

"""

(root / 'compare_report.md').write_text(report)
(root / 'compare_report.json').write_text(json.dumps(analysis, indent=2))
print('Compare report generated at compare_report.md and compare_report.json')
PY

echo "Done. Results and logs are saved under Project_*_*/artifacts and .*/results."