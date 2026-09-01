#!/usr/bin/env bash
# Generate a Travel Rule SDK session so the user can prove wallet ownership.
# Usage: tr_sdk_init.sh SPEC_FILE   ('-' for stdin)
# The applicant must already exist; userId is your externalUserId.
# Returns { link, token, ttlInSecs } — hand the link to the user, never the App Token.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"
SPEC="${1:?Usage: tr_sdk_init.sh SPEC_FILE}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/tr/sdk/init" "$SPEC"
