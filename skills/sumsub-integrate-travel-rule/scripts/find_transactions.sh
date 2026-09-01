#!/usr/bin/env bash
# Run a transaction search. The path must already contain the matrix criteria —
# build it with build_query.py, which validates the field allowlist.
# Usage: find_transactions.sh "PATH_WITH_CRITERIA"
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
QUERY_PATH="${1:?Usage: find_transactions.sh \"PATH_WITH_CRITERIA\"}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" GET "$QUERY_PATH"
