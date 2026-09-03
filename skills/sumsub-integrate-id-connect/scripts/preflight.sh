#!/usr/bin/env bash
# Sumsub ID Connect preflight — machine-validates the Stage 0 preconditions
# checklist that can be checked without minting real OIDC codes or creating
# applicants. Each check is independent; one failing check doesn't abort the
# others.
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

: "${SUMSUB_APP_TOKEN:?set SUMSUB_APP_TOKEN}"
: "${SUMSUB_SECRET_KEY:?set SUMSUB_SECRET_KEY}"
BASE="${SUMSUB_BASE:-https://api.sumsub.com}"
ID_BASE="${SUMSUB_ID_BASE:-https://id.sumsub.com}"

if [[ "${SUMSUB_APP_TOKEN}" != sbx:* && "${SUMSUB_ALLOW_PROD:-0}" != "1" ]]; then
  echo "[FAIL] token_format          SUMSUB_APP_TOKEN doesn't start with 'sbx:' — use a sandbox token." >&2
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

# Checks ----------------------------------------------------------------------

check_connect_token() {
  local path="/resources/snsId/api/connect/token"
  local body='{"grant_type":"authorization_code","code":"_preflight_invalid_code_","codeVerifier":"_preflight_"}'
  read -r ts sig <<<"$(sign_post "${path}" "${body}")"
  local tmp; tmp="$(mktemp)"
  local code
  code="$(curl -sS -o "${tmp}" -w '%{http_code}' -X POST \
    -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
    -H "X-App-Access-Ts: ${ts}" \
    -H "X-App-Access-Sig: ${sig}" \
    -H "X-Agent-Source: sumsub-skills" \
    -H "X-Agent-Source-Ver: 1.4.1" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    --data "${body}" "${BASE}${path}")"
  local desc; desc="$(extract_json_field description <"${tmp}")"
  [[ -z "${desc}" ]] && desc="$(extract_json_field message <"${tmp}")"
  rm -f "${tmp}"

  case "${code}" in
    401)
      if echo "${desc}" | grep -qi 'invalid code'; then
        emit PASS connect_token "endpoint live, HMAC accepted"
        return 0
      fi
      emit FAIL connect_token "401 with non-'Invalid code' description — re-check SUMSUB_APP_TOKEN + SUMSUB_SECRET_KEY pair. body=${desc}"
      return 1 ;;
    403)
      emit FAIL connect_token "App Token rejected (403) — token revoked or wrong sandbox/prod context"
      return 1 ;;
    404)
      if echo "${desc}" | grep -qi 'invalid clientid'; then
        emit FAIL connect_token "ID Connect not enabled for this workspace — email Sumsub support"
      else
        emit WARN connect_token "unexpected 404. body=${desc}"
      fi
      return 0 ;;
    *)
      emit WARN connect_token "unexpected HTTP ${code}. body=${desc}"
      return 0 ;;
  esac
}

check_oidc_discovery() {
  local tmp; tmp="$(mktemp)"
  local code; code="$(curl -sS -o "${tmp}" -w '%{http_code}' "${ID_BASE}/.well-known/openid-configuration")"
  if [[ "${code}" != "200" ]]; then
    rm -f "${tmp}"
    emit FAIL oidc_discovery "${ID_BASE}/.well-known/openid-configuration returned HTTP ${code}"
    return 1
  fi
  local issuer; issuer="$(extract_json_field issuer <"${tmp}")"
  rm -f "${tmp}"
  if [[ -z "${issuer}" ]]; then
    emit WARN oidc_discovery "reachable but not a valid OIDC discovery doc"
    return 0
  fi
  emit PASS oidc_discovery "issuer=${issuer}"
  return 0
}

check_levels() {
  local path="/resources/applicants/-/levels"
  read -r ts sig <<<"$(sign_get "${path}")"
  local tmp; tmp="$(mktemp)"
  local code
  code="$(curl -sS -o "${tmp}" -w '%{http_code}' \
    -H "X-App-Token: ${SUMSUB_APP_TOKEN}" \
    -H "X-App-Access-Ts: ${ts}" \
    -H "X-App-Access-Sig: ${sig}" \
    -H "X-Agent-Source: sumsub-skills" \
    -H "X-Agent-Source-Ver: 1.4.1" \
    -H "Accept: application/json" \
    "${BASE}${path}")"
  if [[ "${code}" != "200" ]]; then
    rm -f "${tmp}"
    emit WARN levels "cannot list levels (HTTP ${code}) — App Token may lack 'manageClientSettings'"
    return 0
  fi
  # Names come back one-per-line so a comma inside a level name doesn't
  # inflate the count or corrupt the display.
  local names
  names="$(python3 -c 'import sys,json
try:
  d=json.load(sys.stdin); items=d.get("list",{}).get("items",[]) or d.get("items",[]) or []
  print("\n".join([i.get("name","?") for i in items]))
except (ValueError, json.JSONDecodeError, AttributeError): print("")' <"${tmp}")"
  rm -f "${tmp}"
  local count
  count="$(printf '%s' "${names}" | grep -c . || true)"
  if [[ "${count}" == "0" ]]; then
    emit FAIL levels "no verification levels in this workspace — create one (sumsub-create-level) before Stage 4"
    return 1
  fi
  local display
  display="$(printf '%s' "${names}" | tr '\n' ',' | sed 's/,$//')"
  emit PASS levels "${count} level(s): ${display}"
  return 0
}

# Run all checks --------------------------------------------------------------

echo "Sumsub ID Connect preflight"
echo

fail=0
check_connect_token  || fail=$((fail+1))
check_oidc_discovery || fail=$((fail+1))
check_levels         || fail=$((fail+1))
echo

if (( fail > 0 )); then
  echo "→ ${fail} FAIL(s). Resolve before Stage 1." >&2
  exit 10
fi
echo "→ All clear. Proceed to Stage 1 (frontend)."
exit 0
