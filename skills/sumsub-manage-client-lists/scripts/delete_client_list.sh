#!/usr/bin/env bash
# Delete a list together with every value in it. Refused past 1000 values and
# for Sumsub-maintained / system lists.
# Refuses my_default_blocklist: deleting it un-blocklists every applicant at once.
# Usage: delete_client_list.sh <listId>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

LIST_ID="${1:?listId argument required}"
# the id goes straight into the path — anything else could address another resource
if [[ ! "${LIST_ID}" =~ ^[0-9a-f]{24}$ ]]; then
  echo "error: listId must be the 24-char hex id from get_client_lists.sh, got '${LIST_ID}'" >&2
  exit 2
fi

# read the list first — fail closed if its name cannot be confirmed.
# `|| STATUS=$?` keeps set -e from killing the script before the error body is
# printed: on a 4xx sumsub_curl.sh writes the body to stdout and then exits 1.
STATUS=0
LIST="$(bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/api/agent/clientLists/${LIST_ID}")" || STATUS=$?
if [[ "${STATUS}" -ne 0 ]]; then
  printf '%s\n' "${LIST}"
  echo "error: could not read the list — not deleting" >&2
  exit "${STATUS}"
fi
NAME="$(LIST="${LIST}" python3 -c '
import json, os
try:
    d = json.loads(os.environ["LIST"])
except json.JSONDecodeError:
    d = None
print(d.get("name", "") if isinstance(d, dict) else "")
')"
if [[ -z "${NAME}" ]]; then
  printf '%s\n' "${LIST}"
  echo "error: could not read the list's name — not deleting" >&2
  exit 1
fi
if [[ "${NAME}" == "my_default_blocklist" ]]; then
  echo "error: refusing to delete my_default_blocklist — it un-blocklists every applicant on it; remove applicants one at a time" >&2
  exit 2
fi
exec bash "$SCRIPT_DIR/sumsub_curl.sh" DELETE "/resources/api/agent/clientLists/${LIST_ID}"
