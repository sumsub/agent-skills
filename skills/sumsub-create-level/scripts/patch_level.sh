#!/usr/bin/env bash
# PATCH an existing applicant level by id via the Sumsub API.
#
# The payload must include the level `id`. The server identifies the row by
# `id` and replaces the rest of the body.
#
# Authenticates via App Token + secret (HMAC-SHA256) per
# https://docs.sumsub.com/reference/authentication.
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:...  \
#   SUMSUB_SECRET_KEY=...     \
#   ./patch_level.sh /path/to/level-with-id.json
#
# Refuses non-sandbox tokens unless SUMSUB_ALLOW_PROD=1.
# Reads the level first; a company (KYB) level payload must pass
# `build_level.py --check --base <current> --levels` or it is not sent: exit 4.
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

if ! python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get("id") else 1)' "${PAYLOAD}"; then
  echo "error: payload is missing required \"id\" field for PATCH" >&2
  exit 2
fi

# A company (KYB) level is changed only as build_level.py --base builds it, with
# every associated party's verification level in place. Read the level first:
# that is what tells a company level (and a WebSDK 1.0 one) from the rest.
ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "${PAYLOAD}")"
"${SCRIPT_DIR}/get_level.sh" "${ID}" > "${WORK}/current.out"
if [[ "$(tail -n 1 "${WORK}/current.out")" != "HTTP 200" ]]; then
  echo "error: can't read level ${ID} before the PATCH:" >&2
  cat "${WORK}/current.out" >&2
  exit 4
fi
if sed '$d' "${WORK}/current.out" | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("applicantType") == "company" else 1)'; then
  "${SCRIPT_DIR}/list_levels.sh" > "${WORK}/levels.out"
  if ! python3 "${SCRIPT_DIR}/build_level.py" --check --base "${WORK}/current.out" --levels "${WORK}/levels.out" < "${PAYLOAD}"; then
    echo "refused: the company level was not changed (see the error above)" >&2
    exit 4
  fi
fi

METHOD="PATCH"
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
