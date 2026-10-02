#!/usr/bin/env bash
# Read one list back by id — after create, update or delete (a deleted list answers 404).
# Usage: get_client_list.sh <listId>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

LIST_ID="${1:?listId argument required}"
# the id goes straight into the path — anything else could address another resource
if [[ ! "${LIST_ID}" =~ ^[0-9a-f]{24}$ ]]; then
  echo "error: listId must be the 24-char hex id from get_client_lists.sh, got '${LIST_ID}'" >&2
  exit 2
fi
exec bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/api/agent/clientLists/${LIST_ID}"
