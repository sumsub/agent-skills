#!/usr/bin/env bash
# Read the latest wallet-ownership check on an action.
# Usage: get_latest_check.sh ACTION_ID [CHECK_TYPE]
#   CHECK_TYPE defaults to WALLET_OWNERSHIP_CHECK.
# An empty result is not a failure — an account offering only manualReview
# never produces an automated check.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
ACTION_ID="${1:?Usage: get_latest_check.sh ACTION_ID [CHECK_TYPE]}"
TYPE="${2:-WALLET_OWNERSHIP_CHECK}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/api/applicantActions/${ACTION_ID}/checks/latest?type=${TYPE}"
