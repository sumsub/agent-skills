#!/usr/bin/env bash
# Mark an unhosted wallet verified by hand. Exception path — the address stays
# trusted for future matching, so keep an audit trail on your side.
# Only valid on a paymentMethod action.
# Usage: manual_verify.sh ACTION_ID
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
ACTION_ID="${1:?Usage: manual_verify.sh ACTION_ID}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/api/applicantActions/${ACTION_ID}/unhostedWallet/manualVerify"
