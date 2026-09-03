---
name: sumsub-create-aml-resolution-rules
description: Create, edit, reorder, delete, and publish Sumsub AML Resolution Rules (the AML Resolution Rule Chain) that auto-review AML screening hits. TRIGGER when the user wants to auto-clear false positives, auto-confirm true positives, carry over previous AML reviews, tag AML hits, or set up / inspect / publish the AML rule chain. SKIP for transaction-monitoring (KYT) rules, workflow routing, or AML check settings on a level (separate skills cover those).
allowed-tools: Read, Write, Bash
---

# Sumsub — Create AML Resolution Rules

Builds AML resolution rules from a compact spec, upserts them into the tenant's **draft** AML rule chain via the agent API, and (optionally) publishes the draft to make it live. The chain (also called the **AML Resolution Rule Chain**) auto-reviews incoming AML screening hits: each rule, in order, is evaluated against every not-yet-reviewed hit, and on match sets the hit's review (match status / risk level / whitelisted / note) and/or tags the case.

Every network step goes through one signed client, `${CLAUDE_SKILL_DIR}/scripts/aml_rules_api.py` (`draft`, `published`, `archive`, `library`, `upsert`, `reorder`, `delete`, `publish`); rule payloads are assembled by `${CLAUDE_SKILL_DIR}/scripts/build_aml_rule.py`.

## Endpoints

All under `/resources/api/agent/amlResolutionRules`. There is **one rule chain per tenant**, versioned as `draft → published → archived` revisions. (Each row maps to an `aml_rules_api.py` subcommand — you never call these paths by hand.)

| Method | Path | Subcommand | When |
|---|---|---|---|
| `GET` | `/draft` | `draft` | Read the editable revision. Auto-creates a draft from the published revision (or empty) — never 404s for an enabled tenant. Carries `notices[]`. |
| `GET` | `/published` | `published` | Read the live revision (404 if nothing published yet). |
| `GET` | `/archive` | `archive [marker]` | Revision history, marker-paginated. **Rate limit 5/min — don't poll.** |
| `GET` | `/library` | `library` | Ready-made rule templates, grouped by category. |
| `POST` | `/draft/rules` | `upsert` | Upsert one rule: omit `id` to create (appended at the end of the chain), include an existing `id` to replace that rule. Response = full draft with recomputed `notices[]`. |
| `PUT` | `/draft/rules/order` | `reorder` | Reorder: body `{"ruleIds": [...]}` must list **every** rule id exactly once. |
| `DELETE` | `/draft/rules/{id}` | `delete <id>` | Remove one rule from the draft by id. **Idempotent** — deleting an id not in the draft still succeeds. See the consent policy below. |
| `POST` | `/draft/publish` | `publish` | Go live. Refused while any `error`-level notice exists. Previous published revision auto-archives. |

> **Publishing via the API is for the integration phase.** Once the integration is considered active, the API may **refuse to publish** (a `4xx`); the chain must then be reviewed and published by a human from the Sumsub web UI. Treat a publish refusal as expected at that stage, not an error to work around — report it and point the user to the web UI.

Token requirements beyond the usual: these are agent endpoints, so the App Token must be **AI-purpose** (created from the AI token page in the dashboard UI) and carry the `manageAmlCases` + `manageClientSettings` permissions. Symptoms of getting this wrong:

- `403 "This endpoint is not allowed for this type of token"` → the token is a regular App Token, not an AI one. Ask the user to mint an AI token.
- `404 "API is not available"` on every endpoint → the AML Resolution Rules API is not enabled for this tenant. **Stop immediately** — tell the user to contact their CSM or Sumsub support; do not retry other endpoints.

## ⚠️ Publishing affects LIVE production

**The AML Resolution Rule Chain is shared across live and sandbox** — only the AML cases / applicants are isolated, not the chain itself. Publishing changes the chain that auto-reviews **real production AML screening hits** (clearing false positives, confirming true positives, whitelisting) — a sandbox `sbx:` token does **not** make this safe. Everything up to publish is safe: reading the draft, upserting, reordering, and deleting rules all touch only the **draft**, which reviews nothing until it's published.

So publish **only on explicit user request**, and know it can be **refused by the backend**: once the chain is active — too many applicants have already been processed / the integration is complete — the API rejects the publish (a `4xx`). That is expected, not an error to work around: report it and tell the user to publish from the Sumsub web UI (see the Endpoints note).

## Auth — App Token + secret (sandbox only)

