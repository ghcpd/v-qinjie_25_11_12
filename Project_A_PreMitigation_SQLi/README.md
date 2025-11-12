# Project A — Pre-Mitigations (Vulnerable)

This is a simple Flask app intentionally vulnerable to SQL Injection. It exposes endpoints that accept user input and build SQL queries via naive string interpolation.

How to run:
- bash setup.sh
- bash run_tests.sh

Results:
- results/results_pre.json
- logs/server.log

The tests attempt injection payloads (basic, encoded, timed) and report whether vulnerabilities were successful.
