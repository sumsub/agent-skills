#!/usr/bin/env bash
# Fetch the database check-sources Sumsub offers for a country and each
# source's enablement status for the current tenant.
#   GET /resources/api/agent/settings/checkSources?country=<country>
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:...  SUMSUB_SECRET_KEY=...  check_databases.sh [country]
#     [country] — ISO alpha-3 country code (e.g. DEU). Omit to return the full catalog.
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

# URL-encode the country. `country` is passed into BOTH the HMAC signature
# (PATH_Q below) and the request URL, so the two must be byte-identical. For a
# valid alpha-3 code (e.g. DEU) this is a no-op — but nothing enforces alpha-3,
# and the endpoint tolerates any value (unrecognized -> empty 200 list). If a
# caller passes a country *name* ("United States") the raw space/non-ASCII would
# make curl re-encode the URL, so the sent path would no longer match the signed
# path -> HTTP 401. Encoding here keeps signed == sent, so a bad country falls
# through to the documented empty-list behavior instead of a confusing auth error.
urlencode() {
  local s="$1" i c out=""
  for (( i=0; i<${#s}; i++ )); do
    c="${s:i:1}"
    case "$c" in
      [a-zA-Z0-9.~_-]) out+="$c" ;;
      *) printf -v c '%%%02X' "'$c"; out+="$c" ;;
    esac
  done
  printf '%s' "$out"
}

METHOD="GET"
PATH_Q="/resources/api/agent/settings/checkSources"
if [[ -n "${1:-}" ]]; then
  PATH_Q="${PATH_Q}?country=$(urlencode "$1")"
fi
TS="$(date -u +%s)"

SIG="$(
  printf '%s%s%s' "${TS}" "${METHOD}" "${PATH_Q}" \
    | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
    | awk '{print $NF}'
)"

curl -sS -X "${METHOD}" \
  -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
  -H "X-App-Access-Ts: ${TS}" \
  -H "X-App-Access-Sig: ${SIG}" \
  -H "Accept: application/json" \
  -H "X-Agent-Source: sumsub-skills" \
  -H "X-Agent-Source-Ver: 1.5.0" \
  -w '\nHTTP %{http_code}\n' \
  "${BASE%/}${PATH_Q}"
