import json
import os

ROOT = os.path.abspath(os.path.dirname(__file__))
A_RESULTS = os.path.join(ROOT, 'Project_A_PreMitigation_SQLi', 'results', 'results_pre.json')
B_RESULTS = os.path.join(ROOT, 'Project_B_PostMitigation_SQLi', 'results', 'results_post.json')
OUT = os.path.join(ROOT, 'compare_report.md')

with open(A_RESULTS) as f:
    a = json.load(f)
with open(B_RESULTS) as f:
    b = json.load(f)

am = a.get('metrics', {})
bm = b.get('metrics', {})

attack_reduction = None
if am and bm:
    attack_reduction = round((am['attack_success_rate'] - bm['attack_success_rate']), 2)

latency_impact = None
if am and bm:
    try:
        latency_impact = round(((bm['avg_latency'] - am['avg_latency']) / am['avg_latency']) * 100, 2)
    except Exception:
        latency_impact = None

sec_score_a = am.get('security_score', round(100 - am['attack_success_rate'], 2)) if am else 0
sec_score_b = bm.get('security_score', round(100 - bm['attack_success_rate'], 2)) if bm else 0

leak_count_a = am.get('leakage_count', 0) if am else 0
leak_count_b = bm.get('leakage_count', 0) if bm else 0

with open(OUT, 'w') as f:
    f.write('# Compare Report: Pre vs Post Mitigation\n\n')
    f.write('## Summary\n')
    f.write(f'- Attack Success Rate (pre): {am.get("attack_success_rate", "N/A")} %\n')
    f.write(f'- Attack Success Rate (post): {bm.get("attack_success_rate", "N/A")} %\n')
    f.write(f'- Attack Success Rate Reduction: {attack_reduction} %\n')
    f.write(f'- Average Latency (pre): {am.get("avg_latency", "N/A")} s\n')
    f.write(f'- Average Latency (post): {bm.get("avg_latency", "N/A")} s\n')
    f.write(f'- Latency Impact (relative): {latency_impact} %\n')
    f.write(f'- Security Score (0-100) pre: {sec_score_a}\n')
    f.write(f'- Security Score (0-100) post: {sec_score_b}\n')
    f.write(f'- Leakage counts: pre={leak_count_a}, post={leak_count_b} \n\n')

    # Pass/Fail checks
    f.write('## Acceptance Criteria Checks\n')
    success_reduction_pass = attack_reduction >= 95 if attack_reduction is not None else False
    latency_ok = latency_impact is None or abs(latency_impact) <= 10
    no_error_leaks = (leak_count_b == 0)
    f.write(f'- SQLi success rate ↓ ≥ 95%: {success_reduction_pass}\n')
    f.write(f'- Average latency increase ≤ 10%: {latency_ok} (impact: {latency_impact} %)\n')
    f.write(f'- No exposed errors in logs (post): {no_error_leaks}\n\n')

    f.write('## Per-test results (pre)\n')
    for r in a['results']:
        f.write(f"- {r['test_id']}: sqli_detected={r.get('sqli_detected')}, latency={r.get('latency')}\n")

    f.write('\n## Per-test results (post)\n')
    for r in b['results']:
        f.write(f"- {r['test_id']}: sqli_detected={r.get('sqli_detected')}, latency={r.get('latency')}\n")

    f.write('\n## Recommendations\n')
    f.write('- Ensure parameterized queries are used for **all** DB paths.\n')
    f.write('- Add continuous scanning and WAF for production traffic.\n')
    f.write('- Add more payloads and edge cases to the test set.\n')

print('Compare report generated at', OUT)
