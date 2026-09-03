#!/usr/bin/env python3
"""Print the three Sumsub auth headers for a request.

Usage:
    SUMSUB_APP_TOKEN=sbx:... SUMSUB_SECRET_KEY=... \
        sumsub_sign.py METHOD PATH_WITH_QUERY [BODY_FILE_OR_-]

Examples:
    sumsub_sign.py GET /resources/applicants/-/count
    sumsub_sign.py POST /resources/accessTokens?userId=u1&levelName=basic-kyc-level
    sumsub_sign.py POST /resources/api/agent/questionnaires payload.json
    cat payload.json | sumsub_sign.py POST /resources/api/agent/poaStepSettings -

Refuses to run when the App Token does not look like a sandbox token. Override
with SUMSUB_ALLOW_PROD=1 only if you know what you are doing — and never with
a credential the user has shared with an LLM.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import sys
import time
from pathlib import Path


def _sandbox_ok(token: str) -> bool:
    # Sumsub sandbox tokens begin with the literal "sbx:" prefix. Production
    # tokens use "prd:" or a bare identifier. We block anything that is not
    # clearly sandbox unless the operator has explicitly opted out.
    return token.startswith("sbx:")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2

    method = sys.argv[1].upper()
    path = sys.argv[2]
    body_arg = sys.argv[3] if len(sys.argv) > 3 else None

    token = os.environ.get("SUMSUB_APP_TOKEN", "").strip()
    secret = os.environ.get("SUMSUB_SECRET_KEY", "").strip()
    if not token or not secret:
        print("error: set SUMSUB_APP_TOKEN and SUMSUB_SECRET_KEY", file=sys.stderr)
        return 2

    if not _sandbox_ok(token) and os.environ.get("SUMSUB_ALLOW_PROD") != "1":
        print(
            "error: SUMSUB_APP_TOKEN does not look like a sandbox token (expected 'sbx:' prefix).\n"
            "       Production credentials must not be shared with this skill.\n"
            "       Rotate the token in the dashboard and use a sandbox one instead.",
            file=sys.stderr,
        )
        return 3

    if not path.startswith("/"):
        print("error: PATH must start with '/'", file=sys.stderr)
        return 2

    if body_arg is None:
        body = b""
    elif body_arg == "-":
        body = sys.stdin.buffer.read()
    else:
        body = Path(body_arg).read_bytes()

    ts = str(int(time.time()))
    signing = ts.encode() + method.encode() + path.encode() + body
    sig = hmac.new(secret.encode(), signing, hashlib.sha256).hexdigest()

    print(f"X-App-Token: {token}")
    print(f"X-App-Access-Ts: {ts}")
    print(f"X-App-Access-Sig: {sig}")
    print("X-Agent-Source: sumsub-skills")
    print("X-Agent-Source-Ver: 1.4.1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
