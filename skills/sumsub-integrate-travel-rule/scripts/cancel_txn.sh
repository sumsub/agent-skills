#!/usr/bin/env bash
# Cancel an exchange the user abandoned (flow ① only).
# Usage: cancel_txn.sh TRANSACTION_ID
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
TXN_ID="${1:?Usage: cancel_txn.sh TRANSACTION_ID}"
BODY_FILE="$(mktemp)"
trap 'rm -f "${BODY_FILE}"' EXIT
printf '{}' >"$BODY_FILE"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/api/tr/${TXN_ID}/cancel" "$BODY_FILE"
