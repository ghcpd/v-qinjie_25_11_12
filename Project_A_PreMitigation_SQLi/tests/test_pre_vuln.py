"""
Test harness for Project A (Pre-Mitigation)
Tests SQL injection vulnerabilities and measures attack success
"""

import json
import os
import sys
import time
import requests
import subprocess
import signal
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://localhost:5000"
# test_data.json is at the root level (parent of Project_A_PreMitigation_SQLi)
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test_data.json')
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


class VulnerabilityTester:
    def __init__(self):
        self.results = []
        self.server_process = None
        self.test_data = self.load_test_data()
    
    def load_test_data(self):
        """Load test cases from test_data.json"""
        if not os.path.exists(TEST_DATA_PATH):
            raise FileNotFoundError(f"Test data file not found: {TEST_DATA_PATH}")
        
        with open(TEST_DATA_PATH, 'r') as f:
            return json.load(f)
    
    def start_server(self):
        """Start the Flask server"""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'app.py')
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(__file__))
        
        self.server_process = subprocess.Popen(
            [sys.executable, app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Wait for server to start
        max_attempts = 30
        for i in range(max_attempts):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=1)
                if response.status_code == 200:
                    print("Server started successfully")
                    return True
            except:
                time.sleep(0.5)
        
        raise RuntimeError("Failed to start server")
    
    def stop_server(self):
        """Stop the Flask server"""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("Server stopped")
    
    def test_search_endpoint(self, test_case):
        """Test SQL injection on /search endpoint"""
        payload = test_case['input_payload']
        start_time = time.time()
        
        try:
            response = requests.get(
                f"{BASE_URL}/search",
                params={'query': payload},
                timeout=5
            )
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = {
                'test_id': test_case['test_id'],
                'endpoint': '/search',
                'payload': payload,
                'status_code': response.status_code,
                'response_time_ms': round(elapsed_time, 2),
                'response_body': response.text[:500],  # Limit response size
                'vulnerability_detected': False,
                'error_leaked': False,
                'unexpected_results': False
            }
            
            # Check for SQL injection success indicators
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Check if we got unexpected results (SQLi success)
                    if 'results' in data:
                        result_count = data.get('count', 0)
                        # If we got more results than expected for a normal query
                        if test_case['test_id'] != 'normal_query' and result_count > 0:
                            result['unexpected_results'] = True
                            result['vulnerability_detected'] = True
                except:
                    pass
            
            # Check for error leakage
            if 'error' in response.text.lower() or 'sql' in response.text.lower():
                if 'traceback' in response.text.lower() or 'exception' in response.text.lower():
                    result['error_leaked'] = True
                    result['vulnerability_detected'] = True
            
            return result
        
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            return {
                'test_id': test_case['test_id'],
                'endpoint': '/search',
                'payload': payload,
                'status_code': 0,
                'response_time_ms': round(elapsed_time, 2),
                'error': str(e),
                'vulnerability_detected': False
            }
    
    def test_login_endpoint(self, test_case):
        """Test SQL injection on /login endpoint"""
        payload = test_case['input_payload']
        start_time = time.time()
        
        try:
            # Parse payload - could be JSON string or direct value
            if isinstance(payload, str) and payload.startswith('{'):
                import json as json_lib
                payload_data = json_lib.loads(payload)
            else:
                # Assume it's a username injection payload
                payload_data = {
                    'username': payload,
                    'password': 'anything'
                }
            
            response = requests.post(
                f"{BASE_URL}/login",
                json=payload_data,
                timeout=5
            )
            elapsed_time = (time.time() - start_time) * 1000
            
            result = {
                'test_id': test_case['test_id'],
                'endpoint': '/login',
                'payload': str(payload),
                'status_code': response.status_code,
                'response_time_ms': round(elapsed_time, 2),
                'response_body': response.text[:500],
                'vulnerability_detected': False,
                'auth_bypassed': False,
                'error_leaked': False
            }
            
            # Check for authentication bypass
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success') and 'user' in data:
                        result['auth_bypassed'] = True
                        result['vulnerability_detected'] = True
                except:
                    pass
            
            # Check for error leakage
            if 'error' in response.text.lower() and ('traceback' in response.text.lower() or 'exception' in response.text.lower()):
                result['error_leaked'] = True
                result['vulnerability_detected'] = True
            
            return result
        
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            return {
                'test_id': test_case['test_id'],
                'endpoint': '/login',
                'payload': str(payload),
                'status_code': 0,
                'response_time_ms': round(elapsed_time, 2),
                'error': str(e),
                'vulnerability_detected': False
            }
    
    def run_tests(self, repeat_count=1):
        """Run all test cases"""
        print(f"Running {len(self.test_data['test_cases'])} test cases (repeat={repeat_count})...")
        
        for test_case in self.test_data['test_cases']:
            print(f"\nTesting: {test_case['test_id']} - {test_case['description']}")
            
            for iteration in range(repeat_count):
                # Determine which endpoint to test based on test case
                if 'login' in test_case.get('endpoint', '').lower() or 'auth' in test_case.get('description', '').lower():
                    result = self.test_login_endpoint(test_case)
                else:
                    result = self.test_search_endpoint(test_case)
                
                result['iteration'] = iteration + 1
                self.results.append(result)
                
                if result.get('vulnerability_detected'):
                    print(f"  ✓ Vulnerability detected!")
                else:
                    print(f"  - No vulnerability detected")
        
        return self.results
    
    def calculate_metrics(self):
        """Calculate security metrics"""
        total_tests = len(self.results)
        if total_tests == 0:
            return {}
        
        successful_attacks = sum(1 for r in self.results if r.get('vulnerability_detected', False))
        attack_success_rate = (successful_attacks / total_tests) * 100
        
        response_times = [r.get('response_time_ms', 0) for r in self.results if r.get('response_time_ms', 0) > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        error_leaks = sum(1 for r in self.results if r.get('error_leaked', False))
        error_leak_rate = (error_leaks / total_tests) * 100
        
        # Security score (0-100, lower is worse for pre-mitigation)
        security_score = max(0, 100 - attack_success_rate - error_leak_rate)
        
        return {
            'total_tests': total_tests,
            'successful_attacks': successful_attacks,
            'attack_success_rate': round(attack_success_rate, 2),
            'average_response_time_ms': round(avg_response_time, 2),
            'error_leaks': error_leaks,
            'error_leak_rate': round(error_leak_rate, 2),
            'security_score': round(security_score, 2),
            'test_results': self.results
        }
    
    def save_results(self):
        """Save test results to JSON file"""
        metrics = self.calculate_metrics()
        output_path = os.path.join(RESULTS_DIR, 'results_pre.json')
        
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"\nResults saved to {output_path}")
        print(f"\n=== Security Metrics (Pre-Mitigation) ===")
        print(f"Attack Success Rate: {metrics['attack_success_rate']}%")
        print(f"Average Response Time: {metrics['average_response_time_ms']} ms")
        print(f"Error Leak Rate: {metrics['error_leak_rate']}%")
        print(f"Security Score: {metrics['security_score']}/100")
        
        return output_path


def main():
    """Main test execution"""
    tester = VulnerabilityTester()
    
    try:
        # Initialize database
        print("Initializing database...")
        init_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'init_db.py')
        subprocess.run([sys.executable, init_script], check=True)
        
        # Start server
        print("Starting server...")
        tester.start_server()
        time.sleep(2)  # Give server time to fully start
        
        # Run tests
        repeat_count = int(os.environ.get('REPEAT_COUNT', '1'))
        tester.run_tests(repeat_count=repeat_count)
        
        # Save results
        tester.save_results()
    
    finally:
        tester.stop_server()


if __name__ == '__main__':
    main()

