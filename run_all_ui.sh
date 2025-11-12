#!/usr/bin/env bash
set -e
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "Running Pre-Mitigation tests..."
cd "$ROOT_DIR/Project_A_PreMitigation_UI"
./run_ui_tests.sh

echo "Running Post-Mitigation tests..."
cd "$ROOT_DIR/Project_B_PostMitigation_UI"
./run_ui_tests.sh

# Aggregate results
cd "$ROOT_DIR"
python - <<'PY'
import json, os
root = os.path.abspath('.')
pre = os.path.join(root, 'Project_A_PreMitigation_UI', 'results_pre.json')
post = os.path.join(root, 'Project_B_PostMitigation_UI', 'results_post.json')

if not os.path.exists(pre) or not os.path.exists(post):
    print('Missing results files. Run both tests to generate results_pre.json and results_post.json')
    raise SystemExit(1)

with open(pre) as f:
    pre_r = json.load(f)
with open(post) as f:
    post_r = json.load(f)

report = {
    'pre_summary': pre_r['summary'],
    'post_summary': post_r['summary'],
}

# Compute deltas
report['changes'] = {
    'xss_success_pct_drop': pre_r['summary']['xss_success_pct'] - post_r['summary']['xss_success_pct'],
    'secrets_exposed_pct_drop': pre_r['summary']['secrets_exposed_pct'] - post_r['summary']['secrets_exposed_pct'],
    'security_score_gain': post_r['summary']['security_score'] - pre_r['summary']['security_score']
}

md = []
md.append('# UI Security Comparison Report')
md.append('\n## Metrics (Pre vs Post)')
md.append('| Metric | Pre | Post | Delta |')
md.append('|---|---:|---:|---:|')
md.append(f"| XSS success % | {pre_r['summary']['xss_success_pct']:.2f} | {post_r['summary']['xss_success_pct']:.2f} | {report['changes']['xss_success_pct_drop']:.2f} |")
md.append(f"| Secrets exposure % | {pre_r['summary']['secrets_exposed_pct']:.2f} | {post_r['summary']['secrets_exposed_pct']:.2f} | {report['changes']['secrets_exposed_pct_drop']:.2f} |")
md.append(f"| Security score | {pre_r['summary']['security_score']} | {post_r['summary']['security_score']} | {report['changes']['security_score_gain']:+d} |")

md.append('\n## Summary')
md.append('Security improvements were measured across the provided test payloads and environments. The patched UI aims to reduce XSS and secrets exposure via input sanitization, CSP, and safe DOM updates.')

with open(os.path.join(root, 'compare_ui_security_report.md'), 'w') as fh:
    fh.write('\n'.join(md))

print('Comparison report written to compare_ui_security_report.md')
PY

echo "All runs complete. See compare_ui_security_report.md for final metrics." 
