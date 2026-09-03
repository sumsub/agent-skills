#!/usr/bin/env bash
# POST a KytTxnData payload to the Sumsub transaction-monitoring endpoint.
#
# Authenticates via App Token + secret (HMAC-SHA256) per
# https://docs.sumsub.com/reference/authentication.
#
# Usage (two-step: build then post; the build emits a sidecar route file):
#
#   SUMSUB_TXN_ROUTE_FILE=/tmp/route.json \
#     python3 build_transaction.py < spec.json > /tmp/txn.json
#
#   SUMSUB_APP_TOKEN=sbx:...  \
#   SUMSUB_SECRET_KEY=...     \
#   SUMSUB_TXN_ROUTE_FILE=/tmp/route.json \
#     ./post_transaction.sh /tmp/txn.json
#
# Route selection (read from $SUMSUB_TXN_ROUTE_FILE):
#   applicantId set       -> POST /resources/applicants/{applicantId}/kyt/txns/-/data
#   levelName set         -> POST /resources/applicants/-/kyt/txns/-/data?levelName=<levelName>
#   neither               -> error (you must pick a routing mode in the spec)
#
# Refuses non-sandbox tokens unless SUMSUB_ALLOW_PROD=1.
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

ROUTE_FILE="${SUMSUB_TXN_ROUTE_FILE:-}"
if [[ -z "${ROUTE_FILE}" || ! -f "${ROUTE_FILE}" ]]; then
  echo "SUMSUB_TXN_ROUTE_FILE must point to the sidecar route file written by build_transaction.py" >&2
  exit 2
fi

# Parse the route file with python (no jq dependency).
APPLICANT_ID="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('applicantId') or '')" "${ROUTE_FILE}")"
LEVEL_NAME="$(python3   -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('levelName')   or '')" "${ROUTE_FILE}")"

if [[ -n "${APPLICANT_ID}" ]]; then
  # URL-encode the applicantId in case it contains awkward chars; in practice
  # it's a Mongo ObjectId hex string, but encode anyway so signing matches the
  # wire form exactly.
  ENCODED_APP_ID="$(python3 -c "import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=''))" "${APPLICANT_ID}")"
  PATH_Q="/resources/applicants/${ENCODED_APP_ID}/kyt/txns/-/data"
elif [[ -n "${LEVEL_NAME}" ]]; then
  ENCODED_LEVEL="$(python3 -c "import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=''))" "${LEVEL_NAME}")"
  PATH_Q="/resources/applicants/-/kyt/txns/-/data?levelName=${ENCODED_LEVEL}"
else
  echo "route file has neither applicantId nor levelName — set _applicantId or _levelName in the spec" >&2
  exit 2
fi

METHOD="POST"
TS="$(date -u +%s)"

# Signing string = ts + METHOD + path?query + body  (raw payload bytes).
SIG="$(
  { printf '%s%s%s' "${TS}" "${METHOD}" "${PATH_Q}"; cat "${PAYLOAD}"; } \
    | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
    | awk '{print $NF}'
)"

curl -sS -X "${METHOD}" \
  -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
  -H "X-App-Access-Ts: ${TS}" \
  -H "X-App-Access-Sig: ${SIG}" \
  -H "X-Agent-Source: sumsub-skills" \
  -H "X-Agent-Source-Ver: 1.4.1" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary "@${PAYLOAD}" \
  -w '\nHTTP %{http_code}\n' \
  "${BASE%/}${PATH_Q}"
