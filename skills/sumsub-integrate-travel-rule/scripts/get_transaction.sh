#!/usr/bin/env bash
# Fetch one transaction by its Sumsub id (not your own txnId).
# Usage: get_transaction.sh TRANSACTION_ID
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
TXN_ID="${1:?Usage: get_transaction.sh TRANSACTION_ID}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/kyt/txns/${TXN_ID}/one"
