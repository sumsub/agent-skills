#!/usr/bin/env bash
# Create a client list. Body on stdin or in a file.
# Refuses a spec named (or titled into) my_default_blocklist — any list under that
# name that the applicant blocklist call did not create breaks every later call.
# Usage: create_client_list.sh [BODY_FILE_OR_-]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

SRC="${1:--}"
if [[ "${SRC}" == "-" ]]; then
  SPEC="$(cat)"
else
  SPEC="$(cat "${SRC}")"
fi

SPEC="${SPEC}" python3 -c '
import json, os, re, sys
try:
    d = json.loads(os.environ["SPEC"])
except json.JSONDecodeError:
    sys.exit(0)  # let the API report the malformed body
if not isinstance(d, dict):
    sys.exit(0)
derived = re.sub(r"[^a-z0-9]+", "_", str(d.get("title", "")).lower()).strip("_")
if (d.get("name") or derived) == "my_default_blocklist":  # server derives only when name is absent
    sys.stderr.write("error: refusing to create my_default_blocklist — the first applicant blocklist call creates it\n")
    sys.exit(2)
'

printf '%s' "${SPEC}" | bash "$SCRIPT_DIR/sumsub_curl.sh" POST "/resources/api/agent/clientLists" -
