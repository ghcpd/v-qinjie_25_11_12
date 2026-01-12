"""
Project A: Test Suite for Vulnerable Application
Tests SQL injection vulnerabilities and generates results_pre.json
"""

import os
import json
import time
import requests
import logging
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import signal

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'test.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = 'http://127.0.0.1:5000'
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'shared_resources', 'test_data.json')


class VulnerabilityTester:
    """Test harness for SQL injection vulnerabilities."""
    
    def __init__(self):
        self.results = {
            'project': 'Project_A_PreMitigation_SQLi',
            'timestamp': datetime.now().isoformat(),
            'test_results': [],
            'metrics': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'injection_success_count': 0,
                'injection_success_rate': 0.0,
                'avg_response_time_ms': 0.0,
                'leakage_detected': False,
                'security_score': 0
            }
        }
        self.test_cases = []
    
    def load_test_data(self):
        """Load test cases from test_data.json."""
        try:
            with open(TEST_DATA_PATH, 'r') as f:
                data = json.load(f)
                self.test_cases = data.get('test_cases', [])
                logger.info(f"Loaded {len(self.test_cases)} test cases")
        except Exception as e:
            logger.error(f"Failed to load test data: {e}")
            raise
    
    def test_search_endpoint(self, test_case):
        """Test the /search endpoint."""
        test_id = test_case.get('test_id')
        payload = test_case.get('input_payload')
        is_injection = test_case.get('is_injection', False)
        
        logger.info(f"Testing {test_id}: {payload[:50]}...")
        
        try:
            start_time = time.time()
            response = requests.get(
                f'{BASE_URL}/search',
                params={'query': payload},
                timeout=10
            )
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Analyze response
            status_ok = response.status_code == 200
            has_data = len(response.json().get('data', [])) > 0
            leakage = self._check_leakage(response)
            
            # For injection tests, success means we got unexpected data
            if is_injection:
                injection_success = status_ok and has_data
            else:
                injection_success = False
            
            result = {
                'test_id': test_id,
                'description': test_case.get('description'),
                'payload': payload,
                'is_injection': is_injection,
                'status_code': response.status_code,
                'response_time_ms': round(elapsed_ms, 2),
                'data_returned': has_data,
                'injection_successful': injection_success,
                'leakage_detected': leakage,
                'passed': not injection_success  # Pass if injection failed
            }
            
            logger.info(f"{test_id}: status={response.status_code}, data={has_data}, injection={injection_success}, leakage={leakage}")
            
            return result, elapsed_ms, injection_success, leakage
            
        except Exception as e:
            logger.error(f"Error testing {test_id}: {e}")
            return {
                'test_id': test_id,
                'description': test_case.get('description'),
                'payload': payload,
                'is_injection': is_injection,
                'error': str(e),
                'passed': False
            }, 0, False, False
    
    def _check_leakage(self, response):
        """Check for information leakage in response."""
        try:
            response_text = json.dumps(response.json())
            
            # Check for stack traces and sensitive info
            leakage_indicators = [
                'traceback',
                'Traceback',
                'OperationalError',
                'DatabaseError',
                'SyntaxError',
                'near',
                'error in your SQL syntax'
            ]
            
            for indicator in leakage_indicators:
                if indicator in response_text:
                    return True
            
            return False
        except:
            return False
    
    def run_tests(self):
        """Run all test cases."""
        logger.info("Starting vulnerability tests for Project A")
        
        self.load_test_data()
        
        response_times = []
        injection_count = 0
        injection_tests = 0
        leakage_count = 0
        
        for test_case in self.test_cases:
            result, response_time, injection_success, leakage = self.test_search_endpoint(test_case)
            
            self.results['test_results'].append(result)
            
            if result.get('passed') is not None:
                self.results['metrics']['total_tests'] += 1
                if result.get('passed'):
                    self.results['metrics']['passed_tests'] += 1
                else:
                    self.results['metrics']['failed_tests'] += 1
            
            if response_time > 0:
                response_times.append(response_time)
            
            if test_case.get('is_injection'):
                injection_tests += 1
                if injection_success:
                    injection_count += 1
                    self.results['metrics']['injection_success_count'] += 1
            
            if leakage:
                leakage_count += 1
                self.results['metrics']['leakage_detected'] = True
        
        # Calculate metrics
        if injection_tests > 0:
            self.results['metrics']['injection_success_rate'] = round(
                (injection_count / injection_tests) * 100, 2
            )
        
        if response_times:
            self.results['metrics']['avg_response_time_ms'] = round(
                sum(response_times) / len(response_times), 2
            )
        
        # Calculate security score (0-100)
        # Higher injection rate = lower security
        security_score = 100 - self.results['metrics']['injection_success_rate']
        if self.results['metrics']['leakage_detected']:
            security_score -= 10
        self.results['metrics']['security_score'] = max(0, security_score)
        
        logger.info(f"Tests completed: {self.results['metrics']['total_tests']} total, "
                   f"{self.results['metrics']['passed_tests']} passed, "
                   f"Injection success rate: {self.results['metrics']['injection_success_rate']}%")
    
    def save_results(self):
        """Save results to JSON file."""
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        results_file = os.path.join(RESULTS_DIR, 'results_pre.json')
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to: {results_file}")
        print(f"\n{'='*60}")
        print(f"RESULTS SAVED: {results_file}")
        print(f"{'='*60}")


def main():
    """Main test runner."""
    try:
        logger.info("Initializing test harness")
        tester = VulnerabilityTester()
        
        # Wait for server to be ready
        logger.info("Waiting for server to be ready...")
        for attempt in range(30):
            try:
                response = requests.get(f'{BASE_URL}/health', timeout=2)
                if response.status_code == 200:
                    logger.info("Server is ready")
                    break
            except:
                pass
            
            if attempt == 29:
                logger.error("Server did not become ready in time")
                return 1
            
            time.sleep(1)
        
        # Run tests
        tester.run_tests()
        tester.save_results()
        
        # Print summary
        metrics = tester.results['metrics']
        print(f"\nVulnerability Test Summary (Pre-Mitigation):")
        print(f"  Total Tests: {metrics['total_tests']}")
        print(f"  Passed: {metrics['passed_tests']}")
        print(f"  Failed: {metrics['failed_tests']}")
        print(f"  Injection Success Rate: {metrics['injection_success_rate']}%")
        print(f"  Avg Response Time: {metrics['avg_response_time_ms']}ms")
        print(f"  Leakage Detected: {metrics['leakage_detected']}")
        print(f"  Security Score: {metrics['security_score']}/100")
        
        return 0
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
