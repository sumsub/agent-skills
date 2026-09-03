#!/usr/bin/env python3
"""Signed Sumsub ApplicantWorkflow API client — one CLI for every network step.

Subcommands (each signs with App Token + secret, HMAC-SHA256):

  state    <default|actions|test>      Show the current draft/published revisions
                                       of a workflow name and the right write mode.
  get      <id>                        Read one revision's full definition by id
                                       (e.g. to reuse node/edge ids when editing,
                                       or to back a draft up to a file).
  traffic  <id>                        Recent applicants on a revision's levels.
  validate [file|-]                    Dry-run validate a built payload (stores
                                       nothing). Reads stdin if no file.
  post     [file|-]                    Create/update a draft from a built payload.
  fork     <id>                        Fork a new draft from a published/archived
                                       revision (POST /{id}/draft).
  publish  <id> [published|archived|draft]
                                       Change a revision's status. GATED — see below.

Auth & environment (shared by all subcommands):
  SUMSUB_APP_TOKEN   sandbox App Token ('sbx:' prefix). Non-sandbox tokens are
                     refused unless SUMSUB_ALLOW_PROD=1.
  SUMSUB_SECRET_KEY  paired secret.
  SUMSUB_BASE        API base; default https://api.sumsub.com. Override only for
                     local/dev testing.

⚠️  publish affects LIVE production traffic. Workflow revisions are SHARED across
live and sandbox; only *applicants* are isolated. Publishing a `default`/`actions`
revision changes the workflow that handles real production verifications/actions —
a sandbox token does NOT make this safe.

`publish` is gated by the workflow's CURRENT LIVE EXPOSURE — the recent applicant
traffic on the revision that is currently `published` (the one this change would
auto-archive):
  • no published revision exists yet, OR its level traffic <= threshold
        -> proceeds unattended (low/zero exposure; no latch needed).
  • traffic > threshold, OR exposure cannot be determined (a list/traffic read
    fails) -> requires the arming latch  SUMSUB_ALLOW_WORKFLOW_PUBLISH=1
             (fail-safe: an unreadable exposure is treated as dangerous).
Threshold defaults to 400; override with SUMSUB_PUBLISH_TRAFFIC_THRESHOLD. The
count is LEVEL-derived (see the `traffic` subcommand) — how busy this workflow's
levels are now, not the blast radius of the new revision going live. `test` is not
publishable at all (the API rejects a revisionStatus change); the gate skips it
and defers to the API.

Output: each subcommand prints the response body, then a final `HTTP <code>` line
(except `state`, which prints a human summary). Gate decisions print to stderr.
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

WF_PATH = "/resources/api/agent/applicantWorkflows"


def die(msg, code) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(code)


def env():
    token = os.environ.get("SUMSUB_APP_TOKEN")
    secret = os.environ.get("SUMSUB_SECRET_KEY")
    if not token:
        die("error: SUMSUB_APP_TOKEN is required (sandbox App Token, 'sbx:' prefix)", 2)
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
    binary the test harness intercepts; signing and gating stay in Python."""
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
    if method != "GET":
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
    are left for the caller to read off the `HTTP <code>` line, matching the
    prior scripts' behavior."""
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

def cmd_state(args):
    code, body = request("GET", WF_PATH)
    if code != 200:
        print("error: list failed (HTTP {})".format(code), file=sys.stderr)
        print(body[:400], file=sys.stderr)
        sys.exit(4)
    items = json.loads(body).get("items") or []
    revs = [w for w in items if w.get("name") == args.name]
    draft = next((w for w in revs if w.get("revisionStatus") == "draft"), None)
    published = next((w for w in revs if w.get("revisionStatus") == "published"), None)
    line = lambda w: "none" if not w else "rev {}  id={}".format(w.get("revision"), w.get("id"))
    print("workflow name: ", args.name)
    print("draft:         ", line(draft))
    print("published:     ", line(published))
    if draft:
        print("WRITE MODE -> update-in-place: POST with id={} (overwrites the existing "
              "draft; CONFIRM with the user first). A no-id POST will 409.".format(draft.get("id")))
    elif published:
        print("WRITE MODE -> new draft: POST without id, OR fork from published id={} "
              "via POST /{{id}}/draft.".format(published.get("id")))
    else:
        print("WRITE MODE -> new draft: POST without id (no existing revisions).")


def cmd_get(args):
    code, body = request("GET", "{}/{}".format(WF_PATH, args.id))
    emit(code, body)


def cmd_fork(args):
    # POST /{id}/draft forks a new draft from a published/archived revision.
    code, body = request("POST", "{}/{}/draft".format(WF_PATH, args.id))
    emit(code, body)


def cmd_traffic(args):
    code, body = request("GET", "{}/{}/traffic".format(WF_PATH, args.id))
    emit(code, body)


def cmd_validate(args):
    payload = read_payload(args.file)
    try:
        d = json.loads(payload)
    except ValueError as e:
        die("error: payload is not valid JSON: {}".format(e), 2)
    # /-/validate accepts only {name, nodes, edges}.
    body = json.dumps({k: d[k] for k in ("name", "nodes", "edges") if k in d})
    code, resp = request("POST", WF_PATH + "/-/validate", body)
    emit(code, resp)


def cmd_post(args):
    payload = read_payload(args.file)
    code, resp = request("POST", WF_PATH, payload)
    emit(code, resp)


