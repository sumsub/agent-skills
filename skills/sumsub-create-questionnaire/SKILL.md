---
name: sumsub-create-questionnaire
description: Create or update a Sumsub KYC questionnaire definition. POST `/resources/api/agent/questionnaires` to create new (fails 409 if id exists), PATCH same path to update (fails 404 if id is unknown), GET `/resources/api/agent/questionnaires/{id}` to read one back. TRIGGER when the user asks to "create / add / build / update / edit a Sumsub questionnaire", or supplies a list of questions / sections meant for a Sumsub applicant flow, or references a questionnaire id / definition to be POSTed or PATCHed. SKIP for other Sumsub entities (levels, workflows, applicants), questionnaire data (answers) submission, or non-Sumsub form builders.
allowed-tools: Read, Write, Bash
---

# Sumsub — Create Questionnaire

Builds a questionnaire definition JSON payload from a compact spec, POSTs it
to the Sumsub API, and reports the resulting `id` (client-supplied slug) and
`_id` (server-assigned identifier).

## Endpoints

| Method | Path | When |
|---|---|---|
| `POST` | `/resources/api/agent/questionnaires` | Create a new questionnaire. **Fails with `409 CONFLICT`** if `id` already exists. |
| `PATCH` | `/resources/api/agent/questionnaires` | Update an existing questionnaire (by `id` in body). **Fails with `404 NOT_FOUND`** if no such questionnaire. |
| `GET` | `/resources/api/agent/questionnaires/{id}` | Read one questionnaire (verify what landed; resolve `title` from a known `id`). |
| `GET` | `/resources/api/questionnaires/list` | List all questionnaires. (Stays on the non-agent path.) |
| `GET` | `/resources/api/questionnaires/usedByLevels` | List questionnaires with the levels that reference them. (Stays on the non-agent path.) |

All require permission `manageClientSettings`. Body shape is the
[questionnaire schema](references/questionnaire-schema.md) — client-settable
fields only (`clientId`, `createdAt`, audit metadata are server-managed).

> **POST vs PATCH** — these are now strict. POST refuses an existing `id`;
> PATCH refuses a missing one. The pre-INT-4893 "single POST upsert" behavior
> is gone — always pick the right verb up front (call GET /{id} first if
> unsure whether the questionnaire exists).

## Auth — App Token + secret (sandbox only)

This skill talks to the public Sumsub API and signs each request per
[the authentication reference](https://docs.sumsub.com/reference/authentication).
The full how-it-works writeup lives in the [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md)
skill — read it if you hit `401 Invalid signature`.

> **⚠️ Sandbox tokens only.** Do **not** accept or use a production App Token
> here. If the user offers one, refuse and ask them to generate a sandbox
> pair at <https://cockpit.sumsub.com/checkus/home?sbx=true> (**Connect
> Sumsub to your AI agent** -> **Build & configure** -> **Generate token**).
> Token + secret are shown once — copy both before closing the dialog. The helper script
> enforces this — it rejects tokens that don't start with `sbx:`.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

## Tenant entitlements

Creating a questionnaire requires the `QUESTIONNAIRE` entitlement. Before doing anything else, invoke the `sumsub-check-permissions` skill and verify that `QUESTIONNAIRE` is present as a key in the `allowedChecks` map.

**If `QUESTIONNAIRE` is not in `allowedChecks` — stop immediately.** Do not build or POST the questionnaire. Tell the user the entitlement is missing and that they need to contact their CSM or Sumsub support to get it enabled.

## Procedure

0. **Fetch tenant entitlements** — see section above.
1. **Gather spec.** Map the user's questions into the compact spec format below — *never* hand-write the full localized payload.
2. **Validate** — confirm `id` is a unique slug, every item has a supported `type`, every conditional reference points to a real `<sectionId>.<itemId>`.
3. **Generate payload** by running `${CLAUDE_SKILL_DIR}/scripts/build_questionnaire.py` with the spec on stdin. Inspect the output briefly.
4. **Create vs. update** — POST/PATCH scripts accept the payload as a path argument **or** on stdin (pipe it from `build_questionnaire.py` for a one-liner):
   - **New** — POST via `${CLAUDE_SKILL_DIR}/scripts/post_questionnaire.sh <payload.json>` (or `… | post_questionnaire.sh -`). If the user already supplied an `id` they used before, GET it first via `${CLAUDE_SKILL_DIR}/scripts/get_questionnaire.sh` to avoid a `409 CONFLICT`.
   - **Update existing** — GET via `${CLAUDE_SKILL_DIR}/scripts/get_questionnaire.sh` first so the user sees what they're overwriting; then PATCH via `${CLAUDE_SKILL_DIR}/scripts/patch_questionnaire.sh <payload.json>`.