This skill talks to the public Sumsub API and signs each request per
[the authentication reference](https://docs.sumsub.com/reference/authentication).
The full how-it-works writeup lives in the [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md)
skill — read it if you hit `401 Invalid signature`.

> **⚠️ Sandbox tokens only.** Do **not** accept or use a production App Token
> here — these rules auto-review real AML hits. If the user offers a prod
> token, refuse and ask them to generate a sandbox pair at
> <https://cockpit.sumsub.com/checkus/home?sbx=true> (**Connect Sumsub to
> your AI agent** -> **Build & configure** -> **Generate token** — that page
> mints the **AI** token these endpoints require, see above). Token + secret
> are shown once — copy both before closing the dialog. `aml_rules_api.py` enforces this — it rejects tokens
> that don't start with `sbx:`.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox **AI** App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

## How the chain executes (keep this in mind while designing rules)

1. Rules run **top to bottom** — order matters.
2. Each rule is evaluated against **every hit that is not yet reviewed**. A hit that gets a `matchStatus` (from moderation or an earlier rule) is skipped by later rules.
3. Effects are visible **mid-run**: tags and recomputed `screening.answer` / `screening.tags` / `screening.matchStatuses` from earlier rules are seen by later ones — this enables chaining (rule A tags `match_tin`, rule B reacts to `screening.tags containsAny ["match_tin"]`).
4. Put specific, decisive rules (ID matches, previous-review carry-over) **before** broad clean-up rules — a broad `false_positive` rule placed first steals hits from preciser rules below it.

## Precondition: AML screening must actually be running

This chain acts **only on hits produced by AML screening**. If screening isn't running, the rules are inert — they evaluate against nothing. Two independent gates decide whether screening runs on a given applicant level:

