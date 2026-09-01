# AML resolution rules — full schema reference

Field-level reference for the AML Resolution Rules chain (also called the **AML Resolution Rule Chain**): the per-tenant, ordered list of rules that auto-review incoming AML screening hits. Read `SKILL.md` first for the procedure; come here for exact field semantics, enums, and limits.

## Concept & lifecycle

There is **one rule chain per tenant**, versioned by revisions:

| `revisionStatus` | Meaning |
|---|---|
| `draft` | The editable revision. All rule changes (upsert / reorder) apply here. Auto-created on first read or write as a copy of the published revision (or empty if nothing is published). |
| `published` | The revision applied to live AML screening. Read-only — to change it, edit the draft and publish. Exactly one revision is published at a time. |
| `archived` | Previous published revisions. History only. |

Transitions: `draft → published` (publish; the old published revision auto-archives). There is no unpublish — to deactivate rules, publish a draft with the rules removed/changed.

**The chain is shared across live and sandbox** — only the AML cases / applicants are isolated, not the chain. Publishing (even with a sandbox token) makes the chain auto-review **real production** AML hits. Everything before publish touches only the draft, which reviews nothing. Publish only on explicit user request; the backend refuses the publish once the chain is active (too many applicants already processed / integration complete), and the user must then publish from the web UI — see `SKILL.md`.

## Endpoints

All under `https://api.sumsub.com/resources/api/agent/amlResolutionRules`. App Token + HMAC signing (see `SKILL.md` auth section). The token must be **AI-purpose** and carry `manageAmlCases` + `manageClientSettings`.

