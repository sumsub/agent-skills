#!/usr/bin/env bash
# Read one applicant action.
# Usage: get_action.sh ACTION_ID
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
ACTION_ID="${1:?Usage: get_action.sh ACTION_ID}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/applicantActions/${ACTION_ID}/one"
