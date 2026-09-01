#!/usr/bin/env bash
# Response one of answering an incoming Travel Rule request:
# declare whether the asked wallet belongs to your organisation/user.
# Usage: confirm_ownership.sh TRANSACTION_ID confirmed|unconfirmed
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
TXN_ID="${1:?Usage: confirm_ownership.sh TRANSACTION_ID confirmed|unconfirmed}"
ANSWER="${2:?Usage: confirm_ownership.sh TRANSACTION_ID confirmed|unconfirmed}"
case "$ANSWER" in confirmed|unconfirmed) ;; *) echo "error: answer must be 'confirmed' or 'unconfirmed'" >&2; exit 2;; esac
exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/kyt/txns/${TXN_ID}/ownership/${ANSWER}"
