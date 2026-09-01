---
name: sumsub-api-generic
description: Catch-all fallback for any Sumsub API task that does NOT match a more specific skill (e.g. `create-sumsub-level`, `sumsub-create-questionnaire`, `sumsub-api-auth`). TRIGGER when the user wants to call, inspect, or debug a Sumsub API endpoint not otherwise covered — fetching applicants, listing levels, reviewing AML hits, exporting data, generating SDK tokens, anything against `api.sumsub.com`. The procedure — locate the right endpoint in the OpenAPI schema, read its request/response shape, build the payload, sign with App Token, and validate. SKIP whenever a narrower Sumsub skill already covers the request.
allowed-tools: Read, Write, Bash, Grep
---

# Sumsub — generic API fallback

A skill of last resort. The Sumsub API has ~130 endpoints. The
[OpenAPI 3.0.1 schema](https://api.sumsub.com/agents-openapi.json)
is the source of truth — read it before guessing.

## When to invoke

The user is asking for *something* against `api.sumsub.com` but none of the
specific skills apply. Examples:

- "Get the latest review status for applicant X"
- "List all questionnaires in this workspace"
- "Generate an SDK access token for user Y at level Z"
- "Mark applicant W as approved"
- "Pull the AML hits attached to this applicant"
- "What endpoint do I call to add a tag?"

If the ask clearly matches one of:

- `sumsub-api-auth` — authentication mechanics, signing debug, 401 triage.
- `sumsub-create-questionnaire` — building a `QuestionnaireDefinition`.
- `create-sumsub-level` — building an `ApplicantLevel` end-to-end.

…use that instead. This skill exists for everything else.

## Auth

Same App-Token-+-secret flow as the rest of the repo. **Sandbox tokens only.**
See [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md) for the deep dive and
signing pitfalls. Helper script `${CLAUDE_SKILL_DIR}/scripts/sumsub_curl.sh` (mirror of the auth
skill's) refuses any token that doesn't start with `sbx:`.

If the user has not supplied `SUMSUB_APP_TOKEN` + `SUMSUB_SECRET_KEY`, stop
and ask. Refuse production credentials on sight.

## Hard rule: no shotgun debugging

**Never guess endpoint paths.** Do not try `/resources/kyt/vasps`, then `/resources/kyt/travelRule/vasps`, then `/resources/vasps`, … The schema has ~1800 paths — guessing is always slower and noisier than searching. If `find_endpoint.py` returns no matches, try a different keyword or check the schema directly. The only valid reason to type a path is because the schema told you it exists.

## Procedure


### 0. The schema is auto-fetched

The helper scripts below pull the OpenAPI schema from
<https://api.sumsub.com/agents-openapi.json> on first use and cache
it for 24 hours at `~/.cache/sumsub/openapi.json` (or `$XDG_CACHE_HOME/sumsub/`).
Stale caches refresh transparently on the next invocation. **No App Token or
secret is required for the schema fetch itself** — only for the endpoints
you'll call later.

Force a refresh with `SUMSUB_SCHEMA_REFRESH=1` or by running
`${CLAUDE_SKILL_DIR}/scripts/refresh_schema.py`.

Override knobs:

- `SUMSUB_OPENAPI=/abs/path.json` — skip cache + network, use a local file.
- `SUMSUB_OPENAPI_URL=https://…` — pull from a different host (e.g. a private
  mirror).

The schema is ~750 KB / ~120 paths — if you want you can read it as whole, but you can use
the helpers grep/parse it for you. Do not try to
fabricate endpoint shapes from memory, or invent paths. 

### 1. Search the schema — always

Before anything else, run:

```bash
${CLAUDE_SKILL_DIR}/scripts/find_endpoint.py <keyword>
```

Examples:

```bash
${CLAUDE_SKILL_DIR}/scripts/find_endpoint.py vasp
${CLAUDE_SKILL_DIR}/scripts/find_endpoint.py applicants tags
${CLAUDE_SKILL_DIR}/scripts/find_endpoint.py accessTokens
```

This is the **only** correct way to find an endpoint. Do not proceed to step 2 until you have a match from the schema.

### 2. Pick the right match

Output: `METHOD path  — summary  (operationId)`. Pick the best match from the list `find_endpoint.py` returned. Show the candidate list to the user before committing if any ambiguity remains.

### 3. Inspect the operation in full

Dump request params, body schema, and response shape:

```bash
${CLAUDE_SKILL_DIR}/scripts/show_endpoint.py GET /resources/applicants/{applicantId}/one
```

Read the schema; do not guess. Note in particular:

- **Path params** — substitute before signing.
- **Query params** — must be in the request URI you sign.
- **Required fields** in the request body.
- **Auth requirements** — virtually all endpoints use `app-token` auth;
  flag if you see something different.

### 4. Build the payload

For writes, draft the JSON body and **show it to the user before sending**.
Spell out what each field means and any assumed defaults. Ask for confirmation
on anything irreversible (status changes, deletions, blacklisting).

### 5. Sign and send

```bash
${CLAUDE_SKILL_DIR}/scripts/sumsub_curl.sh GET  /resources/applicants/{applicantId}/one
${CLAUDE_SKILL_DIR}/scripts/sumsub_curl.sh POST /resources/applicants/{applicantId}/tags tags.json
```

The wrapper signs `ts + METHOD + path?query + body` with HMAC-SHA256 and
sends it to `https://api.sumsub.com`. Final line of output is `HTTP <code>`.

### 6. Validate

For state-changing calls, fetch the entity back and verify the change
actually landed. Sumsub occasionally accepts a field at the API edge and
then silently drops it (tenant entitlement gates). Report any mismatch.

For reads, surface the relevant fields to the user — don't just dump the
whole response. Most Sumsub responses are big.

## Common pitfalls

- **Path-parameter expansion in the signature.** You must sign the *resolved*
  path (`/resources/applicants/abc123/one`), not the template
  (`/resources/applicants/{applicantId}/one`). The helper script signs
  whatever string you pass — so resolve first.
- **Query-string encoding.** `+` vs `%20`, ordering, repeated keys — the
  signing string must match the wire exactly. Build the URL once and reuse.
- **GET/DELETE with an accidental body.** Some HTTP clients add `Content-Length: 0`
  or an empty body; the helper does not, but if you switch to another client,
  watch for it — empty body means *append nothing* to the signing string.
- **Pagination.** Many list endpoints use cursor or offset paging — check
  the schema. Don't claim "no results" from a single page.

## See also

- [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md) — full auth reference and
  `401 Invalid signature` triage.
- [Sumsub API reference](https://docs.sumsub.com/reference) — human-readable
  docs that often lag the schema; cross-check.
