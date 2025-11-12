"""
Pre-Mitigation UI Security Test Suite
Tests Project A (Pre-Mitigation) for XSS vulnerabilities and secrets exposure
Detects whether vulnerabilities are present and can be exploited
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
import requests

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
        logging.FileHandler(LOG_DIR / 'test_pre_ui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = 'http://127.0.0.1:5000'
WAIT_TIMEOUT = 10


class PreMitigationUITester:
    """Test suite for pre-mitigation vulnerable UI"""
    
    def __init__(self):
        self.driver = None
        self.test_results = {
            'project': 'Project_A_PreMitigation_UI',
            'timestamp': datetime.now().isoformat(),
            'test_cases': [],
            'statistics': {
                'total_tests': 0,
                'xss_successful': 0,
                'secrets_exposed': 0,
                'dom_xss_success': 0,
                'edge_cases_vulnerable': 0,
                'vulnerabilities_found': 0,
                'attack_success_rate': 0.0,
                'security_score': 0  # Lower is worse (more vulnerable)
            }
        }
        self.secrets_found = {
            'api_keys': [],
            'tokens': [],
            'passwords': [],
            'other_secrets': []
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
        """Check if JavaScript alert was triggered (indicates XSS success)"""
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            logger.warning(f"XSS DETECTED: Alert triggered with message: {alert_text}")
            return True, alert_text
        except NoAlertPresentException:
            return False, None
    
    def check_secrets_in_page(self):
        """Check for exposed secrets in page source and DOM"""
        secrets_found = {}
        page_source = self.driver.page_source.lower()
        
        secret_patterns = {
            'api_key': ['sk-', 'api_key', 'api-key', 'sk_1234567890'],
            'database_password': ['admin_db_password', 'db_password', 'admin_db_pass'],
            'admin_token': ['admin_token', 'jwt_secret', 'eyjaalgcihsijin'],
            'session_id': ['sess_prod_secret', 'session_id']
        }
        
        for secret_type, patterns in secret_patterns.items():
            for pattern in patterns:
                if pattern.lower() in page_source:
                    secrets_found[secret_type] = True
                    self.secrets_found[secret_type].append(pattern)
                    logger.warning(f"SECRET EXPOSED: {secret_type} detected with pattern '{pattern}'")
        
        return secrets_found
    
    def check_console_logs(self):
        """Check browser console for sensitive information"""
        logs = self.driver.get_log('browser')
        sensitive_data_found = False
        
        for entry in logs:
            message = entry['message'].lower()
            if any(x in message for x in ['api key', 'secret', 'password', 'token']):
                logger.warning(f"SENSITIVE DATA IN CONSOLE: {entry['message']}")
                sensitive_data_found = True
        
        return sensitive_data_found, logs
    
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
            
            # Wait for comment to appear
            time.sleep(2)
            
            # Check for errors
            alert_found, _ = self.check_for_alert()
            result['details']['xss_attempted'] = alert_found
            
            # Verify input appears correctly
            comments_section = self.driver.find_element(By.ID, "comments-list")
            if test_case['input_payload'] in comments_section.text:
                result['passed'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - Safe input rendered correctly")
            else:
                result['vulnerabilities_detected'].append("Input not rendered correctly")
                logger.warning(f"✗ {test_case['test_id']} FAILED - Input not found in rendered output")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test execution error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_reflected_xss(self, test_case):
        """TEST_002: Reflected XSS - Script Alert"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_successful': False,
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
            
            # Check for alert (XSS success indicator)
            time.sleep(1)
            alert_found, alert_text = self.check_for_alert()
            result['details']['xss_attempted'] = alert_found
            result['details']['alert_text'] = alert_text
            
            if alert_found:
                result['vulnerabilities_detected'].append("XSS VULNERABILITY: Script executed successfully")
                result['xss_successful'] = True
                logger.error(f"✗ VULNERABILITY DETECTED: {test_case['test_id']} - XSS executed")
            else:
                result['passed'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - XSS blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test execution error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_dom_xss(self, test_case):
        """TEST_003: DOM XSS - innerHTML Injection"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_successful': False,
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
            result['details']['xss_attempted'] = alert_found
            
            if alert_found:
                result['vulnerabilities_detected'].append("DOM XSS VULNERABILITY: Event handler executed")
                result['xss_successful'] = True
                logger.error(f"✗ VULNERABILITY DETECTED: {test_case['test_id']} - DOM XSS executed")
            else:
                result['passed'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - DOM XSS blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test execution error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_secrets_exposure(self, test_case):
        """TEST_004: Secrets Exposure"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': True,
            'vulnerabilities_detected': [],
            'secrets_exposed': False,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            self.driver.get(f"{BASE_URL}/")
            time.sleep(2)
            
            # Check page source for secrets
            secrets_in_page = self.check_secrets_in_page()
            if secrets_in_page:
                for secret_type in secrets_in_page:
                    result['vulnerabilities_detected'].append(f"INFORMATION DISCLOSURE: {secret_type} exposed")
                    result['secrets_exposed'] = True
                    result['passed'] = False
                logger.error(f"✗ VULNERABILITY DETECTED: {test_case['test_id']} - Secrets exposed")
            
            # Check console logs
            _, console_logs = self.check_console_logs()
            result['details']['console_logs_count'] = len(console_logs)
            
            if result['passed']:
                logger.info(f"✓ {test_case['test_id']} PASSED - No secrets exposed")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test execution error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_malformed_input(self, test_case):
        """TEST_005: Malformed Input - Edge Cases"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_successful': False,
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
            result['details']['xss_attempted'] = alert_found
            
            if alert_found:
                result['vulnerabilities_detected'].append("EDGE CASE XSS: Malformed input bypassed filter")
                result['xss_successful'] = True
                logger.error(f"✗ VULNERABILITY DETECTED: {test_case['test_id']} - XSS via edge case")
            else:
                result['passed'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - Edge case handled safely")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test execution error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_event_handler_injection(self, test_case):
        """TEST_006: Event Handler Injection"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_successful': False,
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
            result['details']['xss_attempted'] = alert_found
            
            if alert_found:
                result['vulnerabilities_detected'].append("EVENT HANDLER XSS: onclick executed")
                result['xss_successful'] = True
                logger.error(f"✗ VULNERABILITY DETECTED: {test_case['test_id']} - Event handler XSS")
            else:
                result['passed'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - Event handler blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test execution error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_data_exfiltration(self, test_case):
        """TEST_007: Data Exfiltration"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': True,
            'vulnerabilities_detected': [],
            'xss_successful': False,
            'details': {}
        }
        
        try:
            logger.info(f"Running {test_case['test_id']}: {test_case['test_name']}")
            
            # This would require network monitoring; for now check if script can execute
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
                result['vulnerabilities_detected'].append("DATA EXFILTRATION: Fetch request could execute")
                result['xss_successful'] = True
                result['passed'] = False
                logger.error(f"✗ VULNERABILITY DETECTED: {test_case['test_id']} - Data exfiltration possible")
            else:
                logger.info(f"✓ {test_case['test_id']} PASSED - Exfiltration prevented")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test execution error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def test_svg_xss(self, test_case):
        """TEST_008: SVG/XML XSS"""
        result = {
            'test_id': test_case['test_id'],
            'test_name': test_case['test_name'],
            'category': test_case['category'],
            'passed': False,
            'vulnerabilities_detected': [],
            'xss_successful': False,
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
            result['details']['xss_attempted'] = alert_found
            
            if alert_found:
                result['vulnerabilities_detected'].append("SVG XSS VULNERABILITY: onload executed")
                result['xss_successful'] = True
                logger.error(f"✗ VULNERABILITY DETECTED: {test_case['test_id']} - SVG XSS")
            else:
                result['passed'] = True
                logger.info(f"✓ {test_case['test_id']} PASSED - SVG XSS blocked")
        
        except Exception as e:
            result['vulnerabilities_detected'].append(f"Test execution error: {str(e)}")
            logger.error(f"Error in {test_case['test_id']}: {e}")
        
        return result
    
    def run_all_tests(self):
        """Execute all test cases"""
        logger.info("=" * 70)
        logger.info("Starting Pre-Mitigation UI Security Test Suite")
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
        
        if result.get('xss_successful'):
            stats['xss_successful'] += 1
            stats['vulnerabilities_found'] += 1
        
        if result.get('secrets_exposed'):
            stats['secrets_exposed'] += 1
            stats['vulnerabilities_found'] += 1
        
        if result['test_id'] in ['TEST_003', 'TEST_006', 'TEST_008'] and result.get('xss_successful'):
            stats['dom_xss_success'] += 1
        
        if result['test_id'] == 'TEST_005' and result.get('xss_successful'):
            stats['edge_cases_vulnerable'] += 1
    
    def calculate_final_score(self):
        """Calculate final security score"""
        stats = self.test_results['statistics']
        total = stats['total_tests']
        
        if total > 0:
            # Pre-mitigation: more vulnerabilities = lower score
            # Score: 0-100, where 100 is fully vulnerable (all attacks succeed)
            success_rate = (stats['vulnerabilities_found'] / total) * 100
            stats['attack_success_rate'] = success_rate
            stats['security_score'] = success_rate  # For pre-mitigation, higher score = worse
            logger.info(f"Attack success rate: {success_rate:.1f}%")
            logger.info(f"Security score: {stats['security_score']:.1f}")
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = RESULTS_DIR / 'results_pre.json'
        try:
            with open(results_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            logger.info(f"Results saved to {results_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


def main():
    """Main entry point"""
    tester = PreMitigationUITester()
    results = tester.run_all_tests()
    tester.save_results()
    
    logger.info("=" * 70)
    logger.info("Test Summary:")
    logger.info(f"Total Tests: {results['statistics']['total_tests']}")
    logger.info(f"Vulnerabilities Found: {results['statistics']['vulnerabilities_found']}")
    logger.info(f"XSS Successful: {results['statistics']['xss_successful']}")
    logger.info(f"Attack Success Rate: {results['statistics']['attack_success_rate']:.1f}%")
    logger.info(f"Security Score: {results['statistics']['security_score']:.1f}")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
