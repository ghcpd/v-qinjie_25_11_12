# Compare Report: Pre vs Post Mitigation

## Summary
- Attack Success Rate (pre): 40.0 %
- Attack Success Rate (post): 0.0 %
- Attack Success Rate Reduction: 40.0 %
- Average Latency (pre): 1.63 s
- Average Latency (post): 0.033 s
- Latency Impact (relative): -97.98 %
- Security Score (0-100) pre: 60.0
- Security Score (0-100) post: 100.0
- Leakage counts: pre=0, post=0 

## Acceptance Criteria Checks
- SQLi success rate ¡ý ¡Ý 95%: False
- Average latency increase ¡Ü 10%: False (impact: -97.98 %)
- No exposed errors in logs (post): True

## Per-test results (pre)
- normal_query: sqli_detected=False, latency=0.014864325523376465
- basic_injection: sqli_detected=True, latency=0.020417094230651855
- encoded_injection: sqli_detected=False, latency=0.017702698707580566
- blind_injection: sqli_detected=True, latency=4.010829210281372
- malformed_input: sqli_detected=False, latency=0.011203169822692871

## Per-test results (post)
- normal_query: sqli_detected=False, latency=0.01636350154876709
- basic_injection: sqli_detected=False, latency=0.015915393829345703
- encoded_injection: sqli_detected=False, latency=0.01621270179748535
- blind_injection: sqli_detected=False, latency=0.016896963119506836
- malformed_input: sqli_detected=False, latency=0.01662147045135498

## Recommendations
- Ensure parameterized queries are used for **all** DB paths.
- Add continuous scanning and WAF for production traffic.
- Add more payloads and edge cases to the test set.
