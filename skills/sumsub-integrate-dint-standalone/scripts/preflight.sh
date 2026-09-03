#!/usr/bin/env bash
# Device Intelligence standalone preflight — machine-validates the workspace
# before any frontend code is written. Each check is independent; one failing
# check doesn't abort the others.
#
# What it probes:
#   behavior_token — mints a real short-TTL behavior token (the Stage-1 call).
#                    Proves HMAC signing is accepted AND Device Intelligence is
#                    enabled for this workspace. The token is never used and
#                    simply expires; nothing else is mutated.
#   levels         — lists verification levels. Only the pre-KYC confirm path
#                    (create-applicant) needs one, so a missing level is a WARN,
#                    not a FAIL — the platform-event path works without it.
#
# Usage:
#   SUMSUB_APP_TOKEN=sbx:... SUMSUB_SECRET_KEY=... bash scripts/preflight.sh
#
# Exit code: 0 on all-PASS or PASS+WARN, 10 on any FAIL.
set -u

# Hard dependencies — fail fast with a clear message rather than letting
# downstream commands swallow the missing-binary error into a misleading
# auth/credential diagnosis.
for dep in curl openssl python3 awk; do
  command -v "$dep" >/dev/null || { echo "[FAIL] preflight requires '$dep' on PATH" >&2; exit 10; }
done

: "${SUMSUB_APP_TOKEN:?set SUMSUB_APP_TOKEN (sbx:...)}"
: "${SUMSUB_SECRET_KEY:?set SUMSUB_SECRET_KEY}"
BASE="${SUMSUB_BASE:-https://api.sumsub.com}"

if [[ "${SUMSUB_APP_TOKEN}" != sbx:* && "${SUMSUB_ALLOW_PROD:-0}" != "1" ]]; then
  echo "[FAIL] token_format          SUMSUB_APP_TOKEN doesn't start with 'sbx:' — use a sandbox token (SUMSUB_ALLOW_PROD=1 to override)." >&2
  exit 10
fi

# Helpers ---------------------------------------------------------------------

sign_get() {  # path -> "ts sig"
  local path="$1" ts sig
  ts="$(date -u +%s)"
  sig="$(printf '%s%s%s' "${ts}" "GET" "${path}" \
        | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex | awk '{print $NF}')"
  printf '%s %s\n' "${ts}" "${sig}"
}

sign_post() {  # path body -> "ts sig"
  local path="$1" body="$2" ts sig
  ts="$(date -u +%s)"
  sig="$(printf '%s%s%s%s' "${ts}" "POST" "${path}" "${body}" \
        | openssl dgst -sha256 -hmac "${SUMSUB_SECRET_KEY}" -hex | awk '{print $NF}')"
  printf '%s %s\n' "${ts}" "${sig}"
}

extract_json_field() {  # field <<<json
  python3 -c 'import sys,json
try:
  d=json.load(sys.stdin); k=sys.argv[1]
  v=d
  for p in k.split("."):
    v = v.get(p) if isinstance(v, dict) else None
    if v is None: break
  print(v if v is not None else "")
except (ValueError, json.JSONDecodeError, AttributeError):
  print("")' "$1" 2>/dev/null
}

emit() {  # status name detail
  printf '  [%s] %-22s %s\n' "$1" "$2" "$3"
}

# Combined-output curl idiom (no -o): the body is followed by a "HTTP <code>"
# trailer line emitted by `-w '\nHTTP %{http_code}\n'`. These split the two back
# out — works identically under real curl and the test mock.
http_code_from() { awk '/^HTTP [0-9][0-9][0-9]$/{c=$2} END{print c}'; }
strip_http_line() { sed '/^HTTP [0-9][0-9][0-9]*$/d'; }

# Checks ----------------------------------------------------------------------

