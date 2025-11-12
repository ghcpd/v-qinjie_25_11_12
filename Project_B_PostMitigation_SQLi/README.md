# Project B — Post-Mitigations (Patched)

This Flask app includes protections against SQL Injection: parameterized queries, input validation middleware (a simple WAF), and a more defensive error handling model.

How to run:
- bash setup.sh
- bash run_tests.sh

Results:
- results/results_post.json
- logs/server.log

The tests mirror those in Project A and validate no injections succeed.
