#!/usr/bin/env bash
# Compares the locally installed agent-skills version against the canonical
# version published at https://api.sumsub.com/llms.txt and prints a verdict.
#
# Local version  — read from references/version.txt (baked at publish time).
# Remote version — the `agent-skills-version:` line in the canonical llms.txt.
#                  Also tolerates a JSON `"version"` field and a bare
#                  `version:` line so the script works if the source ever
#                  moves (e.g. to a package.json or another flat format).
#
# Output (stdout), one key per line:
#   local=<x.y.z>
#   remote=<x.y.z|unknown>
#   status=<UP_TO_DATE|PATCH_BEHIND|MINOR_BEHIND|MAJOR_BEHIND|AHEAD|UNKNOWN>
#
# No API auth needed — the source file is public. Override with
# $SUMSUB_VERSION_URL (preferred) or the legacy $SUMSUB_LLMS_URL.
set -euo pipefail

SKILL_DIR="${CLAUDE_SKILL_DIR:-"$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"}"
DEFAULT_URL="https://api.sumsub.com/llms.txt"
VERSION_URL="${SUMSUB_VERSION_URL:-${SUMSUB_LLMS_URL:-${DEFAULT_URL}}}"

# Read the baked local version and accept it only if it's a full x.y.z semver;
# anything malformed (e.g. "1.0", empty, stray text) falls back to "unknown" so
# the comparison below stays in the safe UNKNOWN branch instead of crashing.
LOCAL="$(
  tr -d '[:space:]' < "${SKILL_DIR}/references/version.txt" 2>/dev/null \
    | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+$' \
    | head -n1 || true
)"
[ -n "${LOCAL}" ] || LOCAL="unknown"

REMOTE_RAW="$(
  curl -fsS \
    --max-time 5 \
    -H "Accept: application/json, text/plain;q=0.9, */*;q=0.1" \
    -H "X-Agent-Source: sumsub-skills" \
    -H "X-Agent-Source-Ver: 1.4.1" \
    "${VERSION_URL}" 2>/dev/null || true
)"

extract_semver() {
  # $1 = raw text, $2 = anchored field-name regex
  # Prints the first semver on a line whose key matches the regex.
  printf '%s\n' "$1" \
    | grep -iE "$2" \
    | head -n1 \
    | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' \
    | head -n1 || true
}

# Preferred: `agent-skills-version: x.y.z` line in the canonical llms.txt.
REMOTE="$(extract_semver "${REMOTE_RAW}" '^[[:space:]]*-?[[:space:]]*agent-skills-version[[:space:]]*:')"
# Fallbacks: JSON `"version":` field (e.g. package.json) and a bare `version:` line.
[ -n "${REMOTE}" ] || REMOTE="$(extract_semver "${REMOTE_RAW}" '"version"[[:space:]]*:')"
[ -n "${REMOTE}" ] || REMOTE="$(extract_semver "${REMOTE_RAW}" '^[[:space:]]*-?[[:space:]]*(skills-)?version[[:space:]]*:')"
[ -n "${REMOTE}" ] || REMOTE="unknown"

status="UNKNOWN"
if [ "${LOCAL}" != "unknown" ] && [ "${REMOTE}" != "unknown" ]; then
  IFS=. read -r lmaj lmin lpat <<EOF
${LOCAL}
EOF
  IFS=. read -r rmaj rmin rpat <<EOF
${REMOTE}
EOF
  if [ "${lmaj}" -eq "${rmaj}" ] && [ "${lmin}" -eq "${rmin}" ] && [ "${lpat}" -eq "${rpat}" ]; then
    status="UP_TO_DATE"
  elif [ "${rmaj}" -gt "${lmaj}" ]; then
    status="MAJOR_BEHIND"
  elif [ "${rmaj}" -eq "${lmaj}" ] && [ "${rmin}" -gt "${lmin}" ]; then
    status="MINOR_BEHIND"
  elif [ "${rmaj}" -eq "${lmaj}" ] && [ "${rmin}" -eq "${lmin}" ] && [ "${rpat}" -gt "${lpat}" ]; then
    status="PATCH_BEHIND"
  else
    status="AHEAD"
  fi
fi

# Ready-to-render heads-up line. Empty for the silent verdicts (UP_TO_DATE,
# UNKNOWN). For every other verdict this is the EXACT markdown the skill must
# surface verbatim as the first line of its reply — single source of truth, so
# the wording can't drift between an implicit and an explicit trigger.
headsup=""
case "${status}" in
  PATCH_BEHIND)
    headsup="> ⚠️ **Sumsub skills update available** — you're on **${LOCAL}**, latest is **${REMOTE}** (patch). Run \`npx skills add sumsub/agent-skills --all\` to update (drop \`--all\` if your CLI reports an unknown flag)." ;;
  MINOR_BEHIND)
    headsup="> ⚠️ **Sumsub skills out of date** — you're on **${LOCAL}**, latest is **${REMOTE}**. Run \`npx skills add sumsub/agent-skills --all\` to update (drop \`--all\` if your CLI reports an unknown flag)." ;;
  MAJOR_BEHIND)
    headsup="> 🚨 **Sumsub skills significantly behind** (**${LOCAL} → ${REMOTE}**) — behavior may have changed. Run \`npx skills add sumsub/agent-skills --all\` before relying on results (drop \`--all\` if your CLI reports an unknown flag)." ;;
  AHEAD)
    headsup="> ℹ️ Sumsub skills **${LOCAL}** are ahead of the published **${REMOTE}** — likely a local dev build. Proceeding." ;;
esac

# Cache the rendered blockquote next to the script so the Phase-2 render step
# (render_headsup.sh) can re-emit it LAST — after the user's task — with no
# second curl. A stable ${SKILL_DIR} path survives a differing parent shell
# between the two invocations.
HEADSUP_CACHE="${SKILL_DIR}/.headsup_cache"

printf 'local=%s\nremote=%s\nstatus=%s\n' "${LOCAL}" "${REMOTE}" "${status}"
if [ -n "${headsup}" ]; then
  printf 'headsup=%s\n' "${headsup}"
  printf '%s\n' "${headsup}" > "${HEADSUP_CACHE}" 2>/dev/null || true
else
  # Silent verdict (UP_TO_DATE / UNKNOWN): never leave a stale line behind.
  rm -f "${HEADSUP_CACHE}" 2>/dev/null || true
fi
