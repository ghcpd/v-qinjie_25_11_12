import json
from pathlib import Path

repo_root = Path(__file__).resolve().parent
pre_file = repo_root / 'Project_A_PreMitigation_UI' / 'results' / 'results_pre.json'
post_file = repo_root / 'Project_B_PostMitigation_UI' / 'results' / 'results_post.json'

if not pre_file.exists():
    print('No pre-mitigation results file found at', pre_file)
    pre_metrics = {'total_tests': 0, 'attack_success_rate': 0.0, 'attack_success_count': 0, 'secret_exposure_count': 0}
else:
    pre_results = json.loads(pre_file.read_text())
    pre_metrics = pre_results['metrics']

if not post_file.exists():
    print('No post-mitigation results file found at', post_file)
    post_metrics = {'total_tests': 0, 'attack_success_rate': 0.0, 'attack_success_count': 0, 'secret_exposure_count': 0}
else:
    post_results = json.loads(post_file.read_text())
    post_metrics = post_results['metrics']

# Compute comparisons
vulnerability_reduction = 100 * (pre_metrics['attack_success_rate'] - post_metrics['attack_success_rate']) / (pre_metrics['attack_success_rate'] if pre_metrics['attack_success_rate'] else 1)
secrets_reduction = 100 * (pre_metrics['secret_exposure_count'] - post_metrics['secret_exposure_count']) / (pre_metrics['secret_exposure_count'] if pre_metrics['secret_exposure_count'] else 1)

score_before = max(0, 100 - pre_metrics['attack_success_rate'] - (pre_metrics['secret_exposure_count'] * 10))
score_after = max(0, 100 - post_metrics['attack_success_rate'] - (post_metrics['secret_exposure_count'] * 10))

# Threshold checks
xss_reduction_threshold = 95.0
secrets_reduction_threshold = 100.0
xss_pass = vulnerability_reduction >= xss_reduction_threshold
secrets_pass = (pre_metrics['secret_exposure_count'] > 0 and (pre_metrics['secret_exposure_count'] - post_metrics['secret_exposure_count']) == pre_metrics['secret_exposure_count'])

md = []
md.append('# UI Security Comparison Report')
md.append('')
md.append('## Summary')
md.append(f"- Pre-mitigation attack success rate: {pre_metrics['attack_success_rate']:.2f}%")
md.append(f"- Post-mitigation attack success rate: {post_metrics['attack_success_rate']:.2f}%")
md.append(f"- Vulnerability occurrence reduction: {vulnerability_reduction:.2f}%")
md.append(f"- Secrets exposure reduction: {secrets_reduction:.2f}%")
md.append('')
md.append('## Details')
md.append('')
md.append('### Pre-mitigation metrics')
md.append('')
md.append('```json')
md.append(json.dumps(pre_metrics, indent=2))
md.append('```')
md.append('')
md.append('### Post-mitigation metrics')
md.append('')
md.append('```json')
md.append(json.dumps(post_metrics, indent=2))
md.append('```')
md.append('')
md.append('## Recommendations')
md.append('- Sanitize inputs both server-side and client-side.')
md.append('- Use CSP headers to block inline scripts.')
md.append('- Avoid storing secrets in DOM/localStorage and avoid logging secrets to console.')
md.append('')
md.append('## Screenshots & Artifacts')
md.append('- See Project_A_PreMitigation_UI/results and Project_B_PostMitigation_UI/results')
md.append('## Threshold Evaluation')
md.append('')
md.append(f"- XSS success rate reduction >= {xss_reduction_threshold}%: {'PASS' if xss_pass else 'FAIL'}")
md.append(f"- Secrets exposure completely removed: {'PASS' if secrets_pass else 'FAIL'}")
md.append('')
md.append('### Security Scores')
md.append('')
md.append(f"- Security score before: {score_before}")
md.append(f"- Security score after: {score_after}")

out_file = repo_root / 'compare_ui_security_report.md'
out_file.write_text('\n'.join(md))
print('Report written to', out_file)
