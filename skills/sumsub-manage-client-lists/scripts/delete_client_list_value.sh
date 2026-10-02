#!/usr/bin/env bash
# Remove one value from a list by its exact key.
# Usage: delete_client_list_value.sh <listId> <key>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

# emails carry "+", CIDR carries "/" — both must be encoded before signing
urlencode() {
  KEY="$1" python3 -c 'import os, urllib.parse; print(urllib.parse.quote(os.environ["KEY"], safe=""))'
}

LIST_ID="${1:?listId argument required}"
# the id goes straight into the path — anything else could address another resource
if [[ ! "${LIST_ID}" =~ ^[0-9a-f]{24}$ ]]; then
  echo "error: listId must be the 24-char hex id from get_client_lists.sh, got '${LIST_ID}'" >&2
  exit 2
fi
KEY="${2:?key argument required}"
exec bash "$SCRIPT_DIR/sumsub_curl.sh" DELETE "/resources/api/agent/clientLists/${LIST_ID}/values?key=$(urlencode "${KEY}")"
