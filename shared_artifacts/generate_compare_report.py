import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
pre = ROOT / 'Project_A_PreMitigation_UI' / 'results' / 'results_pre.json'
post = ROOT / 'Project_B_PostMitigation_UI' / 'results' / 'results_post.json'
report = ROOT / 'compare_ui_security_report.md'

with open(pre, 'r') as f:
    rpre = json.load(f)
with open(post, 'r') as f:
    rpost = json.load(f)

# Helper: find tests by id
pre_map = {r['test_id']: r for r in rpre}
post_map = {r['test_id']: r for r in rpost}

# helper to fetch test with fallback
def get_test(m, tid):
    if tid in m:
        t = m[tid]
        t['missing'] = False
        return t
    return {'test_id': tid, 'pass': False, 'details': {}, 'duration_ms': 0, 'missing': True}

# Evaluate XSS tests: TC02_reflected_xss, TC03_dom_xss, TC05_malformed_edge
xss_tests = ['TC02_reflected_xss','TC03_dom_xss','TC05_malformed_edge']
pre_xss_success = 0
post_xss_success = 0
present_pre = 0
present_post = 0
missing_tests = []
for t in xss_tests:
    p = get_test(pre_map, t)
    q = get_test(post_map, t)
    if p.get('missing'):
        missing_tests.append(('pre', t))
    else:
        present_pre += 1
    if q.get('missing'):
        missing_tests.append(('post', t))
    else:
        present_post += 1
    pre_xss_success += (not p['pass'])
    post_xss_success += (not q['pass'])

# use count of canonical tests for percentage but indicate missing
count = len(xss_tests)
pre_rate = (pre_xss_success / count) * 100
post_rate = (post_xss_success / count) * 100
xss_reduction = max(0, pre_rate - post_rate)

# Secrets: TC04
secret_pre_t = get_test(pre_map, 'TC04_secrets_exposure')
secret_post_t = get_test(post_map, 'TC04_secrets_exposure')
secret_pre = secret_pre_t.get('details', {})
secret_post = secret_post_t.get('details', {})
secret_exposed_pre = False
secret_exposed_post = False
if not secret_pre_t.get('missing'):
    secret_exposed_pre = bool((secret_pre.get('dom_secret') and 'API_KEY' in secret_pre.get('dom_secret')) or secret_pre.get('window_secret'))
if not secret_post_t.get('missing'):
    secret_exposed_post = bool((secret_post.get('dom_secret') and 'API_KEY' in secret_post.get('dom_secret')) or secret_post.get('window_secret'))

secret_reduction = 100.0 if secret_exposed_pre and not secret_exposed_post else 0.0

# Security score: starting 100, subtract 40 for any XSS, subtract 60 for secret exposure.
def compute_score(xss_success_count, secret_exposed):
    score = 100
    score -= min(100, xss_success_count * 25)
    if secret_exposed:
        score -= 50
    return max(0, score)

score_pre = compute_score(pre_xss_success, secret_exposed_pre)
score_post = compute_score(post_xss_success, secret_exposed_post)

# Add warnings for missing tests
missing_pre = [t for (env,t) in missing_tests if env == 'pre']
missing_post = [t for (env,t) in missing_tests if env == 'post']

# Compose report
report_md = f"""# Compare UI Security Report

## Summary

- XSS exploit success (pre): {pre_rate:.1f}%
- XSS exploit success (post): {post_rate:.1f}%
- XSS reduction: {xss_reduction:.1f}%
- Secrets exposed (pre): {secret_exposed_pre}
- Secrets exposed (post): {secret_exposed_post}
- Secrets exposure reduction: {secret_reduction:.1f}%
- Security score (pre): {score_pre}
- Security score (post): {score_post}

"""

if missing_pre or missing_post:
    report_md += "\n## Warnings\n\n"
    if missing_pre:
        report_md += f"- Missing pre-mitigation tests: {missing_pre}\n"
    if missing_post:
        report_md += f"- Missing post-mitigation tests: {missing_post}\n"

report_md += "\n---\n\n## Detailed results\n\n"

backticks = "```"
report_md += "### Pre-mitigation results\n\n" + backticks + "\n" + json.dumps(rpre, indent=2) + "\n" + backticks + "\n\n"

report_md += "### Post-mitigation results\n\n" + backticks + "\n" + json.dumps(rpost, indent=2) + "\n" + backticks + "\n\n"

report_md += "## Conclusion\n\n- The patched UI should reduce XSS exploit rate to near 0% and mask or remove secrets in the DOM and console.\n- Recommendations: add CSP, sanitize inputs, avoid innerHTML, store secrets server-side, and perform CI regression tests.\n\n"

with open(report, 'w') as f:
    f.write(report_md)
print('Report written to', report)
