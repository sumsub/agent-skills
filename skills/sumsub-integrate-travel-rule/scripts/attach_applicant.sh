#!/usr/bin/env bash
# Response two of answering an incoming Travel Rule request:
# identify whose wallet it is. Pass an applicantId, or '-' to read a JSON body
# ({"applicantId": ...} or {"applicantParticipant": {...}}) from stdin.
# Usage: attach_applicant.sh TRANSACTION_ID APPLICANT_ID
#        attach_applicant.sh TRANSACTION_ID - < body.json
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
TXN_ID="${1:?Usage: attach_applicant.sh TRANSACTION_ID APPLICANT_ID|-}"
WHO="${2:?Usage: attach_applicant.sh TRANSACTION_ID APPLICANT_ID|-}"
if [[ "$WHO" == "-" ]]; then
  exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/kyt/txns/${TXN_ID}/travelRuleOwnership" -
fi
BODY_FILE="$(mktemp)"
trap 'rm -f "${BODY_FILE}"' EXIT
printf '{"applicantId":"%s"}' "$WHO" >"$BODY_FILE"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/kyt/txns/${TXN_ID}/travelRuleOwnership" "$BODY_FILE"