def assess_exposure(name, threshold):
    """Return (need_latch:bool, message:str) for a non-`test` workflow `name`.

    need_latch is True when current live exposure is over threshold OR can't be
    read (fail-safe); False when no published revision exists or traffic<=threshold."""
    code, body = request("GET", WF_PATH)
    if code != 200:
        return True, "could not list workflows to find the live revision (HTTP {}) — exposure unknown".format(code)
    try:
        items = json.loads(body).get("items") or []
    except ValueError:
        return True, "workflow list was not valid JSON — exposure unknown"
    pub = next((w for w in items
                if w.get("name") == name and w.get("revisionStatus") == "published"), None)
    if not pub:
        return False, "no published revision of '{}' exists yet (zero live exposure)".format(name)
    pub_id = pub.get("id")
    code, body = request("GET", "{}/{}/traffic".format(WF_PATH, pub_id))
    if code != 200:
        return True, "could not read live traffic for the published revision {} (HTTP {}) — exposure unknown".format(pub_id, code)
    try:
        cnt = json.loads(body).get("applicantCount")
    except ValueError:
        cnt = None
    if not isinstance(cnt, int):
        return True, "traffic response for {} had no integer applicantCount — exposure unknown".format(pub_id)
    rel = ">" if cnt > threshold else "<="
    msg = "the live revision (id {}) has {} recent applicants on its levels ({} {})".format(
        pub_id, cnt, rel, threshold)
    return cnt > threshold, msg


def cmd_publish(args):
    threshold = int(os.environ.get("SUMSUB_PUBLISH_TRAFFIC_THRESHOLD", "400"))
    # 1) Independently read the target to learn its NAME (do not trust the caller).
    code, body = request("GET", "{}/{}".format(WF_PATH, args.id))
    if code != 200:
        print("error: could not read workflow {} (HTTP {}); cannot determine safety. "
              "Aborting.".format(args.id, code), file=sys.stderr)
        print(body[:400], file=sys.stderr)
        sys.exit(4)
    info = json.loads(body)
    name, rev = info.get("name", ""), info.get("revision", "?")

    # 2) Exposure gate — everything except `test`.
    if name != "test":
        need_latch, gate_msg = assess_exposure(name, threshold)
        latched = os.environ.get("SUMSUB_ALLOW_WORKFLOW_PUBLISH") == "1"
        if need_latch and not latched:
            print(
                "REFUSING to set revisionStatus={} on workflow '{}' (revision {}, id {}).\n\n"
                "⚠️  This is a LIVE, traffic-intercepting workflow with meaningful current\n"
                "    exposure:\n      {}.\n"
                "    Workflow revisions are shared across live and sandbox — only applicants\n"
                "    are isolated — so changing its status with a sandbox token still affects\n"
                "    REAL production traffic.\n\n"
                "If you understand the consequences and intend to proceed, re-run with:\n"
                "    SUMSUB_ALLOW_WORKFLOW_PUBLISH=1 {} publish {} {}\n\n"
                "(Threshold is {} recent applicants; override with SUMSUB_PUBLISH_TRAFFIC_THRESHOLD.\n"
                "The 'test' workflow is exempt — but it is not publishable at all: the API\n"
                "rejects any revisionStatus change on it.)".format(
                    args.status, name or "<unknown>", rev, args.id, gate_msg,
                    sys.argv[0], args.id, args.status, threshold),
                file=sys.stderr)
            sys.exit(5)
        tail = "latch present — proceeding." if need_latch else "at/below threshold — proceeding unattended."
        print("exposure gate: {}; {}".format(gate_msg, tail), file=sys.stderr)

    # 3) Apply the status change.
    code, body = request("PUT", "{}/{}/revisionStatus".format(WF_PATH, args.id),
                         json.dumps({"revisionStatus": args.status}))
    emit(code, body)


def main():
    import argparse
    p = argparse.ArgumentParser(prog="workflow_api.py", description="Signed Sumsub ApplicantWorkflow API client.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("state", help="show current revisions + write mode for a workflow name")
    s.add_argument("name", choices=["default", "actions", "test"])
    s.set_defaults(fn=cmd_state)

    s = sub.add_parser("get", help="read one revision's full definition by id")
    s.add_argument("id")
    s.set_defaults(fn=cmd_get)

    s = sub.add_parser("fork", help="fork a new draft from a published/archived revision")
    s.add_argument("id")
    s.set_defaults(fn=cmd_fork)

    s = sub.add_parser("traffic", help="recent applicants on a revision's levels")
    s.add_argument("id")
    s.set_defaults(fn=cmd_traffic)

    s = sub.add_parser("validate", help="dry-run validate a built payload (stores nothing)")
    s.add_argument("file", nargs="?", default="-", help="payload file, or '-'/omitted for stdin")
    s.set_defaults(fn=cmd_validate)

    s = sub.add_parser("post", help="create/update a draft from a built payload")
    s.add_argument("file", nargs="?", default="-", help="payload file, or '-'/omitted for stdin")
    s.set_defaults(fn=cmd_post)

    s = sub.add_parser("publish", help="change a revision's status (GATED — see module docstring)")
    s.add_argument("id")
    s.add_argument("status", nargs="?", default="published", choices=["published", "archived", "draft"])
    s.set_defaults(fn=cmd_publish)

    args = p.parse_args()
    global ENV
    ENV = env()
    args.fn(args)


if __name__ == "__main__":
    main()
