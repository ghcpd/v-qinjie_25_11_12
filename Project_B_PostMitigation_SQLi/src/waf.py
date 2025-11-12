import re
from flask import request, jsonify

BLACKLIST = [r"\bOR\b", r"1=1", r"--", r";", r"/\*", r"sleep\(", r"\bUNION\b", r"DROP\b", r"\bSELECT\b.*sleep\("]


def waf_check():
    # simple WAF: block known SQLi patterns and long inputs
    data = request.args.to_dict(flat=True)
    for k, v in data.items():
        if len(v) > 1000:
            return jsonify({'blocked': 'input_too_long'}), 403
        for pat in BLACKLIST:
            if re.search(pat, v, flags=re.IGNORECASE):
                return jsonify({'blocked': 'waf_detected'}), 403
    return None
