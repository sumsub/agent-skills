#!/usr/bin/env bash
# Register one payment method (e.g. a crypto wallet) against an applicant.
# Usage: add_payment_method.sh APPLICANT_ID PAYLOAD_FILE
#   APPLICANT_ID is Sumsub's internal applicant id, not your externalUserId.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

APPLICANT_ID="${1:?Usage: add_payment_method.sh APPLICANT_ID PAYLOAD_FILE}"
PAYLOAD="${2:?Usage: add_payment_method.sh APPLICANT_ID PAYLOAD_FILE}"

exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/api/applicants/${APPLICANT_ID}/payments" "$PAYLOAD"
