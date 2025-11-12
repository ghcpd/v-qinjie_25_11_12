Test scenario: SQL Injection via GET endpoints

Endpoints tested:
- /search?query= — user-provided search query used in SQL `LIKE` search. In Project A the value is interpolated directly into SQL causing potential SQL injection (e.g., `"' OR '1'='1"` returns all rows).
- /auth?user=&pwd= — naive login using string interpolation, vulnerable to ' OR 1=1 style bypass.
- /sleep?q= — demonstrates time-based injection; the vulnerable server will emulate a delay when 'SLEEP' token is included.

Tests include normal queries, basic and encoded injections, blind (time-based) injection, and malformed input to ensure proper handling of edge cases.

Acceptance: Post-mitigation application should reject or safely handle all dangerous payloads, parameterize queries, and avoid raw SQL logging.
