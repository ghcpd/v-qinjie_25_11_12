"""
Generate comparison report between pre-mitigation and post-mitigation test results
"""

import json
from pathlib import Path
from datetime import datetime

PRE_RESULTS_PATH = Path("Project_A_PreMitigation_UI/results/results_pre.json")
POST_RESULTS_PATH = Path("Project_B_PostMitigation_UI/results/results_post.json")
OUTPUT_PATH = Path("compare_ui_security_report.md")

def load_results(file_path):
    """Load test results from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
        return None

def calculate_improvements(pre_metrics, post_metrics):
    """Calculate improvement percentages"""
    improvements = {}
    
    if pre_metrics and post_metrics:
        # XSS success rate reduction
        pre_xss = pre_metrics.get('xss_attack_success_rate', 0)
        post_xss = post_metrics.get('xss_attack_success_rate', 0)
        xss_reduction = pre_xss - post_xss
        xss_reduction_pct = (xss_reduction / pre_xss * 100) if pre_xss > 0 else 0
        improvements['xss_reduction'] = {
            'pre': pre_xss,
            'post': post_xss,
            'reduction': xss_reduction,
            'reduction_pct': xss_reduction_pct
        }
        
        # Secrets exposure reduction
        pre_secrets = pre_metrics.get('secrets_exposure_rate', 0)
        post_secrets = post_metrics.get('secrets_exposure_rate', 0)
        secrets_reduction = pre_secrets - post_secrets
        secrets_reduction_pct = (secrets_reduction / pre_secrets * 100) if pre_secrets > 0 else 0
        improvements['secrets_reduction'] = {
            'pre': pre_secrets,
            'post': post_secrets,
            'reduction': secrets_reduction,
            'reduction_pct': secrets_reduction_pct
        }
        
        # Security score improvement
        pre_score = pre_metrics.get('security_score', 0)
        post_score = post_metrics.get('security_score', 0)
        score_improvement = post_score - pre_score
        improvements['security_score'] = {
            'pre': pre_score,
            'post': post_score,
            'improvement': score_improvement
        }
        
        # CSP coverage (post-mitigation only)
        post_csp = post_metrics.get('csp_coverage', 0)
        improvements['csp_coverage'] = post_csp
    
    return improvements

def generate_report(pre_results, post_results):
    """Generate markdown comparison report"""
    report = []
    
    report.append("# UI Security Evaluation - Comparison Report")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("---")
    report.append("")
    
    # Executive Summary
    report.append("## Executive Summary")
    report.append("")
    
    if pre_results and post_results:
        pre_metrics = pre_results.get('metrics', {})
        post_metrics = post_results.get('metrics', {})
        improvements = calculate_improvements(pre_metrics, post_metrics)
        
        report.append("This report compares the security posture of the application before and after implementing security mitigations.")
        report.append("")
        report.append("### Key Findings")
        report.append("")
        
        if improvements:
            xss_improvement = improvements.get('xss_reduction', {})
            secrets_improvement = improvements.get('secrets_reduction', {})
            score_improvement = improvements.get('security_score', {})
            
            report.append(f"- **XSS Attack Success Rate**: Reduced from {xss_improvement.get('pre', 0):.2f}% to {xss_improvement.get('post', 0):.2f}% ({xss_improvement.get('reduction_pct', 0):.2f}% reduction)")
            report.append(f"- **Secrets Exposure Rate**: Reduced from {secrets_improvement.get('pre', 0):.2f}% to {secrets_improvement.get('post', 0):.2f}% ({secrets_improvement.get('reduction_pct', 0):.2f}% reduction)")
            report.append(f"- **Security Score**: Improved from {score_improvement.get('pre', 0):.2f}/100 to {score_improvement.get('post', 0):.2f}/100 (+{score_improvement.get('improvement', 0):.2f} points)")
            
            if improvements.get('csp_coverage'):
                report.append(f"- **CSP Coverage**: {improvements['csp_coverage']:.2f}% of pages protected with Content Security Policy")
            
            report.append("")
            
            # Success criteria check
            report.append("### Success Criteria Assessment")
            report.append("")
            xss_reduction_pct = xss_improvement.get('reduction_pct', 0)
            secrets_reduction_pct = secrets_improvement.get('reduction_pct', 0)
            
            if xss_reduction_pct >= 95:
                report.append("✅ **XSS Reduction**: ≥95% reduction achieved")
            else:
                report.append(f"⚠️ **XSS Reduction**: {xss_reduction_pct:.2f}% reduction (target: ≥95%)")
            
            if secrets_reduction_pct >= 100:
                report.append("✅ **Secrets Exposure**: 100% reduction achieved")
            else:
                report.append(f"⚠️ **Secrets Exposure**: {secrets_reduction_pct:.2f}% reduction (target: 100%)")
            
            if post_metrics.get('secrets_exposure_rate', 0) == 0:
                report.append("✅ **No Secrets Exposed**: All secrets properly protected")
            else:
                report.append(f"⚠️ **Secrets Still Exposed**: {post_metrics.get('secrets_exposure_rate', 0):.2f}% exposure rate")
    
    report.append("")
    report.append("---")
    report.append("")
    
    # Detailed Metrics
    report.append("## Detailed Metrics Comparison")
    report.append("")
    
    if pre_results and post_results:
        pre_metrics = pre_results.get('metrics', {})
        post_metrics = post_results.get('metrics', {})
        
        report.append("| Metric | Pre-Mitigation | Post-Mitigation | Improvement |")
        report.append("|--------|----------------|-----------------|-------------|")
        
        # XSS Success Rate
        pre_xss = pre_metrics.get('xss_attack_success_rate', 0)
        post_xss = post_metrics.get('xss_attack_success_rate', 0)
        xss_improvement = pre_xss - post_xss
        report.append(f"| XSS Attack Success Rate | {pre_xss:.2f}% | {post_xss:.2f}% | {xss_improvement:.2f}% ↓ |")
        
        # Secrets Exposure Rate
        pre_secrets = pre_metrics.get('secrets_exposure_rate', 0)
        post_secrets = post_metrics.get('secrets_exposure_rate', 0)
        secrets_improvement = pre_secrets - post_secrets
        report.append(f"| Secrets Exposure Rate | {pre_secrets:.2f}% | {post_secrets:.2f}% | {secrets_improvement:.2f}% ↓ |")
        
        # Security Score
        pre_score = pre_metrics.get('security_score', 0)
        post_score = post_metrics.get('security_score', 0)
        score_improvement = post_score - pre_score
        report.append(f"| Security Score | {pre_score:.2f}/100 | {post_score:.2f}/100 | +{score_improvement:.2f} ↑ |")
        
        # CSP Coverage
        post_csp = post_metrics.get('csp_coverage', 0)
        report.append(f"| CSP Coverage | N/A | {post_csp:.2f}% | New Feature |")
        
        # Total Tests
        pre_tests = pre_metrics.get('total_tests', 0)
        post_tests = post_metrics.get('total_tests', 0)
        report.append(f"| Total Tests | {pre_tests} | {post_tests} | - |")
    
    report.append("")
    report.append("---")
    report.append("")
    
    # Vulnerability Analysis
    report.append("## Vulnerability Analysis")
    report.append("")
    
    if pre_results:
        pre_test_results = pre_results.get('test_results', [])
        report.append("### Pre-Mitigation Vulnerabilities Detected")
        report.append("")
        
        vulnerable_tests = []
        for test in pre_test_results:
            for run in test.get('runs', []):
                if run.get('xss_detected') or run.get('secrets_exposed'):
                    vulnerable_tests.append({
                        'test_id': test.get('test_id'),
                        'test_name': test.get('test_name'),
                        'xss': run.get('xss_detected', False),
                        'secrets': run.get('secrets_exposed', False)
                    })
                    break
        
        if vulnerable_tests:
            report.append("| Test ID | Test Name | XSS Detected | Secrets Exposed |")
            report.append("|---------|-----------|--------------|-----------------|")
            for test in vulnerable_tests:
                xss_status = "✅ Yes" if test['xss'] else "❌ No"
                secrets_status = "✅ Yes" if test['secrets'] else "❌ No"
                report.append(f"| {test['test_id']} | {test['test_name']} | {xss_status} | {secrets_status} |")
        else:
            report.append("No vulnerabilities detected in test results.")
    
    report.append("")
    
    if post_results:
        post_test_results = post_results.get('test_results', [])
        report.append("### Post-Mitigation Security Status")
        report.append("")
        
        remaining_vulns = []
        for test in post_test_results:
            for run in test.get('runs', []):
                if run.get('xss_detected') or run.get('secrets_exposed'):
                    remaining_vulns.append({
                        'test_id': test.get('test_id'),
                        'test_name': test.get('test_name'),
                        'xss': run.get('xss_detected', False),
                        'secrets': run.get('secrets_exposed', False)
                    })
                    break
        
        if remaining_vulns:
            report.append("⚠️ **Remaining Vulnerabilities:**")
            report.append("")
            report.append("| Test ID | Test Name | XSS Detected | Secrets Exposed |")
            report.append("|---------|-----------|--------------|-----------------|")
            for test in remaining_vulns:
                xss_status = "⚠️ Yes" if test['xss'] else "✅ No"
                secrets_status = "⚠️ Yes" if test['secrets'] else "✅ No"
                report.append(f"| {test['test_id']} | {test['test_name']} | {xss_status} | {secrets_status} |")
        else:
            report.append("✅ **All Tested Vulnerabilities Mitigated**")
            report.append("")
            report.append("No XSS attacks or secrets exposure detected in post-mitigation tests.")
    
    report.append("")
    report.append("---")
    report.append("")
    
    # Security Improvements Summary
    report.append("## Security Improvements Summary")
    report.append("")
    report.append("The following security measures were implemented in the post-mitigation version:")
    report.append("")
    report.append("1. **Input Sanitization**: All user inputs are sanitized using the `bleach` library")
    report.append("2. **Safe DOM Manipulation**: Replaced `innerHTML` with `textContent` to prevent DOM-based XSS")
    report.append("3. **Content Security Policy**: Implemented CSP headers to prevent inline script execution")
    report.append("4. **Secrets Management**: Moved API keys to environment variables, removed from templates")
    report.append("5. **Security Headers**: Added X-Content-Type-Options, X-Frame-Options, X-XSS-Protection")
    report.append("6. **Debug Mode**: Disabled debug mode and removed debug panels")
    report.append("7. **Output Encoding**: Proper JSON serialization for safe data passing")
    report.append("")
    
    # Recommendations
    report.append("---")
    report.append("")
    report.append("## Recommendations")
    report.append("")
    report.append("### Immediate Actions")
    report.append("- ✅ Input sanitization implemented")
    report.append("- ✅ CSP headers configured")
    report.append("- ✅ Secrets moved to environment variables")
    report.append("")
    report.append("### Ongoing Security Practices")
    report.append("- Regular security audits and penetration testing")
    report.append("- Keep dependencies updated for security patches")
    report.append("- Monitor for new attack vectors")
    report.append("- Implement rate limiting for API endpoints")
    report.append("- Add logging and monitoring for security events")
    report.append("- Conduct regular code reviews focused on security")
    report.append("")
    
    # Limitations
    report.append("---")
    report.append("")
    report.append("## Limitations")
    report.append("")
    report.append("This evaluation is based on a simplified demonstration application. Real-world applications may require:")
    report.append("- Additional security layers (WAF, rate limiting, DDoS protection)")
    report.append("- More comprehensive input validation")
    report.append("- Advanced threat detection and response")
    report.append("- Regular security updates and patches")
    report.append("- Compliance with security standards (OWASP, PCI-DSS, etc.)")
    report.append("")
    
    return "\n".join(report)

def main():
    """Main function to generate comparison report"""
    print("Loading test results...")
    
    pre_results = load_results(PRE_RESULTS_PATH)
    post_results = load_results(POST_RESULTS_PATH)
    
    if not pre_results:
        print(f"Error: Could not load pre-mitigation results from {PRE_RESULTS_PATH}")
        return
    
    if not post_results:
        print(f"Error: Could not load post-mitigation results from {POST_RESULTS_PATH}")
        return
    
    print("Generating comparison report...")
    report = generate_report(pre_results, post_results)
    
    # Write report to file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Comparison report generated: {OUTPUT_PATH}")

if __name__ == '__main__':
    main()

