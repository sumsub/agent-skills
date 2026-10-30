#!/usr/bin/env bash
# Search for an existing Travel Rule transaction (dedupe before an after-settlement exchange).
# Usage: find_transactions.sh BODY_FILE_OR_-   (body shape: examples/dedupe-search.json)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
BODY="${1:?Usage: find_transactions.sh BODY_FILE_OR_-}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST /resources/api/tr/txns/search "$BODY"
