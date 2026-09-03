#!/usr/bin/env python3
"""Signed Sumsub AML Resolution Rules API client — one CLI for every network step.

Subcommands (each signs with App Token + secret, HMAC-SHA256):

  draft                         Get the draft revision of the rule chain (the
                                editable one; auto-created on first access).
                                Carries the current `notices[]` — read after
                                every change.
  published                     Get the live (published) revision (404 if none).
  archive  [forwardMarker]      List archived revisions (10/page, newest first).
                                Pass the previous response's forwardMarker for
                                the next page. Heavily rate-limited (5/min).
  library                       Get the ready-made rule templates.
  upsert   [file|-]             Create/update one rule from a built payload
                                (POST /draft/rules). Omit `id` in the payload to
                                create; include it to replace that rule.
  reorder  [file|-]             Set the evaluation order: body {"ruleIds":[...]}
                                — a complete permutation of every draft rule id.
  delete   <ruleId>             Remove one rule from the draft by id (idempotent).
                                See the consent policy in SKILL.md before deleting
                                a rule you didn't create.
  publish                       Publish the draft (POST /draft/publish). Makes it
                                the live rule chain; the prior published revision
                                auto-archives. Refused while the draft has any
                                error-level notice. Only on explicit user request.

⚠️  publish affects LIVE production behavior. The AML Resolution Rule Chain is
SHARED across live and sandbox — only the AML cases/applicants are isolated — so
publishing with a sandbox token still makes the chain auto-review REAL production
AML screening hits (clearing false positives, confirming true positives,
whitelisting). The backend may REFUSE the publish once the chain is active (too
many applicants already processed / the integration is complete) — that is
expected, not an error to work around: report it and tell the user to publish from
the Sumsub web UI.

Auth & environment (shared by all subcommands):
  SUMSUB_APP_TOKEN   sandbox App Token ('sbx:' prefix), and AI-purpose — these are
                     agent endpoints. Non-sandbox tokens are refused unless
                     SUMSUB_ALLOW_PROD=1.
  SUMSUB_SECRET_KEY  paired secret.
  SUMSUB_BASE        API base; default https://api.sumsub.com. Override only for
                     local/dev testing.

Failure modes worth recognizing:
  • 404 "API is not available"  -> the AML Resolution Rules API is not enabled for
    this tenant. Stop; contact CSM/Sumsub support. Do not retry other endpoints.
  • 403 "This endpoint is not allowed for this type of token" -> the App Token is
    not AI-purpose. Mint an AI token in the dashboard.
  • publish 4xx when the chain is active -> publishing via the API is refused once
    there are already too many applicants / the integration is complete; the chain
    must then be reviewed and published manually from the Sumsub web UI.

Output: each subcommand prints the response body, then a final `HTTP <code>` line.
"""
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import time
from typing import NoReturn
from urllib.parse import quote, urlencode

AML_PATH = "/resources/api/agent/amlResolutionRules"


def die(msg, code) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(code)


def env():
    token = os.environ.get("SUMSUB_APP_TOKEN")
    secret = os.environ.get("SUMSUB_SECRET_KEY")
    if not token:
        die("error: SUMSUB_APP_TOKEN is required (sandbox AI App Token, 'sbx:' prefix)", 2)
    if not secret:
        die("error: SUMSUB_SECRET_KEY is required (paired secret key)", 2)
    if not token.startswith("sbx:") and os.environ.get("SUMSUB_ALLOW_PROD") != "1":
        die("error: SUMSUB_APP_TOKEN does not look like a sandbox token (expected 'sbx:' "
            "prefix).\n       Production credentials must not be shared with this skill.", 3)
    base = os.environ.get("SUMSUB_BASE", "https://api.sumsub.com").rstrip("/")
    return token, secret, base


def request(method, path, body: "bytes | str" = b""):
    """Signed request via curl. Returns (http_status:int, body:str). status 0 = network error.

    Signature payload is ts + method + path + body (the form the API expects).
    The HTTP transport is `curl` (not urllib) so the request goes through the same
    binary the test harness intercepts; signing stays in Python."""
    token, secret, base = ENV
    if isinstance(body, str):
        body = body.encode()
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode(), ts.encode() + method.encode() + path.encode() + body,
                   hashlib.sha256).hexdigest()
    headers = {
        "X-App-Token": token,
        "X-App-Access-Ts": ts,
        "X-App-Access-Sig": sig,
        "X-Agent-Source": "sumsub-skills",
        "X-Agent-Source-Ver": "1.4.1",
        "Accept": "application/json",
    }
    # `-w '\nHTTP %{http_code}\n'` appends the status as a trailing line so we can
    # read it back off stdout (curl's exit code alone doesn't carry 4xx/5xx).
    cmd = ["curl", "-sS", "-X", method, base + path, "-w", "\nHTTP %{http_code}\n"]
    for k, v in headers.items():
        cmd += ["-H", "{}: {}".format(k, v)]
    if method not in ("GET", "DELETE"):
        cmd += ["-H", "Content-Type: application/json",
                "--data-binary", body.decode("utf-8", "replace")]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return 0, "network error: curl not found on PATH"
    out = proc.stdout
    m = re.search(r"\nHTTP (\d+)\n?\Z", out)
    if not m:
        return 0, "network error: {}".format(
            (proc.stderr or out).strip() or "no HTTP status line from curl")
    code = int(m.group(1))
    if code == 0:  # curl emitted %{http_code}=000 — connection never completed
        return 0, "network error: {}".format(
            (proc.stderr or "").strip() or "curl reported HTTP 000")
    return code, out[:m.start()]


