#!/usr/bin/env bash
# Manage Sumsub clientWebhooks: list / get / create / update.
#
# Reads (GET list/get) hit /resources/api/clientWebhooks; writes (POST upsert
# for create/update) hit /resources/api/agent/clientWebhooks,
# Delete and per-webhook delivery
# stats have no public-API equivalent and must be handled in the Sumsub
# dashboard UI; they are not implemented here.
#
# Authenticates via App Token + secret (HMAC-SHA256) per
# https://docs.sumsub.com/reference/authentication. 
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:...  \
#   SUMSUB_SECRET_KEY=...     \
#     manage_webhooks.sh list [--json]
#   manage_webhooks.sh get    <id>
#   manage_webhooks.sh create <spec.json>
#   manage_webhooks.sh update <spec.json>     # spec must include id
#
# Refuses non-sandbox tokens unless SUMSUB_ALLOW_PROD=1.
# Override SUMSUB_BASE only for testing; default is https://api.sumsub.com.
set -euo pipefail

: "${SUMSUB_APP_TOKEN:?SUMSUB_APP_TOKEN is required (sandbox App Token, 'sbx:' prefix)}"
: "${SUMSUB_SECRET_KEY:?SUMSUB_SECRET_KEY is required (paired secret key)}"
BASE="${SUMSUB_BASE:-https://api.sumsub.com}"

if [[ "${SUMSUB_APP_TOKEN}" != sbx:* && "${SUMSUB_ALLOW_PROD:-0}" != "1" ]]; then
  echo "error: SUMSUB_APP_TOKEN does not look like a sandbox token (expected 'sbx:' prefix)." >&2
  echo "       Production credentials must not be shared with this skill." >&2
  exit 3
fi

HERE="$(cd "$(dirname "$0")" && pwd)"
# Reads (list / get) hit the non-agent resource; writes (create / update)
# hit the agent resource.
READ_PATH="/resources/api/clientWebhooks"
WRITE_PATH="/resources/api/agent/clientWebhooks"

if [[ $# -lt 1 ]]; then
  sed -n '4,22p' "$0" >&2; exit 2
fi
CMD="$1"; shift || true

# sumsub_request METHOD PATH_QUERY [BODY_FILE]
# Signs and sends; echoes response body to stdout. PATH_QUERY must start with '/'.
sumsub_request() {
  local method="$1" path_q="$2" body_file="${3-}"
  local ts sig
  ts="$(date -u +%s)"
  if [[ -n "${body_file}" ]]; then
    sig="$(
      { printf '%s%s%s' "${ts}" "${method}" "${path_q}"; cat "${body_file}"; } \
        | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
        | awk '{print $NF}'
    )"
  else
    sig="$(
      printf '%s%s%s' "${ts}" "${method}" "${path_q}" \
        | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex \
        | awk '{print $NF}'
    )"
  fi
  local args=(
    -sS -X "${method}"
    -H "X-App-Token: ${SUMSUB_APP_TOKEN}"
    -H "X-App-Access-Ts: ${ts}"
    -H "X-App-Access-Sig: ${sig}"
    -H "X-Agent-Source: sumsub-skills"
    -H "X-Agent-Source-Ver: 1.4.1"
    -H "Accept: application/json"
  )
  if [[ -n "${body_file}" ]]; then
    args+=(-H "Content-Type: application/json" --data-binary "@${body_file}")
  fi
  curl "${args[@]}" "${BASE%/}${path_q}"
}

fmt_list() {
  local body
  body=$(cat)
  BODY="$body" python3 - <<'PY'
import json, os, sys
raw = os.environ["BODY"]
try:
    d = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"  (response was not JSON: {e})", file=sys.stderr)
    print(f"  first 200 chars: {raw[:200]!r}", file=sys.stderr)
    sys.exit(1)
items = (d.get("list") or {}).get("items") or (d if isinstance(d, list) else [])
if not items:
    print("(no webhooks)")
    sys.exit(0)
print(f"{'id':24}  {'name':28.28}  {'target':40.40}  {'disabled':8}  {'types':20.20}  applicantType")
print("-"*150)
for w in items:
    types = ", ".join(w.get("types") or [])
    print(f"{w.get('id','?'):24}  {(w.get('name') or '?'):28.28}  {(w.get('target') or '?'):40.40}  "
          f"{str(w.get('disabled')):8}  {types[:20]:20}  {w.get('applicantType') or '-'}")
print(f"\ntotal: {len(items)}")
PY
}

case "$CMD" in
  list)
    json_only="false"
    if [[ "${1:-}" == "--json" ]]; then json_only="true"; fi
    body="$(sumsub_request GET "${READ_PATH}")"
    if [[ "$json_only" == "true" ]]; then
      echo "$body"
    else
      echo "$body" | fmt_list
    fi
    ;;

  get)
    [[ $# -ge 1 ]] || { echo "usage: get <id>" >&2; exit 2; }
    id="$1"
    sumsub_request GET "${READ_PATH}" \
      | python3 -c "
import json, sys
target=sys.argv[1]
d=json.load(sys.stdin)
items=(d.get('list') or {}).get('items') or []
for w in items:
    if w.get('id')==target:
        if 'secretKey' in w and w['secretKey']:
            w['secretKey']='<redacted>'
        print(json.dumps(w, indent=2))
        sys.exit(0)
print(f'no webhook with id={target!r} (checked {len(items)})', file=sys.stderr)
sys.exit(1)
" "$id"
    ;;

  create|update)
    [[ $# -ge 1 ]] || { echo "usage: $CMD <spec.json>" >&2; exit 2; }
    spec="$1"
    [[ -f "$spec" ]] || { echo "spec file not found: $spec" >&2; exit 2; }
    payload="$(mktemp)"
    trap 'rm -f "$payload"' EXIT
    python3 "${HERE}/build_webhook_payload.py" < "$spec" > "$payload"
    has_id="$(python3 -c "import json,sys; print('yes' if json.load(open(sys.argv[1])).get('id') else 'no')" "$payload")"
    if [[ "$CMD" == "create" && "$has_id" == "yes" ]]; then
      echo "warning: spec for 'create' contains id=... — this will UPDATE that webhook instead" >&2
    fi
    if [[ "$CMD" == "update" && "$has_id" == "no" ]]; then
      echo "error: 'update' requires id in the spec" >&2; exit 2
    fi
    resp="$(sumsub_request POST "${WRITE_PATH}" "$payload")"
    echo "$resp" | python3 -c "
import json, sys
w=json.load(sys.stdin)
if w.get('code'):
    print('ERROR:', w); sys.exit(1)
print('persisted webhook:')
print(f\"  id:            {w.get('id')}\")
print(f\"  name:          {w.get('name')!r}\")
print(f\"  target:        {w.get('target')!r}\")
print(f\"  targetType:    {w.get('targetType')}\")
print(f\"  applicantType: {w.get('applicantType')}\")
print(f\"  signing:       {w.get('signatureAlgorithm')}\")
print(f\"  disabled:      {w.get('disabled')}\")
print(f\"  types:         {w.get('types')}\")
"
    ;;

  *)
    echo "unknown command: $CMD" >&2
    sed -n '4,22p' "$0" >&2
    exit 2
    ;;
esac
