#!/usr/bin/env bash
# POST a built ApplicantLevel payload to the Sumsub API.
#
# Authenticates via App Token + secret (HMAC-SHA256) per
# https://docs.sumsub.com/reference/authentication.
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:...  \
#   SUMSUB_SECRET_KEY=...     \
#   ./post_level.sh /path/to/level.json
#
# Refuses non-sandbox tokens unless SUMSUB_ALLOW_PROD=1.
# A company (KYB) level payload must pass `build_level.py --check --levels`
# (built by the builder, party levels exist) or it is not sent: exit 4.
# Override SUMSUB_BASE only for testing; default is https://api.sumsub.com.
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT
# Payload comes from $1 (file path), stdin if no arg, or "-" for explicit stdin.
PAYLOAD="${1:--}"
if [[ "${PAYLOAD}" == "-" ]]; then
  PAYLOAD="${WORK}/payload.json"
  cat > "${PAYLOAD}"
elif [[ ! -f "${PAYLOAD}" ]]; then
  echo "payload file not found: ${PAYLOAD}" >&2
  exit 2
fi
if [[ ! -s "${PAYLOAD}" ]]; then
  echo "error: payload is empty (no file content, or stdin closed without data)" >&2
  exit 2
fi

# A company (KYB) level goes out only as build_level.py builds it, with every
# associated party's verification level in place.
if python3 -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("applicantType") == "company" else 1)' "${PAYLOAD}" 2>/dev/null; then
  "${SCRIPT_DIR}/list_levels.sh" > "${WORK}/levels.out"
  if ! python3 "${SCRIPT_DIR}/build_level.py" --check --levels "${WORK}/levels.out" < "${PAYLOAD}"; then
    echo "refused: the company level was not sent (see the error above)" >&2
    exit 4
  fi
fi

METHOD="POST"
PATH_Q="/resources/applicants/-/levels"
TS="$(date -u +%s)"

SIG="$(
  { printf '%s%s%s' "${TS}" "${METHOD}" "${PATH_Q}"; cat "${PAYLOAD}"; } \
    | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
    | awk '{print $NF}'
)"

curl --compressed -sS -X "${METHOD}" \
  -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
  -H "X-App-Access-Ts: ${TS}" \
  -H "X-App-Access-Sig: ${SIG}" \
  -H "X-Agent-Source: sumsub-skills" \
  -H "X-Agent-Source-Ver: 1.6.0" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary "@${PAYLOAD}" \
  -w '\nHTTP %{http_code}\n' \
  "${BASE%/}${PATH_Q}"
