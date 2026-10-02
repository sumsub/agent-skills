#!/usr/bin/env bash
# Add one NEW value to a list. A key the list already holds is refused with a
# 400 naming the key; the script never asks to overwrite, so an existing entry
# is never silently replaced. To change an entry, delete the key and add it again.
# Usage: add_client_list_value.sh <listId> <key> [description]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

LIST_ID="${1:?listId argument required}"
# the id goes straight into the path — anything else could address another resource
if [[ ! "${LIST_ID}" =~ ^[0-9a-f]{24}$ ]]; then
  echo "error: listId must be the 24-char hex id from get_client_lists.sh, got '${LIST_ID}'" >&2
  exit 2
fi
KEY="${2:?key argument required}"
DESC="${3-}"

BODY="$(KEY="$KEY" DESC="$DESC" python3 -c '
import json, os
value = {"key": os.environ["KEY"]}
if os.environ.get("DESC"):
    value["desc"] = os.environ["DESC"]
print(json.dumps(value))
')"

printf '%s' "${BODY}" | bash "$SCRIPT_DIR/sumsub_curl.sh" \
  POST "/resources/api/agent/clientLists/${LIST_ID}/values" -
