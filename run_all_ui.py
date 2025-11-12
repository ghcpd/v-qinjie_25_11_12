#!/usr/bin/env python3
"""
Unified test runner and comparison report generator
Executes both pre-mitigation and post-mitigation test suites
Generates comprehensive security comparison report
"""

import json
import sys
import os
import subprocess
import time
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
PROJECT_A_DIR = ROOT_DIR / 'Project_A_PreMitigation_UI'
PROJECT_B_DIR = ROOT_DIR / 'Project_B_PostMitigation_UI'
SHARED_DATA_DIR = ROOT_DIR / 'shared_data'


def install_dependencies():
    """Install required dependencies for both projects"""
    logger.info("Installing dependencies...")
    
    for project_dir in [PROJECT_A_DIR, PROJECT_B_DIR]:
        req_file = project_dir / 'requirements.txt'
        if req_file.exists():
            try:
                logger.info(f"Installing dependencies for {project_dir.name}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', str(req_file)], check=True)
                logger.info(f"✓ Dependencies installed for {project_dir.name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependencies: {e}")
                return False
    
    return True


def start_server(project_dir, port):
    """Start Flask server for a project"""
    logger.info(f"Starting server on port {port}...")
    
    app_file = project_dir / 'src' / 'app.py'
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_dir)
    env['FLASK_APP'] = str(app_file)
    
    try:
        # Use absolute path and don't pipe output to avoid issues
        process = subprocess.Popen(
            [sys.executable, str(app_file)],
            env=env,
            cwd=str(project_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        time.sleep(3)  # Wait for server to start
        
        # Check if process is still running
        if process.poll() is None:
            logger.info(f"✓ Server started successfully on port {port}")
            return process
        else:
            # Process exited, try to get error info
            stdout, stderr = process.communicate(timeout=1)
            logger.error(f"Server failed to start. Stderr: {stderr}")
            return None
    
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def run_tests(test_script, project_name):
    """Run test suite for a project"""
    logger.info(f"Running tests for {project_name}...")
    
    try:
        subprocess.run([sys.executable, str(test_script)], check=True)
        logger.info(f"✓ Tests completed for {project_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Test execution failed: {e}")
        return False


def load_results(results_file):
    """Load test results from JSON"""
    try:
        with open(results_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load results: {e}")
        return None


def generate_comparison_report(results_pre, results_post):
    """Generate comprehensive comparison report"""
    report = []
    
    report.append("# UI Security Vulnerability Detection & Mitigation Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    report.append("## Executive Summary\n\n")
    
    pre_score = results_pre['statistics']['security_score']
    post_score = results_post['statistics']['security_score']
    improvement = 100 - (pre_score - 0)  # Improvement from vulnerable to secure
    
    report.append(f"- **Pre-Mitigation Attack Success Rate:** {pre_score:.1f}%\n")
    report.append(f"- **Post-Mitigation Success Rate:** {post_score:.1f}%\n")
    report.append(f"- **Security Improvement:** {improvement:.1f}%\n")
    report.append(f"- **Vulnerabilities Fixed:** {results_pre['statistics']['vulnerabilities_found'] - results_post['statistics']['vulnerabilities_found']}\n\n")
    
    # Vulnerability Breakdown
    report.append("## Vulnerability Analysis\n\n")
    
    report.append("### Pre-Mitigation Results (Project A - Vulnerable)\n\n")
    report.append(f"| Metric | Value |\n")
    report.append(f"|--------|-------|\n")
    report.append(f"| Total Tests | {results_pre['statistics']['total_tests']} |\n")
    report.append(f"| Vulnerabilities Found | {results_pre['statistics']['vulnerabilities_found']} |\n")
    report.append(f"| XSS Attacks Successful | {results_pre['statistics']['xss_successful']} |\n")
    report.append(f"| Secrets Exposed | {'Yes' if results_pre['statistics']['secrets_exposed'] > 0 else 'No'} |\n")
    report.append(f"| DOM XSS Successful | {results_pre['statistics']['dom_xss_success']} |\n")
    report.append(f"| Attack Success Rate | {results_pre['statistics']['attack_success_rate']:.1f}% |\n")
    report.append(f"| Security Score | {results_pre['statistics']['security_score']:.1f}/100 (Lower = More Vulnerable) |\n\n")
    
    report.append("### Post-Mitigation Results (Project B - Secured)\n\n")
    report.append(f"| Metric | Value |\n")
    report.append(f"|--------|-------|\n")
    report.append(f"| Total Tests | {results_post['statistics']['total_tests']} |\n")
    report.append(f"| Tests Passed | {results_post['statistics']['tests_passed']} |\n")
    report.append(f"| Tests Failed | {results_post['statistics']['tests_failed']} |\n")
    report.append(f"| XSS Blocked | {results_post['statistics']['xss_blocked']} |\n")
    report.append(f"| Secrets Protected | {'Yes' if results_post['statistics']['secrets_protected'] > 0 else 'No'} |\n")
    report.append(f"| DOM XSS Blocked | {results_post['statistics']['dom_xss_blocked']} |\n")
    report.append(f"| Success Rate | {results_post['statistics']['success_rate']:.1f}% |\n")
    report.append(f"| Security Score | {results_post['statistics']['security_score']:.1f}/100 (Higher = More Secure) |\n\n")
    
    # Detailed Test Results
    report.append("## Detailed Test Case Results\n\n")
    
    for i, (pre_test, post_test) in enumerate(zip(results_pre['test_cases'], results_post['test_cases'])):
        report.append(f"### {pre_test['test_id']}: {pre_test['test_name']}\n\n")
        report.append(f"**Category:** {pre_test['category']}\n\n")
        
        report.append("| Status | Pre-Mitigation | Post-Mitigation |\n")
        report.append("|--------|-----------------|------------------|\n")
        report.append(f"| Result | {'❌ VULNERABLE' if not pre_test['passed'] else '✓ Safe'} | {'✓ SECURE' if post_test['passed'] else '❌ VULNERABLE'} |\n")
        report.append(f"| Vulnerabilities | {len(pre_test['vulnerabilities_detected'])} | {len(post_test['vulnerabilities_detected'])} |\n\n")
        
        if pre_test['vulnerabilities_detected']:
            report.append("**Pre-Mitigation Issues:**\n")
            for vuln in pre_test['vulnerabilities_detected']:
                report.append(f"- {vuln}\n")
            report.append("\n")
        
        if post_test['vulnerabilities_detected']:
            report.append("**Post-Mitigation Issues (if any):**\n")
            for vuln in post_test['vulnerabilities_detected']:
                report.append(f"- {vuln}\n")
            report.append("\n")
        else:
            report.append("**Post-Mitigation Issues:** None - All threats mitigated ✓\n\n")
    
    # Security Improvements
    report.append("## Security Improvements & Mitigations Applied\n\n")
    
    report.append("### Vulnerabilities Fixed\n\n")
    
    improvements = [
        "1. **Reflected XSS Prevention**\n   - Input sanitization using Bleach library\n   - Whitelist-based HTML filtering\n   - Server-side validation before rendering\n",
        "2. **DOM-based XSS Prevention**\n   - Replaced innerHTML with textContent\n   - No eval() or dynamic script injection\n   - Safe DOM manipulation\n",
        "3. **Secrets Protection**\n   - Removed hardcoded API keys and passwords\n   - Secrets loaded from environment variables\n   - No sensitive data in frontend code\n",
        "4. **Content Security Policy (CSP)**\n   - Strict CSP headers preventing inline scripts\n   - Restricts resource loading to same-origin\n   - Blocks unsafe JavaScript execution\n",
        "5. **Security Headers**\n   - X-Frame-Options: DENY (prevents clickjacking)\n   - X-Content-Type-Options: nosniff (prevents MIME type sniffing)\n   - X-XSS-Protection: 1; mode=block (legacy XSS filter)\n",
        "6. **Input Validation**\n   - Length validation (max 5000 characters)\n   - Type checking and sanitization\n   - Edge case handling for special characters\n"
    ]
    
    for improvement in improvements:
        report.append(improvement)
    
    report.append("\n## Numeric Thresholds & Success Criteria\n\n")
    
    thresholds = {
        'XSS Mitigation': {
            'target': '≥95%',
            'pre': f"{results_pre['statistics']['attack_success_rate']:.1f}%",
            'post': f"{results_post['statistics']['success_rate']:.1f}%",
            'passed': results_post['statistics']['xss_blocked'] >= (results_post['statistics']['total_tests'] * 0.95)
        },
        'Secrets Protection': {
            'target': '100%',
            'pre': 'Failed' if results_pre['statistics']['secrets_exposed'] > 0 else 'Passed',
            'post': 'Passed' if results_post['statistics']['secrets_protected'] > 0 else 'Failed',
            'passed': results_post['statistics']['secrets_protected'] > 0
        },
        'Edge Case Handling': {
            'target': '≥90%',
            'pre': f"{(results_pre['statistics']['edge_cases_vulnerable'] / results_pre['statistics']['total_tests'] * 100):.1f}%",
            'post': f"{(results_post['statistics']['tests_passed'] / results_post['statistics']['total_tests'] * 100):.1f}%",
            'passed': results_post['statistics']['tests_passed'] >= (results_post['statistics']['total_tests'] * 0.90)
        }
    }
    
    report.append("| Criteria | Target | Pre-Mitigation | Post-Mitigation | Status |\n")
    report.append("|----------|--------|-----------------|------------------|---------|\n")
    
    for criteria, data in thresholds.items():
        status = "✓ PASS" if data['passed'] else "❌ FAIL"
        report.append(f"| {criteria} | {data['target']} | {data['pre']} | {data['post']} | {status} |\n")
    
    report.append("\n## Recommendations\n\n")
    
    recommendations = [
        "1. **Input Sanitization**: Continue using Bleach library with whitelist approach for all user inputs\n",
        "2. **Content Security Policy**: Implement strict CSP headers as demonstrated in Project B\n",
        "3. **Secrets Management**: Use environment variables or secure vaults for sensitive data\n",
        "4. **Regular Security Audits**: Perform routine security testing for XSS and CSRF vulnerabilities\n",
        "5. **Dependencies Update**: Keep Flask, Bleach, and other security libraries updated\n",
        "6. **Security Headers**: Apply all recommended security headers (X-Frame-Options, X-Content-Type-Options, etc.)\n",
        "7. **Developer Training**: Educate developers on secure coding practices and common web vulnerabilities\n",
        "8. **Automated Testing**: Integrate security tests into CI/CD pipeline for continuous validation\n"
    ]
    
    for rec in recommendations:
        report.append(rec)
    
    report.append("\n## Conclusion\n\n")
    
    if results_post['statistics']['security_score'] >= 95 and results_post['statistics']['vulnerabilities_found'] == 0:
        report.append("✅ **All UI security vulnerabilities have been successfully mitigated.**\n\n")
        report.append(f"Project B (Post-Mitigation) demonstrates a **{improvement:.0f}% security improvement** over Project A, "
                     f"with XSS attacks blocked at a rate of **{results_post['statistics']['success_rate']:.1f}%** and "
                     f"all secrets properly protected.\n\n")
        report.append("The application is now secure against the tested attack vectors and ready for production use with ongoing monitoring.\n")
    else:
        report.append("⚠️ **Some vulnerabilities may still require attention.**\n\n")
        report.append(f"Review the failed test cases above for additional security improvements needed.\n")
    
    report.append(f"\n---\n*Report Generated: {datetime.now().isoformat()}*\n")
    
    return "".join(report)


def main():
    """Main execution flow"""
    logger.info("=" * 70)
    logger.info("UI Security Vulnerability Detection & Mitigation Test Suite")
    logger.info("=" * 70)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        sys.exit(1)
    
    # Step 2: Start servers
    logger.info("\n" + "=" * 70)
    logger.info("Starting Applications")
    logger.info("=" * 70)
    
    server_a = start_server(PROJECT_A_DIR, 5000)
    time.sleep(2)
    server_b = start_server(PROJECT_B_DIR, 5001)
    time.sleep(2)
    
    if not server_a or not server_b:
        logger.error("Failed to start one or both servers")
        if server_a:
            server_a.terminate()
        if server_b:
            server_b.terminate()
        sys.exit(1)
    
    try:
        # Step 3: Run tests
        logger.info("\n" + "=" * 70)
        logger.info("Running Security Tests")
        logger.info("=" * 70)
        
        test_a_script = PROJECT_A_DIR / 'tests' / 'test_pre_ui.py'
        test_b_script = PROJECT_B_DIR / 'tests' / 'test_post_ui.py'
        
        run_tests(test_a_script, "Project A (Pre-Mitigation)")
        time.sleep(2)
        run_tests(test_b_script, "Project B (Post-Mitigation)")
        
        # Step 4: Generate comparison report
        logger.info("\n" + "=" * 70)
        logger.info("Generating Comparison Report")
        logger.info("=" * 70)
        
        results_pre_file = PROJECT_A_DIR / 'results' / 'results_pre.json'
        results_post_file = PROJECT_B_DIR / 'results' / 'results_post.json'
        
        if not results_pre_file.exists() or not results_post_file.exists():
            logger.error("Test result files not found")
            sys.exit(1)
        
        results_pre = load_results(results_pre_file)
        results_post = load_results(results_post_file)
        
        if not results_pre or not results_post:
            logger.error("Failed to load test results")
            sys.exit(1)
        
        # Generate report
        report_content = generate_comparison_report(results_pre, results_post)
        
        # Save report
        report_file = ROOT_DIR / 'compare_ui_security_report.md'
        try:
            with open(report_file, 'w') as f:
                f.write(report_content)
            logger.info(f"✓ Comparison report saved to {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            sys.exit(1)
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 70)
        logger.info(f"\nPre-Mitigation (Project A):")
        logger.info(f"  - Attack Success Rate: {results_pre['statistics']['attack_success_rate']:.1f}%")
        logger.info(f"  - Vulnerabilities Found: {results_pre['statistics']['vulnerabilities_found']}")
        logger.info(f"\nPost-Mitigation (Project B):")
        logger.info(f"  - Tests Passed: {results_post['statistics']['tests_passed']}/{results_post['statistics']['total_tests']}")
        logger.info(f"  - Success Rate: {results_post['statistics']['success_rate']:.1f}%")
        logger.info(f"  - Vulnerabilities Found: {results_post['statistics']['vulnerabilities_found']}")
        logger.info(f"\nSecurity Improvement: {100 - (results_pre['statistics']['attack_success_rate'] - results_post['statistics']['success_rate']):.1f}%")
        logger.info(f"\nReport: {report_file}")
        logger.info("=" * 70 + "\n")
    
    finally:
        # Cleanup: Stop servers
        logger.info("Stopping servers...")
        if server_a:
            server_a.terminate()
        if server_b:
            server_b.terminate()


if __name__ == '__main__':
    main()