1. **Tenant entitlement `WATCHLISTS`** — all-or-nothing, tenant-wide. Verify it by invoking the [`sumsub-check-permissions`](../sumsub-check-permissions/SKILL.md) skill. `WATCHLISTS` present → AML screening is available and **on by default** on every level. `WATCHLISTS` absent → AML screening is **off for the entire tenant**; no applicant-level setting can turn it on, and this rule chain will **never see a hit**.
2. **Per-level opt-out `disableWatchlists`** — only relevant once gate 1 passes. Screening runs on a level unless that level sets the top-level `disableWatchlists: true` (how a client carves out levels that shouldn't be screened). This is the [`sumsub-create-level`](../sumsub-create-level/SKILL.md) skill's concern, not this one.

| `WATCHLISTS` entitlement | Level `disableWatchlists` | Screening runs on that level? | Chain acts on its hits? |
|---|---|---|---|
| absent | (any) | **No** — off tenant-wide | No |
| present | absent / `false` | **Yes** (default) | Yes |
| present | `true` | **No** — level opted out | No |

The chain is **one per tenant** and acts on hits from **every** level where screening runs — it is not scoped to a level. So confirm gate 1 **before** building rules (step 0). If `WATCHLISTS` is missing, anything you write here stays dormant until the entitlement is enabled.

## Tags bridge into applicant workflows

Rule tags are **common applicant tags** — tenant-wide, not AML-only. They don't just chain within the AML run: they also surface in **applicant workflow** conditions as `checks.personWatchlist.tags` (individuals) and `checks.companyWatchlist.tags` (companies). That makes a tag the hand-off point between the rule chain and a workflow: the rule chain flags a nuanced situation, the workflow routes on it. Example:

1. AML rule — condition "the hit carries the `pep` risk label and the applicant is under 30", tags action `["youngPep"]`.
2. Workflow edge — a `condition` testing that `checks.personWatchlist.tags` contains `youngPep` → a manual-review node.

Both skills author the **same Condition AST** (see below), so the two halves read alike. When the user's goal includes routing or actions downstream of screening, set the tag here and point them to [`sumsub-create-workflow`](../sumsub-create-workflow/SKILL.md) for the routing half.

## Procedure

0. **Confirm AML screening is enabled for the tenant** (see *Precondition*). Invoke the [`sumsub-check-permissions`](../sumsub-check-permissions/SKILL.md) skill and verify `WATCHLISTS` is among the tenant's allowed entitlements. If it's **absent**, AML screening is off tenant-wide, so this rule chain will never fire: tell the user plainly (the entitlement is enabled by their CSM / Sumsub support), and get **explicit confirmation** before proceeding — do not silently build a chain that does nothing. If present, proceed.
1. **Read the draft**: `${CLAUDE_SKILL_DIR}/scripts/aml_rules_api.py draft`. This is also the availability check — on `404 "API is not available"` or `403`, stop and report (see Endpoints above). Review the existing rules: if a rule with the same intent already exists, offer to **update it by `id`** instead of appending a duplicate — upsert has no name deduplication. Note which rule ids exist *before* you make changes — you'll need that to honor the delete consent policy.
2. **Check the library first**: `${CLAUDE_SKILL_DIR}/scripts/aml_rules_api.py library`. If a ready-made template matches the user's intent, start from its `rule` definition — strip the `id`, adjust, and continue. Check the template's `vendors` list against the AML vendor the tenant uses.
3. **Write the rule spec** (below). Author the `condition` as the **real Condition AST**, directly — there is no expression mini-language (see *Authoring conditions*). **Scope the rule to an entity type with an `input.entityType` criterion** (default individual — see *Authoring conditions*). Verify every `exp` path against [references/aml-rules-context-fields.md](references/aml-rules-context-fields.md), and any enum-backed field's allowed values against [references/aml-rules-enumerations.md](references/aml-rules-enumerations.md) — unknown paths produce `unknownField` error notices that block publishing.
4. **Assemble the rule payload** with `${CLAUDE_SKILL_DIR}/scripts/build_aml_rule.py` — compact spec on stdin → full rule JSON on stdout. The builder is a thin assembler: it passes the `condition` AST through, assembles the review/tags actions, validates operators / the `matchStatus` enum / the emptyAction guard, and errors here (before any network call) on a typo or a malformed AST.
5. **Show the resolved payload to the user and get explicit confirmation** before the first upsert. If the rule's `tags` action introduces a tag that doesn't exist yet, call that out explicitly: upserting will create it as a **tenant-wide applicant tag** (visible in dashboard filters, workflows, everywhere) — confirm the name is one worth keeping (clear, concise, reusable) or reuse an existing tag instead.
6. **Upsert** via `${CLAUDE_SKILL_DIR}/scripts/build_aml_rule.py < spec.json | ${CLAUDE_SKILL_DIR}/scripts/aml_rules_api.py upsert` → response is the **full draft** with recomputed `notices[]`. Repeat steps 3–6 for each rule when creating several. Record the id the server assigns each rule you create — that's how you know it's yours (step 9).
7. **Inspect `notices`**. `error` notices (e.g. `invalidTag`, `unknownField`, `unknownFunction`) block publishing — fix the rule and re-upsert with its `id`. `warning`/`info` are advisory; surface them. See the notice key table in [references/aml-resolution-rules-schema.md](references/aml-resolution-rules-schema.md).
8. **Order the chain.** New rules land at the end. If the evaluation order needs changing, pass the full permutation: `echo '{"ruleIds": [...]}' | ${CLAUDE_SKILL_DIR}/scripts/aml_rules_api.py reorder`.
9. **Delete rules — only per the consent policy below.** `${CLAUDE_SKILL_DIR}/scripts/aml_rules_api.py delete <ruleId>`.
10. **Publish only on explicit request** (see the "Publishing affects LIVE production" note): `${CLAUDE_SKILL_DIR}/scripts/aml_rules_api.py publish`. Publishing makes the chain live against real AML hits **across live and sandbox** — never publish without the user asking; until then the draft is dormant. The backend may **refuse** the publish once the chain is active (too many applicants already processed / integration complete) — a `4xx`. That's expected: report it and direct the user to publish from the Sumsub web UI (see the Endpoints note).
11. **Report** (lead with rule names, never bare ids):
    - The rule chain in evaluation order (names), the draft `revision`, and a notices summary.
    - Draft (editable) view: [https://cockpit.sumsub.com/checkus/sdkIntegrations/globalSettings/amlScreening?revision=draft&tab=amlRules&sbx=true](https://cockpit.sumsub.com/checkus/sdkIntegrations/globalSettings/amlScreening?revision=draft&tab=amlRules&sbx=true)
    - Published (live) view, after publishing: [https://cockpit.sumsub.com/checkus/sdkIntegrations/globalSettings/amlScreening?revision=published&tab=amlRules&sbx=true](https://cockpit.sumsub.com/checkus/sdkIntegrations/globalSettings/amlScreening?revision=published&tab=amlRules&sbx=true)
    - Render both as clickable markdown links; `sbx=true` targets the Sandbox workspace.
    - End with a dedicated `Rule id (for future updates / reorder): <id>` line — the one place a raw id belongs in your output.
    - On failure: surface Sumsub's `description` / `errorName` verbatim.

### Deleting rules — consent policy

The `delete` subcommand removes a rule from the draft permanently (it's archived with the revision, but gone from the editable chain). Apply this gate:

- **A rule you created in this session** — delete it freely when it was a mistake, the user asked you to replace it, or you're iterating on your own work. (Updating in place by `id` is usually better than delete-then-recreate, because it preserves the rule's position; reach for delete when the rule should genuinely go away.)
- **Any rule you did not create** — a pre-existing rule, one from an earlier session, or one a human authored — delete **only with explicit user consent for that specific rule**. Name the rule (by its `name`) and confirm before deleting. Never delete someone else's rule as a side effect of "cleaning up" or "rebuilding" the chain.
- When unsure whether a rule is yours, treat it as not yours and ask.

Deleting is idempotent and returns the full draft with recomputed `notices[]` — re-inspect them afterward (removing a rule can change which tags/fields the remaining rules still justify).

## Rule spec format (JSON on stdin)

```jsonc
{
  "name": "Auto-clear hits with incompatible date of birth",   // required
  "description": "Optional free-form description",
  "id": "existing-rule-id",            // only when updating an existing rule

  // condition — the real Sumsub Condition AST, authored directly (see below).
  "condition": {
    "or": [
      { "and": [
        { "op": "ne",   "args": [ { "exp": "input.entityType" }, { "lit": "\"company\"" } ] },   // individual-only — scope every rule (see Authoring conditions)
        { "op": "eq",   "args": [ { "exp": "screening.vendor" }, { "lit": "\"complyAdvantageCSOM\"" } ] },
        { "op": "eq",   "args": [ { "exp": "match.dobs.hasData" }, { "lit": "true" } ] },
        { "op": "call", "args": [ { "exp": "dobsIncompatible" }, { "exp": "match.dobs" }, { "exp": "input.dob" }, { "lit": "\"weakContainment\"" } ] }
      ] }
    ]
  },

  // Review action — what to set on matched hits (every field optional):
  "review": {
    "matchStatus": "false_positive",   // unknown | potential_match | false_positive | true_positive
    "riskLevel": "LOW",                // vendor-specific — omit when unsure
    "whitelisted": true,               // accept the risk: allows approval despite the hit
    "note": "Cleared automatically: DoB mismatch"
    // OR the whole-review form (replaces all per-field keys):
    // "expression": "match.previousReview"   // carry over the previous screening's decision
  },

  // Tags added to the AML case when the rule matches. These are common applicant
  // tags (tenant-wide, usable everywhere — not AML-only). A tag that doesn't exist
  // yet is created automatically on upsert: prefer reusing an existing tag, and
  // name new ones clearly and concisely (e.g. "youngPep", not "rule3_tag"):
  "tags": ["auto_cleared_dob"]
}
```

A rule needs `review` and/or `tags` — neither yields an `emptyAction` error notice. Review fields take a scalar (the builder JSON-encodes it into a `{lit}`) or an explicit `{"exp": "..."}` / `{"lit": "..."}` to compute or supply the value directly.

## Authoring conditions

A rule's `condition` is the **real Sumsub Condition AST, written directly** — the *same* shape and rules as workflow edge conditions, so the two skills stay aligned. There is **no expression mini-language** (the old `condition: "screening.vendor = …"` string and `conditionRaw` key were removed; the builder rejects both with a pointer here).

> **⚠️ Scope every rule to an entity type.** Individual and company matches expose different fields and read differently, so a rule built for one can misfire on the other. **Each rule MUST carry an `input.entityType` criterion** — infer the target from the rule's intent (person name / DoB / PEP signals → individual; company name / KYB signals → company), and **default to individual** when unsure:
> - Individual (the usual case): `{ "op": "ne", "args": [ {"exp": "input.entityType"}, {"lit": "\"company\""} ] }` — entityType ≠ company.
> - Company / organization: `{ "op": "eq", "args": [ {"exp": "input.entityType"}, {"lit": "\"company\""} ] }`.
>
> Omit it **only** for a deliberately entity-agnostic rule (rare — e.g. "whitelist every `sanctions` hit from country X"). Most library templates already carry this criterion — keep it when you adapt one.

```jsonc
{
  "or": [                                  // OR of AND-groups; first matching branch wins
    { "and": [
      { "op": "eq", "args": [ {"exp": "screening.vendor"}, {"lit": "\"complyAdvantageCSOM\""} ] },
      { "op": "in", "args": [ {"exp": "input.country"},    {"lit": "[\"BRA\", \"ARG\"]"} ] }
    ] }
  ]
}
```

- **`{exp: "<path>"}`** — an expression path, verbatim (from [references/aml-rules-context-fields.md](references/aml-rules-context-fields.md)). It's the left side of a comparison, and also the **right** side for field-to-field checks (`{exp: "match.analysis.parentName"}`).
- **`{lit: "<json>"}`** — a literal, supplied **already JSON-encoded as a string** (the form the API stores): `"\"complyAdvantageCSOM\""`, `"2"`, `"true"`, `"[\"pep\", \"sanctions\"]"`. An un-encoded literal (`{lit: "BRA"}`) is rejected by the API, so the encoding is required.
- **`op`** is one of the comparison operators (`eq ne lt lte gt gte in notIn contains notContains containsAny notContainsAny containsAll containsOnly startsWith endsWith match empty notEmpty eqIgnoreCase …`; full set in [references/aml-resolution-rules-schema.md](references/aml-resolution-rules-schema.md)). The builder validates every `op` against its known set.
- **Set membership on list fields** (`match.riskLabels`, `screening.tags`, `match.complyAdvantage.matchTypes`): `contains` / `containsAny` = *has* the value(s); `containsAll` = *has all of*; **`containsOnly` = *has nothing but* the listed values**. To match "**only** label X" (e.g. adverse-media-only hits) use `containsOnly ["X"]` — **never** `notContainsAny [the-other-labels]`, which leaks because it silently assumes you enumerated the whole closed vocabulary (the risk-label set is exactly six — see [references/aml-rules-enumerations.md](references/aml-rules-enumerations.md#AmlRiskLabel)).
- **`call`** invokes a built-in function — the one operator AML conditions have that workflows don't. The first arg is the function name as `{exp: "namesIncompatible"}`, the rest are its arguments: `{op: "call", args: [{exp: "dobsIncompatible"}, {exp: "match.dobs"}, {exp: "input.dob"}, {lit: "\"strict\""}]}`. Functions and their signatures: [references/aml-resolution-rules-schema.md](references/aml-resolution-rules-schema.md).
- **Negation** is expressed with the `not*` operators (`notIn`, `notContains`, `notContainsAny`, `ne`, `notEmpty`, …) — do **not** set a `negate` flag; a top-level `condition.negate` is rejected (UI-unsupported), matching the workflow skill.
- **Dates**: any `Date` field (`input.dob`, `match.previousReview.modifiedAt`, `match.sources.latestEndDate`) exposes `.ageInDays` / `.ageInYears` / `.year` etc. — e.g. `{op: "lt", args: [{exp: "match.previousReview.modifiedAt.ageInYears"}, {lit: "2"}]}`.

The full `Condition`/`And`/`Criterion` AST, literal-encoding rules, operator list, and built-in function signatures live in [references/aml-resolution-rules-schema.md](references/aml-resolution-rules-schema.md); valid `exp` paths are in [references/aml-rules-context-fields.md](references/aml-rules-context-fields.md) and enum-field values in [references/aml-rules-enumerations.md](references/aml-rules-enumerations.md) (both indexed by [references/aml-rules-expressions.md](references/aml-rules-expressions.md)).

## Worked examples

- [`examples/minimal.json`](examples/minimal.json) — tag-only rule (`containsOnly` on risk labels).
- [`examples/auto-clear-dob-mismatch.json`](examples/auto-clear-dob-mismatch.json) — `call` functions + vendor match types; the most common auto-clear topology.
- [`examples/reuse-previous-review.json`](examples/reuse-previous-review.json) — whole-review `expression` form carrying over a previous decision, with a date-age condition. Also the rare **entity-agnostic** rule (carrying a prior decision reads the same for individuals and companies) — the one case that needs no `input.entityType` filter.

## See also

- [references/aml-resolution-rules-schema.md](references/aml-resolution-rules-schema.md) — endpoints with rate limits, every field and enum, condition AST shape, operator list, built-in function signatures, notice message keys, execution model.
- [references/aml-rules-expressions.md](references/aml-rules-expressions.md) — expression-reference **index** + preamble (root variables, `applicant`/`Date` shapes, the enum caveat). Points to the two data files below; all three are lookup databases, don't read end-to-end.
- [references/aml-rules-context-fields.md](references/aml-rules-context-fields.md) — every legal `exp` path with its type (`## Types` / `## Index` / `## Functions`).
- [references/aml-rules-enumerations.md](references/aml-rules-enumerations.md) — allowed **values** for the closed-enum fields (risk labels, match statuses, PEP institution kinds, match types, …).
- [`sumsub-create-workflow`](../sumsub-create-workflow/SKILL.md) — authors the **same Condition AST** in workflow edge conditions; its expressions reference covers the `applicant` / `applicantIdDoc` shapes.
