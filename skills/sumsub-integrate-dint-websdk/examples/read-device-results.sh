#!/usr/bin/env bash
# Read an applicant (including device risk labels) server-side.
# Device Intelligence enriches the same applicant object the base WebSDK flow
# already reads — there is no separate "device" call you must make to gate access.
#
# Auth: App Token + HMAC signature. Sandbox token only (sbx: prefix).
set -euo pipefail

: "${SUMSUB_APP_TOKEN:?set SUMSUB_APP_TOKEN (sbx:...)}"
: "${SUMSUB_SECRET_KEY:?set SUMSUB_SECRET_KEY}"
USER_ID="${1:?usage: read-device-results.sh <externalUserId>}"

case "$SUMSUB_APP_TOKEN" in
  sbx:*) ;;
  *) echo "refusing non-sandbox token; use an sbx: App Token for integration work" >&2; exit 1 ;;
esac

# Look up by your externalUserId via the matrix-param form. To read by the Sumsub
# applicant id instead, drop the "-;externalUserId=" prefix and pass the id directly:
#   PATH_Q="/resources/applicants/${USER_ID}/one"
PATH_Q="/resources/applicants/-;externalUserId=${USER_ID}/one"
TS=$(date -u +%s)
SIG=$(printf '%s%s%s' "$TS" "GET" "$PATH_Q" \
      | openssl dgst -sha256 -hmac "$SUMSUB_SECRET_KEY" -hex \
      | awk '{print $NF}')

curl -sS --fail-with-body \
  -H "X-App-Token: $SUMSUB_APP_TOKEN" \
  -H "X-App-Access-Ts: $TS" \
  -H "X-App-Access-Sig: $SIG" \
  -H "X-Agent-Source: sumsub-skills" \
  -H "X-Agent-Source-Ver: 1.4.1" \
  "https://api.sumsub.com${PATH_Q}"

# In the JSON, read review.reviewResult.reviewAnswer for the verdict and the
# applicant's risk labels for device signals. Full device detail (per-device
# history) is in the dashboard: applicant → Devices tab.
