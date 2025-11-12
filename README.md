# Vulnerability Detection & Mitigation - SQL Injection Demo

This workspace contains two projects demonstrating a SQL injection vulnerability (pre-mitigation) and a patched app (post-mitigation). Use `run_all.sh` or `run_all.ps1` to run the experiments and generate a comparison report.

## Acceptance Criteria
- SQLi success rate reduced by ≥ 95% after mitigation.
- Latency increase ≤ 10% after mitigation.
- No error stack traces or data leakage from the patched app.

Use the scripts in each project folder (`run_tests.sh` / `run_tests.ps1`) to run the example tests in isolation.

Windows: use `run_all.bat` or `run_all_windows.ps1` to run both projects and generate the compare report:
- `run_all.bat 2 10` (REPEAT=2, DB_SIZE=10)
- `PowerShell -File run_all_windows.ps1 -REPEAT 2 -DB_SIZE 10`
