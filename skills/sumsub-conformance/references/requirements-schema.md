# `requirements.json` — the requirement model

The agent produces this from the regulation (ingest + map steps). `trace.py` consumes it
against the deployed config graph. One array `requirements`, each entry:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | stable slug for the requirement (internal cross-ref; not shown prominently) |
| `source` | **strongly recommended** | citation into the ORIGINAL document — section number / heading / page, e.g. `"§5.9.2"`, `"Section 2: Product Governance — Scoring Result"`, `"p.21"`. The report leads each finding with this so a reader can trace it back to the regulation, not an artificial id. |
| `text` | yes | human description (quote the regulation) |
| `type` | yes | one of the types below — **`trace.py` has a deterministic branch per type, not just questionnaire questions** |
| `enforceable` | yes | `config` (checkable in Sumsub config) · `sdk` · `platform` (not checkable → NOT-CONFIG-REPRESENTABLE) |
| `match` | depends on `type` | the mapping payload — **shape differs per type, see the table below** |
| `expectScores` | optional, `scoring` | regulation's per-option scores **in deployed option order** → compared deterministically |
| `enforcementSignal` | for `screening`/`routing-outcome` | tokens that MUST all appear in the workflow/scoring conditions for the outcome to count as enforced |

## Types and their `match` shape (this is how you map non-questionnaire requirements)

`trace.py` checks each type against a specific part of the resolved graph. The **map step's job is to
pick the right `type` and fill its `match`** — not everything is a questionnaire question.

| `type` | `match` shape | What `trace.py` checks (deterministic) | Graph field |
|---|---|---|---|
| `question` / `scoring` | `{questionnaire, section, item}` (+ `expectScores` for scoring), or `null` if absent | question exists; option scores equal `expectScores` | `questionnaires[].sections[].items[].options[].score` |
| `question` / `scoring` (document collection) | `{docSet: "IDENTITY", types: ["PASSPORT", …]}` | the level collects that docSet + (optionally) those doc types | `level.requiredIdDocs.docSets[].{idDocSetType,types}` |
| `question` (KYB beneficial owners / UBOs) | `{docSet: "COMPANY_BENEFICIARIES"}` — no `types` (not the legacy `COMPANY`) | the company level collects associated parties | `level.requiredIdDocs.docSets[].idDocSetType` |
| `data-field` | `{field: "dob"}` or `{fields: ["dob","country"]}` | **APPLICANT_DATA collects the named field(s)** | `docSets[APPLICANT_DATA].fields[].name` |
| `country-eligibility` | `{mustHaveAllowlist: true}` **or** `{mustExclude: ["USA","IRN"]}` | a geo restriction exists / prohibited countries are not admitted | `requiredIdDocs.includedCountries` / `excludedCountries` / `rejectUsaResidents` |
| `liveness` | `{}` | a SELFIE step enforces a liveness mode (not photo-only/disabled) | `docSets[SELFIE].videoRequired` |
| `entitlement` | `{entitlement: "WATCHLISTS"}` or `{entitlements: ["COMPANY","KYB_FULL"]}` (any-of) | the tenant holds the capability | `entitlements` (allowedChecks keys) |
| `screening` / `routing-outcome` | — (use `enforcementSignal`, not `match`) | the outcome is referenced in workflow/scoring conditions | workflow edge/node conditions |
| `disclosure` / `account-state` | — | always → `NOT-CONFIG-REPRESENTABLE` (SDK/platform) | n/a |

## The `config-graph.json` shape (`resolve_graph.sh` output) — read it via `graph_summary.py`

For the **Map** step, inspect the graph with `python3 scripts/graph_summary.py "$CONFIG"` (it prints
questionnaire **section/item indices + option scores**, docSets, APPLICANT_DATA fields, geo, entitlements,
workflow). **Do NOT hand-iterate the graph JSON** — the shapes are mixed and ad-hoc probes keep crashing.

| Key | Shape | Correct access |
|---|---|---|
| `level` | object | `g["level"]["name"]`, `…["requiredIdDocs"]["docSets"]`, `…["includedCountries"]`, `["rejectUsaResidents"]` |
| `questionnaires` | **dict keyed by id** `{"<id>": {"sections":[{"items":[{"options":[{"score":…}]}]}]}}` | `for qid, q in g["questionnaires"].items()` |
| `poaPresets` / `crossCheckPresets` | **dict keyed by id** (value may be `{"_error":"404"}`) | `.items()` |
| `workflow` | object or `null` — `{"nodes":[…], "edges":[{"from","to","condition"}]}` | guard for `None` |
| `entitlements` | **list of strings** (allowedChecks keys) | `"WATCHLISTS" in g["entitlements"]` — **no `.get()`** |

> ⚠️ Iterating a dict-keyed-by-id yields the id **strings**, so `for q in g["questionnaires"]: q.get(...)`
> raises `'str' object has no attribute 'get'`. Use `.items()`, or just run `graph_summary.py`.

## Buckets `trace.py` produces

- **MISSING** — the required thing isn't deployed: `match` is null/unresolved, or a required docSet /
  APPLICANT_DATA field / entitlement / geo restriction is absent.
- **SCORING-MISMATCH** — question present but `expectScores != deployed scores`.
- **COLLECTED-NOT-ENFORCED** — the data is collected but the required enforcement isn't applied: the
  `enforcementSignal` is absent from routing/scoring, or a SELFIE is collected without a liveness mode.
  *The flagship finding.*
- **NOT-CONFIG-REPRESENTABLE** — `enforceable` is `sdk`/`platform`. Bucketed, never silently passed.
- **CONFORMANT** — collected + scored + enforced as specified.

## `enforcementSignal` must be DISCRIMINATING (critical)

The enforcement search is a substring match over the workflow's condition tokens (`exp` paths +
`lit` values) plus any scoring config. **Do not use a generic token** that a catch-all edge would
satisfy. Live example: the CFD workflow has a catch-all `applicant.country notEmpty` edge — so
`["country"]` would *falsely* mark the high-risk-country override as enforced. Use a discriminating
token instead: a representative high-risk country literal (`["albania"]`), or `["score"]` /
`["riskLevel"]` / `["appropriateness"]` for score-driven outcomes. All listed tokens must co-occur.

## Mapping is judgment; scores/enforcement are deterministic

- Filling `match` (which deployed config element — question, docSet, field, country rule, entitlement —
  satisfies this requirement) and extracting the regulation's requirements are **agent judgment** →
  advisory, human-signed.
- Given `match`, the score comparison and the `enforcementSignal` search are **deterministic** and
  cited as evidence. Keep the two separated (see the `basis` field on every finding).
