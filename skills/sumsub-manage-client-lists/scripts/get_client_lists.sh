#!/usr/bin/env bash
# List client lists, or resolve one by its exact name.
# Usage: get_client_lists.sh [listName]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

NAME="${1-}"
# `|| STATUS=$?` keeps set -e from killing the script before the error body is
# printed: on a 4xx sumsub_curl.sh writes the body to stdout and then exits 1.
# Its stderr ("HTTP 400") is held back so it prints after the body, not before.
STATUS=0
ERR_FILE="$(mktemp)"
trap 'rm -f "${ERR_FILE}"' EXIT
BODY="$(bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/api/agent/clientLists?limit=1000" 2>"${ERR_FILE}")" || STATUS=$?
if [[ "${STATUS}" -ne 0 || -z "${NAME}" ]]; then
  printf '%s\n' "${BODY}"
  cat "${ERR_FILE}" >&2
  exit "${STATUS}"
fi
cat "${ERR_FILE}" >&2

# The API has no name filter, so the lookup is an exact match over the listing.
# An empty result means the client has no list with that name.
BODY="${BODY}" NAME="${NAME}" python3 -c '
import json, os, sys
try:
    d = json.loads(os.environ["BODY"])
except json.JSONDecodeError:
    d = None
if not isinstance(d, dict):
    print(os.environ["BODY"])
    sys.stderr.write("error: the listing is not a JSON object — cannot resolve the name\n")
    sys.exit(1)
lists = d.get("items") or []
total = d.get("totalItems")
# a truncated listing can hide the list: empty is then not proof it is missing
if isinstance(total, int) and len(lists) < total:
    sys.stderr.write(
        f"warning: the listing holds {len(lists)} of {total} lists — an empty result does not "
        "prove the list is missing; do not create it, ask the user to check the dashboard\n"
    )
items = [l for l in lists if isinstance(l, dict) and l.get("name") == os.environ["NAME"]]
print(json.dumps({"items": items, "totalItems": len(items)}))
'
