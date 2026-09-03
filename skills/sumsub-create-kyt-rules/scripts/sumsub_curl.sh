#!/usr/bin/env bash
# Sign + send a single Sumsub API request.
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:... SUMSUB_SECRET_KEY=... \
#     sumsub_curl.sh METHOD PATH_WITH_QUERY [BODY_FILE_OR_-]
#
# Refuses non-sandbox tokens unless SUMSUB_ALLOW_PROD=1.
set -euo pipefail

if [[ $# -lt 2 ]]; then
  sed -n '2,12p' "$0" >&2
  exit 2
fi

METHOD="$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')"
PATH_Q="$2"
BODY_ARG="${3-}"

: "${SUMSUB_APP_TOKEN:?set SUMSUB_APP_TOKEN}"
: "${SUMSUB_SECRET_KEY:?set SUMSUB_SECRET_KEY}"
BASE="${SUMSUB_BASE:-https://api.sumsub.com}"

if [[ "${SUMSUB_APP_TOKEN}" != sbx:* && "${SUMSUB_ALLOW_PROD:-0}" != "1" ]]; then
  echo "error: SUMSUB_APP_TOKEN does not look like a sandbox token (expected 'sbx:' prefix)." >&2
  echo "       Production credentials must not be shared with this skill." >&2
  exit 3
fi

if [[ "${PATH_Q}" != /* ]]; then
  echo "error: PATH must start with '/'" >&2
  exit 2
fi

# Materialise the body to a temp file so we can sign the *exact* bytes we send.
BODY_FILE="$(mktemp)"
trap 'rm -f "${BODY_FILE}"' EXIT
if [[ -z "${BODY_ARG}" ]]; then
  : >"${BODY_FILE}"
elif [[ "${BODY_ARG}" == "-" ]]; then
  cat >"${BODY_FILE}"
else
  cp "${BODY_ARG}" "${BODY_FILE}"
fi

TS="$(date -u +%s)"

SIG="$(
  { printf '%s%s%s' "${TS}" "${METHOD}" "${PATH_Q}"; cat "${BODY_FILE}"; } \
    | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
    | awk '{print $NF}'
)"

CURL_ARGS=(
  -sS -X "${METHOD}"
  -H "X-App-Token: ${SUMSUB_APP_TOKEN}"
  -H "X-App-Access-Ts: ${TS}"
  -H "X-App-Access-Sig: ${SIG}"
  -H "X-Agent-Source: sumsub-skills"
  -H "X-Agent-Source-Ver: 1.4.1"
  -H "Accept: application/json"
)

# Only attach Content-Type + body for methods that send one.
if [[ -s "${BODY_FILE}" ]]; then
  CURL_ARGS+=(-H "Content-Type: application/json" --data-binary "@${BODY_FILE}")
fi

RESP_FILE="$(mktemp)"
trap 'rm -f "${BODY_FILE}" "${RESP_FILE}"' EXIT
HTTP_STATUS="$(curl "${CURL_ARGS[@]}" -w "%{http_code}" -o "${RESP_FILE}" "${BASE}${PATH_Q}")"
cat "${RESP_FILE}"
if [[ "${HTTP_STATUS}" -ge 400 ]]; then
  echo "HTTP ${HTTP_STATUS}" >&2
  exit 1
fi
