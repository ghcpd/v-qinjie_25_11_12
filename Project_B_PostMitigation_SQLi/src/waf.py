import re
from flask import request, jsonify

BLOCK_PATTERNS = [
    re.compile(r"--|;|/\*|\*/|\bOR\b|\bUNION\b|\bSLEEP\b", re.I),
]


def waf_middleware():
    q = request.args.get('query', '')
    for p in BLOCK_PATTERNS:
        if p.search(q):
            return jsonify({'error': 'Request blocked by WAF'}), 400
    return None
