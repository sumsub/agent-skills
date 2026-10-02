#!/usr/bin/env bash
# Change a list's title and/or desc — the only editable fields. Body on stdin or in
# a file: {"id": "<listId>", "title": "...", "desc": "..."}; omitted fields are kept.
# Usage: update_client_list.sh [BODY_FILE_OR_-]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

exec bash "$SCRIPT_DIR/sumsub_curl.sh" PATCH "/resources/api/agent/clientLists" "${1:--}"
