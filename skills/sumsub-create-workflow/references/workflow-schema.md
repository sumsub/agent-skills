# ApplicantWorkflow — schema reference

**Sources & authority.** Structure (shapes, fields, enums) reflects the Sumsub
OpenAPI schema (`components.schemas`) and is **schema-authoritative**. Behavioural
semantics (what's honored vs ignored, real validation rules) come from the API owner
and are tagged *(semantics)*. `build_workflow.py` checks payloads against small built-in
sets mirroring the API's enums (node types, operators, `targetType`); the API's
`POST /-/validate` is authoritative for everything else.

## Top-level fields

| Field | Type | Notes |
|---|---|---|
| `name` | enum | **Required.** Workflow *kind* — `default` (verification, auto-runs), `actions` (post-verification action workflow, auto-runs), `test` (isolated; runs only from its draft, launched manually per applicant — **not publishable**, see Lifecycle). Not a slug. The compact spec calls this `kind:`. |
| `title` | string | **Unused by the engine** *(semantics)*. The schema carries it (server defaults it to `"Default"`), but it does not affect behaviour and is not displayed in routing — the skill neither sets nor relies on it. Identify a workflow by `name` + `revision`. |
| `revision` | int | Server-assigned per save. Don't send. |
| `revisionStatus` | enum `draft｜published｜archived` | Create/update POST only writes `draft` (`published`/`archived` here is rejected). Status changes go through `PUT /{id}/revisionStatus` — **but only for `default`/`actions`; a `test` workflow's `revisionStatus` is immutable (the API rejects the call), so `test` lives only as a draft.** ⚠️ Publishing `default`/`actions` affects **live** traffic — see Lifecycle + the skill's Danger section. |
| `nodes` | array | Flow-graph vertices. See *Node types*. |
| `edges` | array | Directed transitions. May carry `condition` and/or `reviewDecisions`. |
| `notices` | array | Validation hints (`severity: info｜error`); `error` blocks publish. **Response-only** — server-populated by `/-/validate`; not part of the write (`UpsertApplicantWorkflowDto`) and not sent on save. |
| `clientId` / `created` / `modified` / `published` / `archived` | — | Server-populated. Don't send. |

## Node types (`ApplicantWorkflowNodeType`)

A node is `{ id, type, name?, description?, disableGoBack?, <familyParams> }` — the
params object key matches the family (`applicantLevel`, `actions`, `finalRejection`,
`applicantTransition`, …). The skill uses these **real schema type names** directly.
The spec also accepts flattened body fields (`levelName`, `labels`, `buttonIds`,
`actions`) as a convenience, lifted into the nested family object on build.

### Standard verification workflow (`kind: default｜test`)

| Type | Params |
|---|---|
| `applicantLevel` | `applicantLevel: { levelName }` — references a level by **name**, not id. Optional `disableGoBack`, `resetDocSets`*. |
| `exclusiveChoice` | none — branches via outgoing edges (see *Edges*). |
| `actions` | `actions: { items: [Action] }` — tag/note/sourceKey without changing flow. |
| `manualReview` | none — applicant lands in a review queue. |
| `finalRejection` | `finalRejection: { reviewRejectLabels?: [ReviewLabel], reviewButtonIds?: [string] }` — terminal blocked state. |

### Action workflow (`kind: actions` only)

| Type | Params |
|---|---|
| `actionApplicantLevel` | as `applicantLevel`. |
| `actionExclusiveChoice` | as `exclusiveChoice`. |
| `actionActions` | as `actions`. |
| `actionManualReview` | as `manualReview`. |
| `actionFinalRejection` | as `finalRejection`. |
| `actionApplicantTransition` | `applicantTransition: { applicantLevel: { levelName } }` — hands the verification process **back from the action workflow to the `default` workflow**, entering the named level. *(semantics)* |

- *(semantics)* **`actionXyz` types are valid only in an action workflow (`kind: actions`); standard types only in `default`/`test`. Mixing is rejected** (`standardLevelsInStandardWorkflowsOnly` and friends). The builder enforces this before POST.
- `resetDocSets` and the `And.score` field exist in the schema but **must not be used** in workflows yet (unsupported) — the builder does not expose them.

## Actions (`actions.items[]` — `ApplicantWorkflowAction`)

Shape: `{ type, <familyBody> }`. *(semantics)* **`type` is required and equals the family
key.** The skill supports a subset of `ActionType` (the rest are listed as not-supported below):

| Action | Compact | Body | Notes |
|---|---|---|---|
| `tags` | `{tag: [...]}` or `{tag: {add:[...], remove:[...], target: applicant｜applicantAction}}` | `tags: { tags?, tagsToRemove?, targetType? }` | `tags` adds, `tagsToRemove` removes. |
| `notes` | `{note: "text"}` or `{note: {text:"...", target: …}}` | `notes: { note, targetType? }` | |
| `sourceKey` | `{sourceKey: "..."}` | `sourceKey: { sourceKey }` | overrides applicant source key. |

- *(semantics)* **`targetType` default is `applicant`.** `applicantAction` targets the
  triggering action and is only available in an **action workflow** (only there is the
  applicantAction in the evaluation context). The builder rejects `applicantAction` in a
  `default`/`test` workflow.
- **Not author-supported:** `kytCase` (postponed — no public API to obtain `blueprintId`),
  `riskScore`, `recheck`. The old skill's `riskLevel` action never existed — it was a
  mis-name of `riskScore`; it has been removed.

## Edges & conditions

```json
{ "id":"…", "from":"<node>", "to":"<node>",
  "reviewDecisions":["approved","rejected","resubmission"],
  "condition": { "or": [ { "and": [ { "op":"eq",
                 "args":[{"exp":"applicant.country"},{"lit":"\"USA\""}] } ] } ] } }
```

- *(semantics)* **A level node has exactly one out-edge**, and it is **unconditional** —
  the API ignores `reviewDecisions`/`condition` on a level's own out-edge and rejects
  `>1` level out-edge with `multipleOutEdgesNotSupported`. Branch *after* a level by
  routing into an `exclusiveChoice`: one plain edge `level → choice`, then the branches
  on the choice's out-edges. The builder **enforces** this — it rejects `on:`/`condition:`
  on a level edge (and a level with >1 out-edge); it does **not** synthesize a choice for
  you. The same holds for every non-choice node (`actions`, `manualReview`, …): one
  unconditional out-edge, never branching.
- *(semantics)* **`reviewDecisions`** (`approved`/`rejected`/`resubmission`, from
  `ReviewDecision`) is honored **only on edges leaving an `exclusiveChoice`/
  `actionExclusiveChoice`**, matching the upstream level's decision. It is the canonical
  way to branch on a level's outcome.
- *(semantics)* Mixed choice out-edges (`reviewDecisions`-gated, `condition`-gated, plain)
  are evaluated **in declared order, first match wins**; a plain edge is the catch-all.
  **Exception:** an applicant whose decision is `resubmission` is *not* caught by a plain
  edge — by default they stay on the level (retry), and they only advance if the immediate
  post-level choice explicitly handles `resubmission`. See *Iteration without cycles: the
  resubmission gate* in [workflow-patterns.md](workflow-patterns.md).
- *(semantics)* **A decision that matches none of a choice's out-edges is terminal in that
  state** — an `approved` applicant with no matching out-edge simply ends approved (this is why
  examples can leave `approved`/`rejected` unrouted). This is distinct from a choice with **zero**
  out-edges, which strands every applicant and the builder rejects (*Common gotchas*).
  `resubmission` is the exception above: no match means **stay-and-retry**, not terminal.

### Condition AST (`Condition`)

Authored directly on an edge as `condition:`. Shape:

```
Condition = { or: [And] (1..30) }                # negate? exists — NOT UI-supported; builder rejects it
And       = { and: [Criterion] (1..30) }          # negate? honored by the engine; score? unsupported
Criterion = { op: Op, args: [Arg] (1..10) }
Arg       = { exp: string(≤512) } | { lit: string(≤1024) }   # exp = raw path; lit = JSON-encoded value
```

- It is an **OR of AND-groups of criteria**.
- `Arg` is a keyed union: `{exp}` (a raw expression path) **or** `{lit}` (a literal,
  supplied already JSON-encoded as a string — see *Literal encoding*). Both args of a
  comparison may be `{exp}` (field-to-field, or a client-list RHS).
- *(semantics)* **Express negation with the `not*` operators** — `notContains`, `notIn`,
  `notEmpty`, `notStartsWith`, `notEndsWith`, `notMatch`, `ne`, `neIgnoreCase`,
  `notContainsAny`. Do **not** set a `negate` flag: **`Condition.negate` (top level) is
  not UI-supported and the builder rejects it.** `And.negate` *is* honored by the engine
  if hand-written (the UI doesn't expose it); `And.score` is unsupported.
- `op: empty` / `op: notEmpty` take a single `{exp}` arg; most ops take `[{exp}, {lit}]`.

### Operators (`Op`)

`eq eqIgnoreCase neIgnoreCase eqOrNull eqIgnoreCaseOrNull ne lt lte gt gte match notMatch
in notIn startsWith notStartsWith endsWith notEndsWith empty notEmpty contains notContains
containsAny notContainsAny containsAll containsOnly`

- The list above is the full set; `build_workflow.py` validates every authored
  condition's operator against it.
- **`call` is reserved** (exists in the enum, not exposed) — the builder rejects it.

### Literal encoding

`lit` carries a **JSON-encoded value as a string** — write it that way directly (the
API rejects an un-encoded literal with `syntaxError`):

```
"USA" → "\"USA\""      3 → "3"      true → "true"      ["USA","DEU"] → "[\"USA\", \"DEU\"]"
```

(`exp`, by contrast, is the raw path with no encoding: `{"exp": "applicant.country"}`.)

## Expression paths (left-hand side of comparisons)

The authoritative inventory of every legal `exp` path is **[`workflow-expressions.md`](workflow-expressions.md)** (a lookup dictionary, sourced separately from the expression-context vocabulary — *not* from `components.schemas`). Grep by leaf field name. Cheat sheet of common patterns:

| Path | Use case |
|---|---|
| `applicant.country` | Route / reject by ISO-3 country. |
| `poi.country` | Country from the proof-of-identity document. |
| `applicant.review.attemptCnt` | "Is this the Nth re-attempt?" |
| `applicant.fixedInfo.firstName` | Direct profile field. |
| `questionnaires.<qId>.<sectionId>.<itemId>` | Questionnaire answer. |
| `checks.<checkName>.<field>` | Automated-check outputs. |
| `applicant.review.rejectLabels` | AML/check result labels — `contains PEP`, `containsAny [SANCTIONS, ADVERSE_MEDIA]`. The canonical post-AML branch. |
| `applicant.review.reviewAnswer` | `GREEN` / `RED` overall answer. |
| `applicant.tags` | Tags set upstream by `actions` nodes — route with `contains` / `containsAny` (tag-as-state-machine). |
| `clientLists.<name>` | A **tenant-defined named list**. Used as the **RHS** of `in` / `notIn` / `containsAny`: `poi.country in clientLists.high_risk_countries_list`. Not creatable via this skill — create and populate it with [`sumsub-manage-client-lists`](../../sumsub-manage-client-lists/SKILL.md); an unknown name validates as `invalidExpression`. |
| `random` | Random-bucket A/B sampling. |

Paths absent from `workflow-expressions.md` resolve to "empty" at runtime — wrap unverified paths with `notEmpty` so the edge fails closed.

## Lifecycle

1. **Create as draft** — `POST /resources/api/agent/applicantWorkflows`, `revisionStatus: draft` (default). App Token + HMAC; permission `manageWorkflows`. Safe — drafts route no traffic. **One draft per workflow:** a no-`id` POST when a draft of this `name` exists returns `409` — update that draft in place instead. Check first with `scripts/workflow_api.py state`.
2. **Edit** — POST again with the same `id` to update the **draft** in place. Published/archived revisions are read-only; to change a published one, `POST /{id}/draft` to fork a new draft from it — subject to the one-draft rule (`409` if a draft already exists; edit that draft instead). Update-in-place (POST with the draft's `id`) is the **only** way to overwrite an existing draft — both a no-`id` POST and `fork` `409` when the slot is taken.
3. **Validate without saving** — `POST /…/-/validate` with `{name, nodes, edges}`. Returns `notices[]`; `error` severity blocks publish. The API's validate is authoritative — the builder's client-side checks just give faster feedback. *(semantics)*
4. **Publish / archive** — `PUT /…/{id}/revisionStatus`, **for `default`/`actions` only**. Publishing **auto-archives** the prior published revision. ⚠️ **Revisions are shared across live and sandbox; only applicants are isolated — publishing `default`/`actions` changes real production routing.** Gated by the workflow's **current live exposure** (the traffic on the currently-published revision, step 6 below) — see SKILL.md's Danger section for the full gating policy and step 8 for the flow. Rollback by re-publishing the previously-published revision id. **`test` has no publish/archive step — its `revisionStatus` is immutable (the API rejects the call); it runs from its draft.**
5. **Per-applicant runs** are stored separately as `ApplicantWorkflowRun`, visible per-applicant in the dashboard.
6. **Traffic check (pre-publish guard)** — `GET /…/{id}/traffic` → `{"applicantCount": N}`, approximate applicants recently on this revision's levels. ⚠️ **Level-derived, not workflow-routed** — revisions sharing level names report overlapping counts. `0` = no recent traffic; `>0` = those levels are live.

### Revision continuity — keep node/edge ids sticky when editing *(semantics)*

The engine upgrades **in-flight applicant runs** onto a newly published revision using
matching strategies keyed on **node id** and **edge id**. The
dashboard editor forks a draft from the last published revision and preserves existing
node/edge ids through read-modify-update cycles — so ids are normally **sticky** across
revisions and runs upgrade cleanly.

When this skill *edits* an existing workflow (forking a published revision, or updating a
draft that descends from one), do the same: **GET the revision you're basing on first and
carry its node and edge ids through verbatim for every element you keep — mint new ids only
for genuinely new nodes/edges.** Rebuilding from a fresh spec with new ids isn't an error,
but it defeats id-matching, so the engine falls back to weaker strategies (it may re-enter a
run at a level node, skip the upgrade, or otherwise diverge — the outcome is strategy-
dependent, not guaranteed). The builder cooperates: it emits node `id` verbatim and passes
an edge `id` through whenever the spec supplies one. For a brand-new workflow, ids don't
matter — there are no prior runs to upgrade.

## Constraints (product semantics)

- **Entry node required**: ≥1 `applicantLevel` with no incoming edges — and there is **no upper bound**. A workflow is a **forest**: each entry level roots an independent flow and the graph need not be connected. Small workflows have one or a few roots; large consolidated ones routinely have **dozens** (e.g. a single `default` workflow holding KYC bases per region *and* KYB bases per entity class — regulated / non-regulated / tech-provider / reliance / entity-linked — each its own root).
- **An applicant's type is fixed and cannot change mid-workflow** *(semantics)*. So flows for different applicant types — e.g. **KYC (individual) vs KYB (company)** — live as **separate, non-intersecting components in the same workflow**, each entered by a type-appropriate level. Never bridge them with an edge: an applicant can't switch type, so a transition from an individual level into a company level (or vice versa) is invalid. A single `default` workflow commonly holds many such isolated flows.
- **Each verification level appears at most once** in a workflow.
- **All levels in a workflow should use the same WebSDK version** — dashboard-warned, not server-enforced.
- **Sequential level transitions reset verification state** — gate progression through a `condition` node.

## Common gotchas

- **`levelName` is the level's *name*, not its id.** Unknown names → the applicant stalls (`levelNotFound` at validate).
- **`condition` node with no branching out-edge** — saves, but applicants have nowhere to go. The builder rejects it upfront.
- **`reviewRejectLabels`** must be `ReviewLabel` enum values (validated by the API at `POST /-/validate`). Button IDs come from the dashboard's moderation-buttons config.
