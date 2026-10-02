#!/usr/bin/env bash
# PUT the FULL countryMappings payload — REPLACES the whole map.
#
#   PUT /resources/api/agent/globalSettings/idDocSettings/countryMappings
#
# The single write path of this skill: edits send the complete map built by
# build_country_mappings.py (current settings + merged changes), removals send
# the map built by remove_country_mapping.py. Anything omitted is wiped, so
# never send a hand-crafted partial map here.
#
# Authenticates via App Token + secret (HMAC-SHA256) per
# https://docs.sumsub.com/reference/authentication.
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:...  \
#   SUMSUB_SECRET_KEY=...     \
#   ./put_country_mappings.sh <payload.json>
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

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <payload.json>" >&2
  exit 2
fi

PAYLOAD_FILE="$1"
if [[ ! -f "${PAYLOAD_FILE}" ]]; then
  echo "error: payload file not found: ${PAYLOAD_FILE}" >&2
  exit 2
fi

METHOD="PUT"
PATH_Q="/resources/api/agent/globalSettings/idDocSettings/countryMappings"
TS="$(date -u +%s)"
BODY="$(cat "${PAYLOAD_FILE}")"

# Signature covers ts + method + path + raw body, per Sumsub HMAC spec.
SIG="$(
  printf '%s%s%s%s' "${TS}" "${METHOD}" "${PATH_Q}" "${BODY}" \
    | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
    | awk '{print $NF}'
)"

curl -sS -X "${METHOD}" \
  -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
  -H "X-App-Access-Ts: ${TS}" \
  -H "X-App-Access-Sig: ${SIG}" \
  -H "X-Agent-Source-Ver: 1.5.0" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data-binary "${BODY}" \
  -w '\nHTTP %{http_code}\n' \
  "${BASE%/}${PATH_Q}"