check_behavior_token() {
  local path="/resources/accessTokens/behavior"
  # Body is part of the signed string for POSTs with a body (Stage-1 rule).
  local body
  body="$(printf '{"sessionId":"_preflight_%s","ttlInSecs":600}' "$(date -u +%s)")"
  read -r ts sig <<<"$(sign_post "${path}" "${body}")"
  local resp code rbody
  resp="$(curl -sS -w '\nHTTP %{http_code}\n' -X POST \
    -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
    -H "X-App-Access-Ts: ${ts}" \
    -H "X-App-Access-Sig: ${sig}" \
    -H "X-Agent-Source: sumsub-skills" \
    -H "X-Agent-Source-Ver: 1.4.1" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    --data "${body}" "${BASE}${path}")"
  code="$(printf '%s' "${resp}" | http_code_from)"
  rbody="$(printf '%s' "${resp}" | strip_http_line)"
  local token; token="$(printf '%s' "${rbody}" | extract_json_field token)"
  local desc; desc="$(printf '%s' "${rbody}" | extract_json_field description)"
  [[ -z "${desc}" ]] && desc="$(printf '%s' "${rbody}" | extract_json_field message)"

  case "${code}" in
    200|201)
      if [[ -n "${token}" ]]; then
        emit PASS behavior_token "HMAC accepted, Device Intelligence enabled — behavior token minted (short TTL, discarded)"
        return 0
      fi
      emit FAIL behavior_token "HTTP ${code} but no token in response — Device Intelligence likely not enabled for this workspace. Check the entitlement (sumsub-check-permissions) or contact support@sumsub.com. body=${desc}"
      return 1 ;;
    401)
      emit FAIL behavior_token "HMAC rejected (401) — re-check the SUMSUB_APP_TOKEN + SUMSUB_SECRET_KEY pair. body=${desc}"
      return 1 ;;
    403)
      emit FAIL behavior_token "rejected (403) — App Token revoked, wrong sandbox/prod context, or Device Intelligence not enabled for this workspace. Check the entitlement (Dashboard, or sumsub-check-permissions) and contact your CSM / support@sumsub.com if it's off. body=${desc}"
      return 1 ;;
    *)
      emit WARN behavior_token "unexpected HTTP ${code}. body=${desc}"
      return 0 ;;
  esac
}

check_levels() {
  local path="/resources/applicants/-/levels"
  read -r ts sig <<<"$(sign_get "${path}")"
  local resp code rbody
  resp="$(curl -sS -w '\nHTTP %{http_code}\n' \
    -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
    -H "X-App-Access-Ts: ${ts}" \
    -H "X-App-Access-Sig: ${sig}" \
    -H "X-Agent-Source: sumsub-skills" \
    -H "X-Agent-Source-Ver: 1.4.1" \
    -H "Accept: application/json" \
    "${BASE}${path}")"
  code="$(printf '%s' "${resp}" | http_code_from)"
  rbody="$(printf '%s' "${resp}" | strip_http_line)"
  if [[ "${code}" != "200" ]]; then
    emit WARN levels "cannot list levels (HTTP ${code}) — App Token may lack 'manageClientSettings'. Only the pre-KYC confirm path needs a level."
    return 0
  fi
  # Names come back one-per-line so a comma inside a level name doesn't
  # inflate the count or corrupt the display.
  local names
  names="$(printf '%s' "${rbody}" | python3 -c 'import sys,json
try:
  d=json.load(sys.stdin); items=d.get("list",{}).get("items",[]) or d.get("items",[]) or []
  print("\n".join([i.get("name","?") for i in items]))
except (ValueError, json.JSONDecodeError, AttributeError): print("")')"
  local count
  count="$(printf '%s' "${names}" | grep -c . || true)"
  if [[ "${count}" == "0" ]]; then
    emit WARN levels "no verification levels — fine for the platform-event path; the pre-KYC confirm path needs one (sumsub-create-level)"
    return 0
  fi
  local display
  display="$(printf '%s' "${names}" | tr '\n' ',' | sed 's/,$//')"
  emit PASS levels "${count} level(s): ${display}"
  return 0
}

# Run all checks --------------------------------------------------------------

echo "Sumsub Device Intelligence standalone preflight"
echo

fail=0
check_behavior_token || fail=$((fail+1))
check_levels         || fail=$((fail+1))
echo

if (( fail > 0 )); then
  echo "→ ${fail} FAIL(s). Resolve before Stage 1." >&2
  exit 10
fi
echo "→ All clear. Proceed to Stage 1 (backend token route)."
exit 0
