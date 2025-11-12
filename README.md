# Vulnerability Detection & Mitigation - Projects

This workspace contains two projects demonstrating SQL Injection vulnerability and its mitigation.

Folders:
- Project_A_PreMitigation_SQLi: vulnerable Flask app + tests
- Project_B_PostMitigation_SQLi: patched Flask app + tests
- test_data.json: shared test cases
- run_all.sh: run both test sets and generate compare report

Run 'bash run_all.sh' to run everything and generate `compare_report.md`.

## Acceptance criteria

- All SQL inputs are parameterized and sanitized in the Post-mitigation project.
- Injection payloads return safe error or empty result in the Post-mitigation project.
- No data leakage or stack trace exposure (stack traces suppressed, errors returned as sanitized messages).
- Response time <200 ms for normal endpoints under moderate load, and average latency increase ≤10% for the patched app relative to the baseline.
- SQLi success rate drop ≥ 95% after mitigation.

## How to run

On systems with bash (Linux, macOS, WSL, Git Bash), run:
- bash run_all.sh

On Windows PowerShell (if bash is not available):
- run `bash run_all.sh` in WSL or Git Bash; or use `run_all.ps1` to invoke the bash script.

Outputs will be produced in `Project_*_*/results` and `compare_report.md` at repository root.