def emit(code, body):
    """Print response body then the trailing `HTTP <code>` line.

    Exits non-zero on a transport failure (code 0); HTTP error statuses (4xx/5xx)
    are left for the caller to read off the `HTTP <code>` line."""
    sys.stdout.write(body)
    if not body.endswith("\n"):
        sys.stdout.write("\n")
    print("HTTP {}".format(code))
    if code == 0:
        sys.exit(1)


def read_payload(arg):
    if arg in (None, "-"):
        data = sys.stdin.buffer.read()
    elif os.path.isfile(arg):
        with open(arg, "rb") as f:
            data = f.read()
    else:
        die("payload file not found: {}".format(arg), 2)
    if not data.strip():
        die("error: payload is empty (no file content, or stdin closed without data)", 2)
    return data


# ── subcommands ───────────────────────────────────────────────────────────────

def cmd_draft(args):
    emit(*request("GET", AML_PATH + "/draft"))


def cmd_published(args):
    emit(*request("GET", AML_PATH + "/published"))


def cmd_archive(args):
    path = AML_PATH + "/archive"
    if args.forward_marker:
        path += "?" + urlencode({"forwardMarker": args.forward_marker})
    emit(*request("GET", path))


def cmd_library(args):
    emit(*request("GET", AML_PATH + "/library"))


def cmd_upsert(args):
    payload = read_payload(args.file)
    emit(*request("POST", AML_PATH + "/draft/rules", payload))


def cmd_reorder(args):
    payload = read_payload(args.file)
    try:
        json.loads(payload)
    except ValueError as e:
        die("error: payload is not valid JSON: {}".format(e), 2)
    emit(*request("PUT", AML_PATH + "/draft/rules/order", payload))


def cmd_delete(args):
    # Idempotent: deleting a rule not in the draft still succeeds.
    emit(*request("DELETE", "{}/draft/rules/{}".format(AML_PATH, quote(args.rule_id, safe=""))))


def cmd_publish(args):
    # The backend enforces publish safety (it refuses once the chain is active /
    # too many applicants have been processed), so this is a thin POST; the agent
    # surfaces a refusal and points the user to the web UI. Only run on explicit
    # user request (see SKILL.md).
    emit(*request("POST", AML_PATH + "/draft/publish"))


def main():
    import argparse
    p = argparse.ArgumentParser(prog="aml_rules_api.py",
                                description="Signed Sumsub AML Resolution Rules API client.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("draft", help="get the draft revision (with notices)").set_defaults(fn=cmd_draft)
    sub.add_parser("published", help="get the live revision (404 if none)").set_defaults(fn=cmd_published)

    s = sub.add_parser("archive", help="list archived revisions (paginated, 5/min)")
    s.add_argument("forward_marker", nargs="?", default=None, help="marker from the previous page")
    s.set_defaults(fn=cmd_archive)

    sub.add_parser("library", help="get the ready-made rule templates").set_defaults(fn=cmd_library)

    s = sub.add_parser("upsert", help="create/update one rule from a built payload")
    s.add_argument("file", nargs="?", default="-", help="rule payload file, or '-'/omitted for stdin")
    s.set_defaults(fn=cmd_upsert)

    s = sub.add_parser("reorder", help="set evaluation order: {\"ruleIds\":[...]} (full permutation)")
    s.add_argument("file", nargs="?", default="-", help="payload file, or '-'/omitted for stdin")
    s.set_defaults(fn=cmd_reorder)

    s = sub.add_parser("delete", help="remove one rule from the draft by id (idempotent)")
    s.add_argument("rule_id")
    s.set_defaults(fn=cmd_delete)

    sub.add_parser("publish", help="publish the draft (live; only on explicit request)").set_defaults(fn=cmd_publish)

    args = p.parse_args()
    global ENV
    ENV = env()
    args.fn(args)


if __name__ == "__main__":
    main()
