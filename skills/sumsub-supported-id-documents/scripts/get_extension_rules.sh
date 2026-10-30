#!/usr/bin/env bash
# GET Sumsub's built-in document expiry-EXTENSION rules (read-only reference).
# These describe how a document's validity is officially extended/interpreted per
# country/doc type (e.g. "owner 60+ valid indefinitely"). Not a client setting —
# you can't edit them; they back the 'officially extended documents' expiry modes.
#
# Authenticates via App Token + secret (HMAC-SHA256) per
# https://docs.sumsub.com/reference/authentication.
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:...  \
#   SUMSUB_SECRET_KEY=...     \
#   ./get_extension_rules.sh
#
# Refuses non-sandbox tokens unless SUMSUB_ALLOW_PROD=1.
set -euo pipefail

: "${SUMSUB_APP_TOKEN:?SUMSUB_APP_TOKEN is required (sandbox App Token, 'sbx:' prefix)}"
: "${SUMSUB_SECRET_KEY:?SUMSUB_SECRET_KEY is required (paired secret key)}"
BASE="${SUMSUB_BASE:-https://api.sumsub.com}"

if [[ "${SUMSUB_APP_TOKEN}" != sbx:* && "${SUMSUB_ALLOW_PROD:-0}" != "1" ]]; then
  echo "error: SUMSUB_APP_TOKEN does not look like a sandbox token (expected 'sbx:' prefix)." >&2
  echo "       Production credentials must not be shared with this skill." >&2
  exit 3
fi

METHOD="GET"
PATH_Q="/resources/api/agent/globalSettings/extensionRules"
TS="$(date -u +%s)"

SIG="$(
  printf '%s%s%s' "${TS}" "${METHOD}" "${PATH_Q}" \
    | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
    | awk '{print $NF}'
)"

BODY_FILE="$(mktemp)"
trap 'rm -f "${BODY_FILE}"' EXIT

HTTP_CODE="$(
  curl --compressed -sS -X "${METHOD}" \
    -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
    -H "X-App-Access-Ts: ${TS}" \
    -H "X-App-Access-Sig: ${SIG}" \
    -H "X-Agent-Source-Ver: 1.6.0" \
    -H "Accept: application/json" \
    -o "${BODY_FILE}" \
    -w '%{http_code}' \
    "${BASE%/}${PATH_Q}"
)"

if [[ "${HTTP_CODE}" -lt 200 || "${HTTP_CODE}" -ge 300 ]]; then
  echo "error: GET ${PATH_Q} returned HTTP ${HTTP_CODE}" >&2
  cat "${BODY_FILE}" >&2
  exit 4
fi

cat "${BODY_FILE}"
