#!/usr/bin/env bash
# Bulk-import wallet addresses into the Wallet Address Book.
# Usage: import_wallet_addresses.sh PAYLOAD_FILE
#   PAYLOAD_FILE is the JSON array produced by build_wallet_import.py ('-' for stdin).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

PAYLOAD="${1:?Usage: import_wallet_addresses.sh PAYLOAD_FILE}"

exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/kyt/walletAddress/import" "$PAYLOAD"
