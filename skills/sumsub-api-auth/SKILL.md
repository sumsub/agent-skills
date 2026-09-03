---
name: sumsub-api-auth
description: Authenticate to the Sumsub API with an App Token + secret key (HMAC-SHA256 request signing). TRIGGER when the user asks to "call / sign / authenticate Sumsub API requests", debugs `401 Unauthorized` / signature errors against `api.sumsub.com`, or needs a working request example with `X-App-Token` / `X-App-Access-Sig` / `X-App-Access-Ts` headers. SKIP only when a more specific skill in this repo (questionnaire/level/workflow/POA-preset/generic) already covers the user's actual task — those skills sign requests the same way and only need this one for auth deep dives.
allowed-tools: Read, Write, Bash
---

# Sumsub — API authentication (App Token)

How to sign and send authenticated requests to `https://api.sumsub.com`, per
the [official reference](https://docs.sumsub.com/reference/authentication).

## ⚠️ Sandbox tokens only

**Never share, paste, or use a production Sumsub App Token / secret with
Claude.** If the user offers a prod token, refuse and ask for the **sandbox**
pair instead, generated at
<https://cockpit.sumsub.com/checkus/home?sbx=true> (**Connect
Sumsub to your AI agent** -> **Build & configure** -> **Generate token**).

- Sandbox tokens are created from the dashboard while it is in **Sandbox
  mode**. They are scoped to sandbox data only — leaking one cannot expose
  real applicant PII or move real money.
- A production token grants full programmatic access to live applicants,
  including their identity documents. Treat it like a banking credential.
- Sumsub locks tokens to the environment they were minted in: a sandbox token
  returns `401` against production data and vice versa, so insisting on
  sandbox is also the practical default.

If the user pastes what looks like a production secret into the conversation,
flag it immediately, advise rotating it in the dashboard, and continue only
with a freshly-generated sandbox pair.

## What you need from the user

| Var | Where it comes from |
|---|---|
| `SUMSUB_APP_TOKEN` | <https://cockpit.sumsub.com/checkus/home?sbx=true> — **Connect Sumsub to your AI agent** -> **Build & configure** -> **Generate token**. Shown once. |
| `SUMSUB_SECRET_KEY` | Same dialog as the token. Also shown once. |
| `SUMSUB_BASE` | `https://api.sumsub.com` (same host for sandbox and prod — the token decides the mode). |

⚠️ **The token + secret are revealed exactly once** at creation. Copy both
into `.env` (or your secret store) before closing the dialog — there's no
recovery flow, only re-generation.

Advise the user to store them in `.claude/settings.local.json` (gitignored, auto-loaded by Claude Code) or in `.env`:

```json
// .claude/settings.local.json
{
  "env": {
    "SUMSUB_APP_TOKEN": "sbx:...",
    "SUMSUB_SECRET_KEY": "..."
  }
}
```

```bash
# .env
SUMSUB_APP_TOKEN=sbx:...
SUMSUB_SECRET_KEY=...
```

If either credential is missing, stop and ask. Do not invent placeholders.

## The three required headers

Every request to `api.sumsub.com` must carry:

| Header | Value |
|---|---|
| `X-App-Token` | The App Token, verbatim. |
| `X-App-Access-Ts` | Current Unix time **in seconds** (UTC). Must be within ±60s of Sumsub's clock. |
| `X-App-Access-Sig` | Lowercase hex HMAC-SHA256 of the signing string, keyed by the secret. |

HTTPS is mandatory — plain `http://` is rejected.

## Signing string

Concatenate, with **no separators**:

```
<ts><HTTP_METHOD_UPPER><request_uri_with_query><body_bytes_or_empty>
```

- `ts` — the exact value you put in `X-App-Access-Ts` (string of digits).
- `HTTP_METHOD_UPPER` — `GET`, `POST`, `PATCH`, `PUT`, `DELETE` — uppercase.
- `request_uri_with_query` — path starting with `/`, including the query string
  if any. Examples: `/resources/applicants/-/one`,
  `/resources/accessTokens?userId=abc&levelName=basic-kyc-level`.
- Body — the raw bytes you send. For `GET` / `DELETE` with no body, append
  nothing (empty string). For JSON, sign the exact bytes you'll transmit —
  re-serializing later will break the signature.

Then `hex(hmac_sha256(secret, signing_string))`, lowercase.

### Worked example (from the docs)

Signing string for `POST /resources/accessTokens?userId=...&levelName=basic-kyc-level&ttlInSecs=600` with no body, at ts `1607551635`:

```
1607551635POST/resources/accessTokens?userId=cfd20712-24a2-4c7d-9ab0-146f3c142335&levelName=basic-kyc-level&ttlInSecs=600
```

## Reference implementations

