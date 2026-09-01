#!/usr/bin/env bash
# List an applicant's actions — use it to find an existing verification action
# before creating a new SDK session.
# Usage: get_applicant_actions.sh APPLICANT_ID
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
APPLICANT_ID="${1:?Usage: get_applicant_actions.sh APPLICANT_ID}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/applicantActions/-;applicantId=${APPLICANT_ID}"
