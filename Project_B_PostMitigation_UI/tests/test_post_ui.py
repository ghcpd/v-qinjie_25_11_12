"""
Post-Mitigation UI Security Test Suite
Tests Project B (Post-Mitigation) to verify that XSS vulnerabilities and secrets exposure are fixed
"""

import json
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoAlertPresentException

# Setup absolute paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
ROOT_DIR = PROJECT_DIR.parent
LOG_DIR = PROJECT_DIR / 'logs'
RESULTS_DIR = PROJECT_DIR / 'results'
TEST_DATA_PATH = ROOT_DIR / 'shared_data' / 'test_ui_vuln.json'

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'test_post_ui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = 'http://127.0.0.1:5001'
WAIT_TIMEOUT = 10


class PostMitigationUITester:
    """Test suite for post-mitigation secure UI"""
    
    def __init__(self):
        self.driver = None
        self.test_results = {
            'project': 'Project_B_PostMitigation_UI',
            'timestamp': datetime.now().isoformat(),
            'test_cases': [],
            'statistics': {
                'total_tests': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'xss_blocked': 0,
                'secrets_protected': 0,
                'dom_xss_blocked': 0,
                'edge_cases_handled': 0,
                'vulnerabilities_found': 0,
                'success_rate': 0.0,
                'security_score': 0  # Higher is better (more secure)
            }
        }
        self.load_test_data()
    
    def load_test_data(self):
        """Load test cases from JSON"""
        try:
            with open(TEST_DATA_PATH, 'r') as f:
                self.test_data = json.load(f)
            logger.info(f"Loaded {len(self.test_data['test_cases'])} test cases")
        except Exception as e:
            logger.error(f"Failed to load test data: {e}")
            sys.exit(1)
    
    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        try:
            options = webdriver.ChromeOptions()
            # Uncomment for headless mode:
            # options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            try:
                # Try to download the matching version
                service = Service(ChromeDriverManager().install())
            except Exception as e:
                logger.warning(f"ChromeDriverManager failed: {e}. Using default driver search.")
                # Fallback: don't specify a path, let Chrome find it in PATH
                service = None
            
            self.driver = webdriver.Chrome(service=service, options=options)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            sys.exit(1)
    
    def teardown_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def check_for_alert(self):
        """Check if JavaScript alert was triggered"""
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            return True, alert_text
        except NoAlertPresentException:
            return False, None
    
    def check_csp_headers(self):
        """Check if security headers are present"""
        headers_check = {
            'csp_present': False,
            'x_frame_options': False,
            'x_content_type_options': False
        }
        
        try:
            # Note: Direct header access via Selenium is limited
            # This is more for documentation
            logger.info("CSP headers should be enforced by server")
        except Exception as e:
            logger.warning(f"Could not verify headers: {e}")
        
        return headers_check
    
    def check_secrets_in_page(self):
        """Verify no secrets are exposed"""
        page_source = self.driver.page_source.lower()
        secrets_found = []
        
        secret_patterns = {
            'api_key': ['sk-1234567890', 'sk_1234567890'],
            'database_password': ['admin_db_password_prod'],
            'admin_token': ['eyjaalgcihsijin'],
        }
        
        for secret_type, patterns in secret_patterns.items():
            for pattern in patterns:
                if pattern.lower() in page_source:
                    secrets_found.append(f"{secret_type}: {pattern}")
                    logger.warning(f"SECRET FOUND: {secret_type}")
        
        if not secrets_found:
            logger.info("✓ No secrets exposed in page source")
        
        return secrets_found
    
    def test_normal_input(self, test_case):
        """TEST_001: Normal input rendering"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            input_elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "comment-input"))
            )
            
            # Enter safe input
            input_elem.send_keys(test_case['input_payload'])
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post Comment')]")
            submit_btn.click()
            
            time.sleep(2)
            
            # Check for errors
            alert_found, _ = self.check_for_alert()
            result['details']['xss_attempted'] = alert_found
            
            # Verify input appears correctly
            comments_section = self.driver.find_element(By.ID, "comments-list")
            if test_case['input_payload'] in comments_section.text:
                result['passed'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED")
            else:
                result['vulnerabilities_detected'].append("Input not rendered correctly")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_reflected_xss(self, test_case):
        """TEST_002: Reflected XSS - Script Alert (should be blocked)"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_blocked': True,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            input_elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "comment-input"))
            )
            
            # Send XSS payload
            input_elem.send_keys(test_case['input_payload'])
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post Comment')]")
            submit_btn.click()
            
            time.sleep(1)
            alert_found, alert_text = self.check_for_alert()
            result['details']['xss_attempted'] = alert_found
            
            if alert_found:
                result['vulnerabilities_detected'].append("XSS vulnerability still present")
                result['xss_blocked'] = False
                result['passed'] = False
                logger.error(f"✗ {test_case['test_id']} FAILED - XSS not blocked")
            else:
                result['passed'] = True
                result['xss_blocked'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - XSS blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_dom_xss(self, test_case):
        """TEST_003: DOM XSS - innerHTML Injection (should be blocked)"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_blocked': True,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            input_elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "comment-input"))
            )
            
            # Send DOM XSS payload
            input_elem.send_keys(test_case['input_payload'])
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post Comment')]")
            submit_btn.click()
            
            time.sleep(1)
            alert_found, alert_text = self.check_for_alert()
            
            if alert_found:
                result['vulnerabilities_detected'].append("DOM XSS vulnerability still present")
                result['xss_blocked'] = False
                result['passed'] = False
                logger.error(f"✗ {test_case['test_id']} FAILED - DOM XSS not blocked")
            else:
                result['passed'] = True
                result['xss_blocked'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - DOM XSS blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_secrets_exposure(self, test_case):
        """TEST_004: Secrets Exposure (should find none)"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': True,
            'vulnerabilities_detected': [],
            'secrets_protected': True,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            time.sleep(2)
            
            # Check page source for secrets
            secrets_found = self.check_secrets_in_page()
            if secrets_found:
                for secret in secrets_found:
                    result['vulnerabilities_detected'].append(f"Secret exposed: {secret}")
                result['secrets_protected'] = False
                result['passed'] = False
                logger.error(f"✗ {test_case['test_id']} FAILED - Secrets exposed")
            else:
                result['passed'] = True
                result['secrets_protected'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - Secrets protected")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_malformed_input(self, test_case):
        """TEST_005: Malformed Input - Edge Cases (should be handled safely)"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_blocked': True,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            input_elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "comment-input"))
            )
            
            # Send complex malformed input
            input_elem.send_keys(test_case['input_payload'])
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post Comment')]")
            submit_btn.click()
            
            time.sleep(1)
            alert_found, alert_text = self.check_for_alert()
            
            if alert_found:
                result['vulnerabilities_detected'].append("Edge case XSS not blocked")
                result['xss_blocked'] = False
                result['passed'] = False
                logger.error(f"✗ {test_case['test_id']} FAILED - Edge case XSS")
            else:
                result['passed'] = True
                result['xss_blocked'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - Edge case handled safely")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_event_handler_injection(self, test_case):
        """TEST_006: Event Handler Injection (should be blocked)"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_blocked': True,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            input_elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "comment-input"))
            )
            
            input_elem.send_keys(test_case['input_payload'])
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post Comment')]")
            submit_btn.click()
            
            time.sleep(1)
            alert_found, alert_text = self.check_for_alert()
            
            if alert_found:
                result['vulnerabilities_detected'].append("Event handler injection not blocked")
                result['xss_blocked'] = False
                result['passed'] = False
                logger.error(f"✗ {test_case['test_id']} FAILED - Event handler XSS")
            else:
                result['passed'] = True
                result['xss_blocked'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - Event handler blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_data_exfiltration(self, test_case):
        """TEST_007: Data Exfiltration (should be blocked)"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_blocked': True,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            input_elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "comment-input"))
            )
            
            input_elem.send_keys(test_case['input_payload'])
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post Comment')]")
            submit_btn.click()
            
            time.sleep(1)
            alert_found, alert_text = self.check_for_alert()
            
            if alert_found:
                result['vulnerabilities_detected'].append("Data exfiltration not blocked")
                result['xss_blocked'] = False
                result['passed'] = False
                logger.error(f"✗ {test_case['test_id']} FAILED - Exfiltration XSS")
            else:
                result['passed'] = True
                result['xss_blocked'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - Exfiltration blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_svg_xss(self, test_case):
        """TEST_008: SVG/XML XSS (should be blocked)"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_blocked': True,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            input_elem = WebDriverWait(self.driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "comment-input"))
            )
            
            input_elem.send_keys(test_case['input_payload'])
            submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post Comment')]")
            submit_btn.click()
            
            time.sleep(1)
            alert_found, alert_text = self.check_for_alert()
            
            if alert_found:
                result['vulnerabilities_detected'].append("SVG XSS not blocked")
                result['xss_blocked'] = False
                result['passed'] = False
                logger.error(f"✗ {test_case['test_id']} FAILED - SVG XSS")
            else:
                result['passed'] = True
                result['xss_blocked'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - SVG XSS blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def run_all_tests(self):
        """Execute all test cases"""
        logger.info("=" * 70)
        logger.info("Starting Post-Mitigation UI Security Test Suite")
        logger.info("=" * 70)
        
        self.setup_driver()
        
        # Map test IDs to test methods
        test_methods = {
            'TEST_001': self.test_normal_input,
            'TEST_002': self.test_reflected_xss,
            'TEST_003': self.test_dom_xss,
            'TEST_004': self.test_secrets_exposure,
            'TEST_005': self.test_malformed_input,
            'TEST_006': self.test_event_handler_injection,
            'TEST_007': self.test_data_exfiltration,
            'TEST_008': self.test_svg_xss
        }
        
        for test_case in self.test_data['test_cases']:
            test_id = test_case['test_id']
            if test_id in test_methods:
                result = test_methods[test_id](test_case)
                self.test_results['test_cases'].append(result)
                self.update_statistics(result)
        
        self.calculate_final_score()
        self.teardown_driver()
        
        return self.test_results
    
    def update_statistics(self, result):
        """Update statistics based on test result"""
        stats = self.test_results['statistics']
        stats['total_tests'] += 1
        
        if result['passed']:
            stats['tests_passed'] += 1
        else:
            stats['tests_failed'] += 1
            stats['vulnerabilities_found'] += 1
        
        if result.get('xss_blocked'):
            stats['xss_blocked'] += 1
        
        if result.get('secrets_protected'):
            stats['secrets_protected'] += 1
        
        if result['test_id'] in ['TEST_003', 'TEST_006', 'TEST_008'] and result.get('xss_blocked'):
            stats['dom_xss_blocked'] += 1
        
        if result['test_id'] == 'TEST_005' and result.get('xss_blocked'):
            stats['edge_cases_handled'] += 1
    
    def calculate_final_score(self):
        """Calculate final security score"""
        stats = self.test_results['statistics']
        total = stats['total_tests']
        
        if total > 0:
            # Post-mitigation: more passed tests = higher score
            # Score: 0-100, where 100 is fully secure (all attacks blocked)
            success_rate = (stats['tests_passed'] / total) * 100
            stats['success_rate'] = success_rate
            stats['security_score'] = success_rate
            logger.info(f"Success rate (tests passed): {success_rate:.1f}%")
            logger.info(f"Security score: {stats['security_score']:.1f}")
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = RESULTS_DIR / 'results_post.json'
        try:
            with open(results_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            logger.info(f"Results saved to {results_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


def main():
    """Main entry point"""
    tester = PostMitigationUITester()
    results = tester.run_all_tests()
    tester.save_results()
    
    logger.info("=" * 70)
    logger.info("Test Summary:")
    logger.info(f"Total Tests: {results['statistics']['total_tests']}")
    logger.info(f"Tests Passed: {results['statistics']['tests_passed']}")
    logger.info(f"Tests Failed: {results['statistics']['tests_failed']}")
    logger.info(f"XSS Blocked: {results['statistics']['xss_blocked']}")
    logger.info(f"Secrets Protected: {results['statistics']['secrets_protected']}")
    logger.info(f"Success Rate: {results['statistics']['success_rate']:.1f}%")
    logger.info(f"Security Score: {results['statistics']['security_score']:.1f}")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
