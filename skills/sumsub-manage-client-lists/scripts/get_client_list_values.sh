#!/usr/bin/env bash
# Read a list's values, or check one exact key.
# Usage: get_client_list_values.sh <listId> [key] [offset]
#   page a listing with an empty key: get_client_list_values.sh <listId> "" 1000
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
KEY="${2-}"
if [[ -n "${KEY}" ]]; then
  exec bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/api/agent/clientLists/${LIST_ID}/values?key=$(urlencode "${KEY}")"
fi

# One page only. A list holds up to 50 000 values, so a read-back of a large list
# is a window, not the whole list — never conclude "the key did not land" from a
# truncated page. The warning below says when that happened and prints the exact
# command for the next page — the key slot stays "" so the offset is not read as a key.
LIMIT=1000
OFFSET="${3-0}"
if [[ ! "${OFFSET}" =~ ^[0-9]+$ ]]; then
  echo "error: offset must be a non-negative integer, got '${OFFSET}'" >&2
  exit 2
fi
# `|| STATUS=$?` keeps set -e from killing the script before the error body is
# printed: on a 4xx sumsub_curl.sh writes the body to stdout and then exits 1.
# Its stderr ("HTTP 400") is held back so it prints after the body, not before.
STATUS=0
ERR_FILE="$(mktemp)"
trap 'rm -f "${ERR_FILE}"' EXIT
BODY="$(bash "$SCRIPT_DIR/sumsub_curl.sh" \
  GET "/resources/api/agent/clientLists/${LIST_ID}/values?limit=${LIMIT}&offset=${OFFSET}" 2>"${ERR_FILE}")" || STATUS=$?
printf '%s\n' "${BODY}"
cat "${ERR_FILE}" >&2
if [[ "${STATUS}" -ne 0 ]]; then
  exit "${STATUS}"
fi

BODY="${BODY}" LIST_ID="${LIST_ID}" OFFSET="${OFFSET}" python3 -c '
import json, os, sys
try:
    d = json.loads(os.environ["BODY"])
except json.JSONDecodeError:
    sys.exit(0)
if not isinstance(d, dict):
    sys.exit(0)
offset = int(os.environ["OFFSET"])
shown = len(d.get("items") or []) + offset
total = d.get("totalItems")
if isinstance(total, int) and shown < total:
    cmd = "get_client_list_values.sh " + os.environ["LIST_ID"]
    # the API refuses an offset above 5000 with a 400, so past that only ?key= checks read
    if offset < 5000:
        next_step = f"Next page: {cmd} \"\" {min(shown, 5000)} — or check one key: {cmd} <key>"
    else:
        next_step = f"No further page can be read (offset is capped at 5000) — check each key: {cmd} <key>"
    sys.stderr.write(
        f"warning: this page holds values {offset + 1}–{shown} of {total} — the list is truncated. "
        f"{next_step}\n"
    )
' || true
