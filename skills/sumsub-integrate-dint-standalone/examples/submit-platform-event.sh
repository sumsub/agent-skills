#!/usr/bin/env bash
# Confirm an applicant platform event (login / signup / password reset / 2FA)
# with the captured device, so Sumsub runs Device Intelligence analysis on it.
#
# Auth: App Token + HMAC signing (sign ts + "POST" + path + body, where path
# INCLUDES the ?accessToken= query string), PLUS the BEHAVIOR access token (the
# same one used to init Fisherman) carried as the ?accessToken= query param. The
# behavior token does NOT replace signing — it rides alongside it so Sumsub can
# tie the captured device to this event. Sandbox App Token only (sbx: prefix).
#
# Body = KytTxnData with type "userPlatformEvent". Reference:
#   https://docs.sumsub.com/reference/send-applicant-platform-event-with-captured-device
#
# CORRELATION: Sumsub correlates the captured device to this event server-side
# using the session the behavior token was minted with (reconstructed from your
# externalUserId) — do NOT put a visitorId or device block in the body on the
# default flow.
set -euo pipefail

: "${SUMSUB_APP_TOKEN:?set SUMSUB_APP_TOKEN (sbx:...)}"
: "${SUMSUB_SECRET_KEY:?set SUMSUB_SECRET_KEY}"
ACCESS_TOKEN="${1:?usage: submit-platform-event.sh <behaviorAccessToken> <externalUserId> [eventType]}"
EXTERNAL_USER_ID="${2:?missing externalUserId}"
EVENT_TYPE="${3:-login}"   # login | failedLogin | signup | passwordReset | twoFaReset | general

case "$SUMSUB_APP_TOKEN" in
  sbx:*) ;;
  *) echo "refusing non-sandbox token; use an sbx: App Token for integration work" >&2; exit 1 ;;
esac

# The behavior token is an _act- token, not an sbx:/prd: App Token, so there is
# no prefix to gate on — but the call still hits whatever workspace the token
# belongs to. Use a SANDBOX behavior token during integration work.
echo "note: this fires against the workspace your behavior token belongs to — use a sandbox token while integrating" >&2

# _act- behavior tokens are base64url-encoded and contain no URL-unsafe chars, so no
# percent-encoding needed here. If your token format ever changes, wrap in $(python3 -c
# "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$ACCESS_TOKEN").
PATH_Q="/resources/applicants/-/kyt/txns/-/data?accessToken=${ACCESS_TOKEN}"

# Escape " and \ in the string fields so a value containing them can't break out of /
# inject into the JSON body. Pure bash, no extra deps; an exotic control char would
# still yield a harmless 400, never injection. (txnId is a uuid we generate ourselves.)
esc() { local s=$1; s=${s//\\/\\\\}; s=${s//\"/\\\"}; printf '%s' "$s"; }
EXTERNAL_USER_ID=$(esc "$EXTERNAL_USER_ID")
EVENT_TYPE=$(esc "$EVENT_TYPE")
# type=userPlatformEvent; applicant.externalUserId identifies the user;
# userPlatformEventInfo.type is the action. txnId is REQUIRED — a unique id you
# generate (here evt-<uuid>); omitting it is rejected with 422 "txnId must not be
# null". Optional: userPlatformEventInfo.passwordHash, userPlatformEventInfo.twoFaUsed.
BODY=$(cat <<JSON
{
  "txnId": "evt-$(uuidgen | tr '[:upper:]' '[:lower:]')",
  "type": "userPlatformEvent",
  "applicant": { "externalUserId": "${EXTERNAL_USER_ID}", "type": "individual" },
  "userPlatformEventInfo": { "type": "${EVENT_TYPE}" }
}
JSON
)

# App-Token + HMAC: the signed path INCLUDES the ?accessToken= query string.
TS=$(date -u +%s)
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

# Review the result in the dashboard: Transactions → filter "User platform event".