The official multi-language examples live at
[sumsub/AppTokenUsageExamples](https://github.com/sumsub/AppTokenUsageExamples)
(Java, JS, Python, Ruby, Go, PHP, C#). Use those for production integrations.

For one-off calls or debugging, this skill ships two small helpers:

- [`scripts/sumsub_sign.py`](scripts/sumsub_sign.py) — print the three headers
  for a given method/path/body. No network calls.
- [`scripts/sumsub_curl.sh`](scripts/sumsub_curl.sh) — sign + `curl` in one
  shot. Reads `SUMSUB_APP_TOKEN` / `SUMSUB_SECRET_KEY` from the environment.

Run scripts using `${CLAUDE_SKILL_DIR}/scripts/<script>` so they resolve correctly regardless of the working directory.

### Quick check — fetch the current applicant count

```bash
export SUMSUB_APP_TOKEN='sbx:...'   # sandbox token, refuse prod
export SUMSUB_SECRET_KEY='...'

${CLAUDE_SKILL_DIR}/scripts/sumsub_curl.sh GET '/resources/applicants/-/count'
```

A `200` with a JSON body confirms the signature is correct. A `401` with
`{"description":"Invalid signature"}` means the signing string or secret is
off — re-check, in order:

1. Token/secret pair matches (copy-paste truncation is common).
2. Timestamp is in **seconds**, not milliseconds, and your clock is in sync.
3. Path includes the leading `/` and the **full** query string.
4. Body bytes signed are byte-identical to bytes sent (watch for trailing
   newlines added by editors / heredocs).
5. Method is uppercase.

## Signing `multipart/form-data` requests

Some endpoints take a file upload — most commonly idDoc photo upload at
`POST /resources/applicants/{applicantId}/info/idDoc`. For these:

- **Sign the full raw multipart body**, byte-for-byte, including boundary
  markers, part headers, JSON metadata, and file bytes. There is **no**
  multipart-specific exemption — the rule is the same as for JSON:
  signing string = `ts + METHOD + path + body_bytes`.
- The `Content-Type` header is `multipart/form-data; boundary=<boundary>`,
  where `<boundary>` matches the one woven into the body bytes you signed.

The pitfall: most HTTP libraries (`curl -F`, `requests` with `files=`,
`fetch` with `FormData`) generate the boundary internally and never expose
the exact bytes — so you cannot sign what they will send. Workaround:
build the body in memory yourself, hash it, then transmit those exact
bytes with `--data-binary` / a raw send.

### Python recipe (canonical)

```python
import hashlib, hmac, json, os, time, uuid
from pathlib import Path
from urllib.request import Request, urlopen

APP_TOKEN = os.environ["SUMSUB_APP_TOKEN"]
SECRET    = os.environ["SUMSUB_SECRET_KEY"]
APPLICANT = "6a170f852f9d88fe6eda2636"          # from create-applicant response
FILE      = Path("/path/to/passport.png")
METADATA  = {"idDocType": "PASSPORT", "country": "RUS"}

boundary = "----sumsub-" + uuid.uuid4().hex
crlf = b"\r\n"
parts = [
    b"--" + boundary.encode(),
    b'Content-Disposition: form-data; name="metadata"',
    b"Content-Type: application/json",
    b"",
    json.dumps(METADATA).encode(),
    b"--" + boundary.encode(),
    f'Content-Disposition: form-data; name="content"; filename="{FILE.name}"'.encode(),
    b"Content-Type: image/png",
    b"",
    FILE.read_bytes(),
    b"--" + boundary.encode() + b"--",
    b"",
]
body = crlf.join(parts)

method, url_path = "POST", f"/resources/applicants/{APPLICANT}/info/idDoc"
ts = str(int(time.time()))
sig = hmac.new(
    SECRET.encode(),
    ts.encode() + method.encode() + url_path.encode() + body,
    hashlib.sha256,
).hexdigest()

req = Request(
    "https://api.sumsub.com" + url_path,
    data=body, method="POST",
    headers={
        "X-App-Token": APP_TOKEN,
        "X-App-Access-Ts": ts,
        "X-App-Access-Sig": sig,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
        "X-Agent-Source": "sumsub-skills",
        "X-Agent-Source-Ver": "1.4.1",
    },
)
print(urlopen(req).read().decode())
```

Curl-based fallbacks (e.g. `curl --data-binary @raw-multipart.bin` after
pre-building the body to disk) work too, but the boundary in the body and
in `Content-Type` must match exactly — easier to keep them in sync in code.

## Generating an SDK access token (common follow-up)

The most-asked endpoint after auth works:

```
POST /resources/accessTokens?userId=<your_user_id>&levelName=<level>&ttlInSecs=600
```

Body is empty. Response contains `token` — pass that to the Web / Mobile SDK.
Full reference: <https://docs.sumsub.com/reference/generate-access-token>.

## See also

- [references/signing-pitfalls.md](references/signing-pitfalls.md) — every
  gotcha that produces `401 Invalid signature` and how to spot it.