| Method | Path | Rate limit | Semantics |
|---|---|---|---|
| `GET` | `/draft` | 60/min | Returns the draft (auto-creates from published / empty — never 404s for an enabled tenant). Includes current `notices[]`. |
| `GET` | `/published` | 30/min | The live revision. `404` when nothing has been published yet. |
| `GET` | `/archive[?forwardMarker=...]` | **5/min** | Archived revisions, newest first, 10 per page. Marker-paginated: pass the response's `forwardMarker` back to get the next page; absent marker = last page. Heavily rate-limited — history, not something to poll. |
| `GET` | `/library` | 10/min | Ready-made rule templates grouped by category. |
| `POST` | `/draft/rules` | 60/min | **Upsert one rule.** Omit `id` → create: server assigns the id and appends the rule at the **end** of the evaluation order. Provide an existing `id` → update that rule in place (the request body's fields are written as given; this is a whole-rule replace, not a merge — send the full rule). Response = the full draft with freshly recomputed `notices[]`. |
| `PUT` | `/draft/rules/order` | 60/min | Body `{"ruleIds": [...]}` — a **complete permutation** of every rule id currently in the draft, exactly once each. Partial lists are rejected. `404` when no draft exists. |
| `DELETE` | `/draft/rules/{id}` | 20/min | Remove one rule from the draft by id. **Idempotent** — deleting an id not in the draft leaves the draft unchanged and still succeeds. `404` when no draft exists. Response = the full draft with recomputed `notices[]`. One rule at a time; no bulk delete. The skill gates this behind a consent policy — see `SKILL.md`. |
| `POST` | `/draft/publish` | 5/min | Publishes the draft. Refused while the draft has any `error`-level notice. `404` when no draft exists. **Intended for the integration phase**: once the integration is active, the API may refuse to publish, and the chain must be reviewed and published manually from the Sumsub web UI. |

Errors:
- `404 "API is not available"` on every endpoint → the AML Resolution Rules API is not enabled for this tenant. Stop and tell the user to contact their CSM or Sumsub support.
- `403 "This endpoint is not allowed for this type of token"` → the App Token is not AI-purpose. The user needs to mint an **AI** App Token (AI token page in the dashboard UI).

## Rule chain revision object

```jsonc
{
  "id": "6650...",                  // id of this revision
  "revision": 3,                    // increases with each new revision
  "revisionStatus": "draft",        // draft | published | archived
  "created":   {"date": "...", "clientSubject": "..."},   // action trails: who/when
  "modified":  {"date": "...", "clientSubject": "..."},
  "published": {"date": "...", "clientSubject": "..."},   // present once published
  "archived":  {"date": "...", "clientSubject": "..."},   // present once archived
  "rules": [ ... ],                 // the rules, in evaluation order (max 100)
  "notices": [ ... ]                // validation findings (max 100)
}
```

## Rule object

```jsonc
{
  "id": "...",                  // unique within the rule chain; omit on create
  "name": "...",                // required, ≤1000 chars — human-readable rule name
  "description": "...",         // optional, ≤3000 chars
  "condition": { ... },         // Condition AST selecting the hits the rule applies to
  "review": { ... },            // review action applied to matched hits
  "tags": {"tags": ["..."]}     // applicant/case tags added when the rule matches (≤100)
}
```

A rule must have a `review` and/or `tags` action — neither present yields an `emptyAction` error notice.

## Condition AST

OR of ANDs of criteria — the same `Condition` shape workflow edge conditions use, **authored directly** (there is no expression mini-language; the builder validates and passes it through):

```jsonc
{
  "or": [                       // 1–30 branches; first matching branch wins
    {
      "and": [                  // 1–30 criteria, all must hold
        {"op": "eq", "args": [{"exp": "screening.vendor"}, {"lit": "\"complyAdvantageCSOM\""}]}
      ]
    }
  ]
}
```

Each criterion: `{"op": <operator>, "args": [<arg>, ...]}` with 1–10 args. An arg is either:
- `{"exp": "<dotted path>"}` — an expression path from `aml-rules-context-fields.md` (values for enum-backed fields in `aml-rules-enumerations.md`), ≤512 chars; or
- `{"lit": "<JSON-encoded value>"}` — a literal, ≤8192 chars. **Lit values are JSON-encoded strings**: `"\"USA\""` (string), `"3"` (number), `"true"` (boolean), `"[\"pep\",\"sanctions\"]"` (string array).

**Negation** is expressed with the `not*` operators (`notIn`, `notContains`, `notContainsAny`, `ne`, `notEmpty`, …), not a flag. A top-level `Condition.negate` is **not supported** (UI-unsupported, and the builder rejects it) — matching the workflow skill.

### Operators

| `op` | Args | Meaning |
|---|---|---|
| `eq` / `ne` | exp, value | Equal / not equal (value = lit or another exp) |
| `eqIgnoreCase` / `neIgnoreCase` | exp, value | Case-insensitive equal / not equal |
| `eqOrNull` / `eqIgnoreCaseOrNull` | exp, value | Equal, also true when the field is null |
| `gt` / `gte` / `lt` / `lte` | exp, value | Numeric / date comparison |
| `match` / `notMatch` | exp, lit | Regex match / non-match |
| `in` / `notIn` | exp, lit array | Value is / is not one of the listed values |
| `startsWith` / `notStartsWith` | exp, lit | String prefix |
| `endsWith` / `notEndsWith` | exp, lit | String suffix |
| `empty` / `notEmpty` | exp | Field is absent-or-empty / present |
| `contains` / `notContains` | exp, value | The list *has* / *does not have* this one value. "Hit carries `adverseMedia`" → `contains ["adverseMedia"]`. |
| `containsAny` / `notContainsAny` | exp, lit array | The list has *at least one of* / *none of* these values (set intersection). |
| `containsAll` | exp, lit array | The list has *every* listed value (listed values ⊆ field). |
| `containsOnly` | exp, lit array | The list has *nothing outside* these values (field ⊆ listed values) — i.e. the field's values are **only** these. "Adverse-media-**only** hit" → `containsOnly ["adverseMedia"]`. |

> **Expressing "only X" on a list field** (risk labels, tags, match types). Use `containsOnly ["X"]`. Do **not** approximate it by excluding the other values (`notContainsAny [...]`): that forces you to enumerate the entire remaining vocabulary and silently leaks the moment one value is missed or the vocabulary grows — this is a common, hard-to-spot bug. `containsOnly` is the closed-set complement done correctly (equivalently: the listed values `containsAll` the field). For risk labels the closed set is the six in [`aml-rules-enumerations.md`](aml-rules-enumerations.md#AmlRiskLabel).
| `call` | exp (function name), then function args | Built-in function call — see below |

### Built-in functions (`op: call`)

The first arg is the function name as an `{"exp": ...}`; remaining args follow the function signature (exp paths or JSON-encoded lits):

| Function | Signature | Meaning |
|---|---|---|
| `namesCompatible` | `(match, name, country, comparisonMode, compareAlternativeNames)` | True when the match's name is compatible with `name` (usually `input.fullName`), using `country`'s name-normalization rules. `comparisonMode`: `"strict"` or `"weakContainment"`. `compareAlternativeNames`: boolean — also compare the match's alternative names. |
| `namesIncompatible` | same | Negation of `namesCompatible`. |
| `dobsCompatible` | `(dobs, date, comparisonMode)` | True when any of the match's dates of birth (`match.dobs`) is compatible with `date` (usually `input.dob`). `comparisonMode`: `"strict"` or `"weakContainment"`. |
| `dobsIncompatible` | same | Negation of `dobsCompatible`. |

Example (from the built-in library — auto-clear hits whose name and DoB both diverge):

```json
{"op": "call", "args": [
  {"exp": "dobsIncompatible"},
  {"exp": "match.dobs"},
  {"exp": "input.dob"},
  {"lit": "\"weakContainment\""}
]}
```

A misspelled function name produces an `unknownFunction` error notice on the draft.

## Review action

Two mutually exclusive forms:

**Per-field form** — each field is an arg (`{"lit": ...}` or `{"exp": ...}`); only the fields present are set on the hit's review:

```jsonc
{
  "matchStatus": {"lit": "\"false_positive\""},   // see enum below
  "riskLevel":   {"lit": "\"LOW\""},              // vendor-specific, see below
  "whitelisted": {"lit": "true"},                 // boolean
  "note":        {"lit": "\"Cleared automatically: DoB mismatch\""}
}
```

**Whole-review form** — `expression` evaluates to an entire review object, which is copied onto the hit verbatim; the per-field keys are ignored when `expression` is set:

```jsonc
{"expression": "match.previousReview"}    // carry over the previous screening's decision
```

> The OpenAPI description of `expression` ("condition guarding the review action") is misleading — the implemented semantics are the whole-review form above.

### `matchStatus` values

| Value | Meaning |
|---|---|
| `unknown` | No answer — the hit is still to be reviewed. |
| `potential_match` | The hit potentially identifies the same entity as the screening input. |
| `false_positive` | The hit most likely identifies a *different* entity. |
| `true_positive` | The hit identifies the same entity. |

(`no_match` exists but is deprecated — use `false_positive`.)

A hit that receives a non-null `matchStatus` from a rule counts as **reviewed** — later rules in the chain no longer evaluate against it.

### `riskLevel` values

Vendor-specific, not a fixed enum. For World-Check One: `LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`. Possible values may change with vendor changes; when unsure, omit `riskLevel`.

### `whitelisted`

Client-side risk acceptance: allows approving the applicant even when the hit is `potential_match` / `true_positive`.

## Tags action

```jsonc
{"tags": {"tags": ["match_tin"]}}
```

Adds the listed tags to the AML case (deduplicated). These are **applicant tags** — the common, tenant-wide tag list used across the whole platform (dashboard filters, workflows, other rules), not something private to AML screening.

Tags do **not** need to pre-exist: upserting a rule automatically adds any unknown tag from its `tags` action to the tenant's applicant tag list. That makes introducing a tag a **tenant-wide side effect** — so prefer reusing an existing tag when one fits, and give new tags clear, readable, reusable, concise names (`youngPep`, `match_tin` — not `rule3_tag` or a sentence). The `invalidTag` error notice fires for tags referenced in **conditions** (`screening.tags` literals) that exist nowhere — typically a typo, or a condition checking a tag no rule or human ever sets.

Tags added by one rule are visible to **later** rules in the same run via `screening.tags`, which enables chaining (e.g. rule 5 tags `match_tin`; rule 9 marks all remaining hits `potential_match` when `screening.tags containsAny ["match_tin"]`).

Tags also cross over into **applicant workflows**: workflow edge conditions see them as `checks.personWatchlist.tags` (individuals) and `checks.companyWatchlist.tags` (companies). A rule chain can therefore encode screening expertise as a tag (`youngPep` when `match.riskLabels contains pep` and the applicant is under 30) and a workflow routes on it (`checks.personWatchlist.tags contains youngPep` → manual review). See the workflow skill's expressions reference for the workflow-side paths.

## Notices

Validation findings recomputed on every draft change. `severity`: `info` | `warning` | `error` — **any `error` blocks publishing**.

| `message` key | Meaning |
|---|---|
| `emptyRules` | The rule chain has no rules. |
| `emptyAction` | A rule has neither `review` nor `tags`. |
| `emptyTags` | A `tags` action with an empty list. |
| `invalidTag` | Tag `{tag}` referenced in a condition (`screening.tags`) does not exist anywhere — typically a typo. Tags in a rule's `tags` *action* are auto-created on upsert and don't trigger this. |
| `unknownField` | Expression path `{field}` does not exist in the context. |
| `unknownValue` | Value `{value}` is not valid for field `{field}` (vocabulary-backed fields). |
| `compareWithEmptyList` | Field `{field}` is compared to an empty list. |
| `emptyFunctionName` | A `call` criterion without a function name. |
| `unknownFunction` | Function `{function}` is not a known built-in. |
| `error` | Generic validation error `{error}`. |

`messageParams` carries the `{placeholders}`; `ruleId` points at the offending rule when applicable.

## Library

`GET /library` returns `{"categories": [{"id", "name", "rules": [{"vendors": [...], "rule": {...}}]}]}`. Library rules are **templates**: take the `rule` definition, adjust it, strip the `id`, and upsert it into the draft (the server assigns a fresh id). The `vendors` list names the AML screening vendors the template is designed for (empty = applies to all) — check it against the vendor the tenant uses before suggesting a template.

## How the rule chain executes (what to tell users)

When an AML screening produces hits, the **published** rule chain runs:

1. Rules run **in order, top to bottom**. Order matters.
2. Each rule is evaluated against **every hit that is not yet reviewed** (no `matchStatus` from moderation or an earlier rule).
3. When a rule's condition is true for a hit: the review action is applied to that hit, the tags are added to the case, and the case-level context (`screening.answer`, `screening.tags`, `screening.matchStatuses`) is **recomputed immediately** — later rules see the effects of earlier ones.
4. The run stops early once the case is fully resolved.

Consequences for rule design:
- Put **specific, decisive** rules (exact-ID matches, carry-over of previous reviews) **before** broad clean-up rules.
- A broad `false_positive` rule placed first can "steal" hits from a more precise `true_positive` rule placed after it.
- Chained rules (via `screening.tags` / `screening.matchStatuses`) only see effects of rules **above** them.
