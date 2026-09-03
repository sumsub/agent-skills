#!/usr/bin/env bash
# Fetches tenant background-check entitlements from
# GET /resources/api/agent/settings/bgCheckTargets
# and returns JSON `{"allowedChecks": {key: label}}` — a map whose keys are
# the enabled entitlement keys.
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:...  SUMSUB_SECRET_KEY=...  bash check_permissions.sh
set -euo pipefail

: "${SUMSUB_APP_TOKEN:?SUMSUB_APP_TOKEN is required (sandbox App Token, 'sbx:' prefix)}"
: "${SUMSUB_SECRET_KEY:?SUMSUB_SECRET_KEY is required (paired secret key)}"
BASE="${SUMSUB_BASE:-https://api.sumsub.com}"

METHOD="GET"
PATH_Q="/resources/api/agent/settings/bgCheckTargets"
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
  -H "X-Agent-Source-Ver: 1.4.1" \
  -w '\nHTTP %{http_code}\n' \
  "${BASE%/}${PATH_Q}"
