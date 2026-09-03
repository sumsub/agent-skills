#!/usr/bin/env bash
# POST a built cross-check preset payload to the Sumsub API.
#
# The payload must NOT contain `id` — that's assigned by the server.
# For updates use patch_cross_check_preset.sh instead.
#
# Authenticates via App Token + secret (HMAC-SHA256) per
# https://docs.sumsub.com/reference/authentication.
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:...  \
#   SUMSUB_SECRET_KEY=...     \
#   ./post_cross_check_preset.sh /path/to/preset.json
#
# Refuses non-sandbox tokens unless SUMSUB_ALLOW_PROD=1.
#
# Prints the response body followed by a final line: HTTP <code>
set -euo pipefail

: "${SUMSUB_APP_TOKEN:?SUMSUB_APP_TOKEN is required (sandbox App Token, 'sbx:' prefix)}"
: "${SUMSUB_SECRET_KEY:?SUMSUB_SECRET_KEY is required (paired secret key)}"
BASE="${SUMSUB_BASE:-https://api.sumsub.com}"

if [[ "${SUMSUB_APP_TOKEN}" != sbx:* && "${SUMSUB_ALLOW_PROD:-0}" != "1" ]]; then
  echo "error: SUMSUB_APP_TOKEN does not look like a sandbox token (expected 'sbx:' prefix)." >&2
  echo "       Production credentials must not be shared with this skill." >&2
  exit 3
fi

# Payload comes from $1 (file path), stdin if no arg, or "-" for explicit stdin.
PAYLOAD="${1:--}"
if [[ "${PAYLOAD}" == "-" ]]; then
  PAYLOAD="$(mktemp)"
  trap 'rm -f "${PAYLOAD}"' EXIT
  cat > "${PAYLOAD}"
elif [[ ! -f "${PAYLOAD}" ]]; then
  echo "payload file not found: ${PAYLOAD}" >&2
  exit 2
fi
if [[ ! -s "${PAYLOAD}" ]]; then
  echo "error: payload is empty (no file content, or stdin closed without data)" >&2
  exit 2
fi

if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get("id") else 1)' "${PAYLOAD}"; then
  echo "error: payload contains \"id\" — use patch_cross_check_preset.sh for updates." >&2
  exit 2
fi

METHOD="POST"
PATH_Q="/resources/api/agent/crossCheckPresets"
TS="$(date -u +%s)"

SIG="$(
  { printf '%s%s%s' "${TS}" "${METHOD}" "${PATH_Q}"; cat "${PAYLOAD}"; } \
    | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
    | awk '{print $NF}'
)"

curl -sS -X "${METHOD}" \
  -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
  -H "X-App-Access-Ts: ${TS}" \
  -H "X-App-Access-Sig: ${SIG}" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Source: sumsub-skills" \
  -H "X-Agent-Source-Ver: 1.4.1" \
  --data-binary "@${PAYLOAD}" \
  -w '\nHTTP %{http_code}\n' \
  "${BASE%/}${PATH_Q}"
