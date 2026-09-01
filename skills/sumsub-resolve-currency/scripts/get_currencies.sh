#!/usr/bin/env bash
# Fetch the Sumsub currency catalogue.
# Usage: get_currencies.sh [crypto|fiat]
#   Defaults to crypto. Omitting the type server-side yields the fiat list.
#   The crypto catalogue is ~10k entries and static — cache it for the session
#   rather than re-fetching per lookup.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${SUMSUB_APP_TOKEN:?}" "${SUMSUB_SECRET_KEY:?}"

TYPE="${1:-crypto}"
case "$TYPE" in
  crypto|fiat) ;;
  *) echo "error: type must be 'crypto' or 'fiat' (got '$TYPE')" >&2; exit 2 ;;
esac

exec bash "$SCRIPT_DIR/sumsub_curl.sh" GET "/resources/kyt/currency?type=${TYPE}"