5. **Build the dashboard link.** Read `id` and `clientId` from the response body (both fields are present on the persisted questionnaire) and format:

   ```
   https://cockpit.sumsub.com/checkus/sdkIntegrations/questionnaireDetails/<id>?clientId=<clientId>&sbx=true
   ```

   The `sbx=true` query param targets the **Sandbox** workspace — it is the canonical sandbox link param shared across all skills.
6. **Report** — lead with the human-readable title:
   - `title`, section/item count, country/lang coverage if relevant.
   - **Dashboard link** as a clickable markdown link.
   - Final line: `Questionnaire ID (for level wiring / future PATCH): <id>`.

   Surface any 4xx with the `description` field from the error body. For `409 CONFLICT` on POST — suggest PATCH instead.

## Compact spec format

JSON or YAML accepted on stdin. English titles are auto-wrapped into `localizedTitle` / `localizedDesc`. Use `condition` strings for show/hide logic — see [references/questionnaire-schema.md](references/questionnaire-schema.md) for syntax.

```json
{
  "id": "source-of-funds",
  "title": "Source of Funds",
  "desc": "Optional one-liner shown to applicants.",
  "showTitleAsStepName": true,
  "sections": [
    {
      "id": "primary",
      "title": "Primary Source",
      "desc": "Optional section description.",
      "condition": null,
      "items": [
        {"id": "main", "title": "Main source?", "type": "select", "required": true,
         "options": [["salary","Salary"],["business","Business"],["other","Other"]]},
        {"id": "other", "title": "Specify", "type": "text",
         "condition": "primary.main = other"}
      ]
    }
  ]
}
```

### Supported item types
`text`, `textArea`, `date`, `dateTime`, `bool`, `select`, `phone`, `selectDropdown`, `multiSelect`, `countrySelect`, `countryMultiSelect`, `fileAttachment`, `multiFileAttachments`.

`select` / `selectDropdown` / `multiSelect` require `options: [[value, title], ...]`.

## Outputs

On success, lead with the human-readable info:
- `title`, section/item count, `createdAt`.
- **Dashboard link**: `https://cockpit.sumsub.com/checkus/sdkIntegrations/questionnaireDetails/<id>?clientId=<clientId>&sbx=true`. Render as a clickable markdown link so the user can jump to the entity. Both `id` and `clientId` are in the POST response body; `sbx=true` targets the Sandbox workspace.
- Finally, on its own line: `Questionnaire ID (slug, for level wiring / future PATCH): <id>`.

On failure: print HTTP status + `description`/`type` from the error envelope; do not retry blindly. On `409 CONFLICT` from POST — suggest PATCH for an update.

### Names, not ids, in user-facing messages

This applies to **every** message about the questionnaire — pre-POST summary, mid-flow status updates, diagnostics — not only the final report:

- Refer to the questionnaire by `title` ("Applicant basics"), not by its `id` slug, in prose.
- The slug `id` belongs only on the final dedicated line (`Questionnaire ID (slug): <id>`) — that line is the one place a raw id is correct, because the user needs to copy it into a level's `questionnaireDefId`.
- When mentioning sections or items, prefer their `title` over their `id`.

### Hand-off to `sumsub-create-level`

The `id` returned here (the questionnaire slug) is what you pass on a level's `QUESTIONNAIRE` doc-set. The level skill accepts it as `questionnaireDefId` (canonical) or `questionnaireId` (alias):

```json
{
  "type": "QUESTIONNAIRE",
  "questionnaireDefId": "<id from this skill>"
}
```

See [`sumsub-create-level/examples/with-presets.json`](../sumsub-create-level/examples/with-presets.json).

## See also

- [references/questionnaire-schema.md](references/questionnaire-schema.md) — full field list, condition expressions, gotchas.
- [examples/source-of-funds.json](examples/source-of-funds.json) — multi-section spec with conditional branches.
