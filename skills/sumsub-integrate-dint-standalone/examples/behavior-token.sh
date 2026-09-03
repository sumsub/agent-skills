#!/usr/bin/env bash
# Mint a Device Intelligence "behavior" access token for the standalone flow.
# This is the token your page passes to @sumsub/fisherman init().
#
# Differs from the WebSDK access-token recipe in two ways:
#   1. endpoint is /resources/accessTokens/behavior
#   2. there IS a JSON body, so the body MUST be included in the signature
#      (sign: ts + "POST" + path + body)
#
# Auth: App Token + HMAC. Sandbox token only (sbx: prefix).
set -euo pipefail

: "${SUMSUB_APP_TOKEN:?set SUMSUB_APP_TOKEN (sbx:...)}"
: "${SUMSUB_SECRET_KEY:?set SUMSUB_SECRET_KEY}"
SESSION_ID="${1:?usage: behavior-token.sh <sessionId> [ttlInSecs]}"
TTL="${2:-1800}"

case "$SUMSUB_APP_TOKEN" in
  sbx:*) ;;
  *) echo "refusing non-sandbox token; use an sbx: App Token for integration work" >&2; exit 1 ;;
esac

PATH_Q="/resources/accessTokens/behavior"
# Escape " and \ so a session id containing them can't break out of / inject into the
# JSON body (which gets signed and sent as-is). Pure bash, no extra deps; an exotic
# control char would still yield a harmless 400, never injection.
esc() { local s=$1; s=${s//\\/\\\\}; s=${s//\"/\\\"}; printf '%s' "$s"; }
# ttlInSecs is a bare JSON number — validate it rather than string-escaping, else a
# value like '1800}...' would inject structure.
[[ "$TTL" =~ ^[0-9]+$ ]] || { echo "ttlInSecs must be a positive integer" >&2; exit 1; }
BODY=$(printf '{"sessionId":"%s","ttlInSecs":%s}' "$(esc "$SESSION_ID")" "$TTL")
TS=$(date -u +%s)

# IMPORTANT: body is part of the signed string for POSTs with a body.
SIG=$(printf '%s%s%s%s' "$TS" "POST" "$PATH_Q" "$BODY" \
      | openssl dgst -sha256 -hmac "$SUMSUB_SECRET_KEY" -hex \
      | awk '{print $NF}')

curl -sS --fail-with-body -X POST \
  -H "Content-Type: application/json" \
  -H "X-App-Token: $SUMSUB_APP_TOKEN" \
  -H "X-App-Access-Ts: $TS" \
  -H "X-App-Access-Sig: $SIG" \
  -H "X-Agent-Source: sumsub-skills" \
  -H "X-Agent-Source-Ver: 1.4.1" \
  --data "$BODY" \
  "https://api.sumsub.com${PATH_Q}"

# Response: { "token": "_act-jwt-..." }  (behavior tokens carry no userId)  -> return .token to the browser.
