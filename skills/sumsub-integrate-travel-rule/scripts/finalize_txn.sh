#!/usr/bin/env bash
# Flow ① finalisation: link the broadcast on-chain hash so the exchange can
# move from completed to finished.
# Usage: finalize_txn.sh TRANSACTION_ID PAYMENT_TXN_ID
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
TXN_ID="${1:?Usage: finalize_txn.sh TRANSACTION_ID PAYMENT_TXN_ID}"
HASH="${2:?Usage: finalize_txn.sh TRANSACTION_ID PAYMENT_TXN_ID}"
BODY_FILE="$(mktemp)"
trap 'rm -f "${BODY_FILE}"' EXIT
printf '{"paymentTxnId":"%s"}' "$HASH" >"$BODY_FILE"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" PATCH "/resources/kyt/txns/${TXN_ID}/data/info" "$BODY_FILE"
