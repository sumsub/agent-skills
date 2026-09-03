---
name: sumsub-create-workflow
description: Create a Sumsub applicant workflow — verification routing (levels, branches, country/age rules, final-rejection or manual-review steps) or an action workflow (post-verification tagging, notes, source-key changes). TRIGGER on requests to create/build/add a workflow or a flowchart-style routing description. Builds, validates, and saves a draft, then publishes it — gated by live traffic — automatically when the workflow's traffic is low, only after explicit confirmation when it's high. Publishing changes LIVE traffic — see the Danger section. SKIP for editing arbitrary fields of an existing revision, or for questionnaires/levels (separate skills).
allowed-tools: Read, Write, Bash
---

# Sumsub — Create Workflow

Builds an `ApplicantWorkflow` JSON payload from a compact node/edge spec, validates it (dry-run), POSTs it as a `draft`, and then — gated by the workflow's **current live exposure** — publishes it via `PUT /{id}/revisionStatus`: directly when exposure is low, or only after explicit confirmation when it's high. Reports the resulting `name` (kind) / `revision` / `revisionStatus` / `id`. **Read the Danger section before publishing anything.**

## Concepts

A *workflow* routes applicants through levels and branches. There is exactly **one** workflow
per **kind**: `default` (auto-runs for every verification), `actions` (auto-runs for applicant
actions), `test` (isolated; runs only from its draft, launched manually per applicant — **not
publishable**). Each save creates a new **revision** of that singleton, never a new workflow.
A revision is a **draft** — editable, routes no traffic, always safe to create / update /
validate — until it is **published**, which makes it live for **all real production traffic**
and auto-archives the previously published revision. `test` never publishes; it runs from its
draft.

## Endpoints

| Method | Path | When |
|---|---|---|
| `POST` | `/resources/api/agent/applicantWorkflows` | Create (no `id`) or update a **draft** by `id`. Only drafts are editable; a `published`/`archived` `revisionStatus` here is rejected. **Always safe** — drafts route no traffic. |
| `POST` | `/resources/api/agent/applicantWorkflows/-/validate` | Dry-run validation. Returns `notices[]` without persisting. Read-only. |
| `GET`  | `/resources/api/agent/applicantWorkflows` | List workflows (every revision, all statuses). Response is flat: `{ "items": [...], "totalItems": N, "pageInfo": { "limit", "offset" }, "error": {...}? }` — `items` is top-level (no `list` wrapper). |
| `GET`  | `/resources/api/agent/applicantWorkflows/{id}` | Read one revision (the `id` is a specific revision, not the workflow name). |
| `GET`  | `/resources/api/agent/applicantWorkflows/{id}/traffic` | Applicants recently on this revision's levels: `{"applicantCount": N}`. Read-only; the input to the publish exposure gate. **Level-derived, not workflow-routed — see Danger.** |
| `POST` | `/resources/api/agent/applicantWorkflows/{id}/draft` | Fork a new draft from a published/archived revision — the way to iterate on a live workflow without touching it. |
| `PUT`  | `/resources/api/agent/applicantWorkflows/{id}/revisionStatus` | **Publish / archive** a revision. Body `{"revisionStatus":"published"｜"archived"｜"draft"}`. Publishing requires zero `error` notices and **auto-archives the prior published revision**. ⚠️ **Affects live traffic — see Danger.** |

Permission required on the App Token: `manageWorkflows`. Sandbox tokens typically have it; if you hit `403 Unauthorized (atd)`, regenerate the token with the right scopes.

## ⚠️ Danger — publishing affects LIVE production traffic

**Workflow revisions are shared across live and sandbox; only *applicants* are
isolated.** Publishing changes the workflow that handles **all real production
traffic** — a sandbox `sbx:` token does **not** make this safe. This is the single
most important fact about this skill. (Drafts, by contrast, route no traffic —
create / update / validate them freely.)

Publishing `default`/`actions` is gated by the workflow's **current live exposure**
— the recent applicant traffic on the revision that is currently `published` (the
one a publish auto-archives), measured by the `workflow_api.py traffic` subcommand. The
threshold is **400** recent applicants (override: `SUMSUB_PUBLISH_TRAFFIC_THRESHOLD`):

| Workflow `name` | Current live exposure | Publishing |
|---|---|---|
| `default` / `actions` | **> 400** recent applicants, **or** unreadable | **Fully guarded**: clean validate · diff vs current published · explicit user "yes" · `SUMSUB_ALLOW_WORKFLOW_PUBLISH=1` latch |
| `default` / `actions` | **≤ 400**, **or** no published revision yet | **Low-exposure: publish directly** — no confirmation, no latch (still report what you did) |
| `test` | — | **Not publishable** — `revisionStatus` is immutable (the API rejects the call); it runs from its draft |

The exposure count is **level-derived** — it counts applicants recently seen on the level
*names* the published revision contains (so revisions sharing level names report overlapping
counts), reflecting how busy this workflow's levels are *now*, not the new revision's blast
radius. Phrase it to the user as *"the levels in this revision have N recent applicants,"*
never *"this workflow handled N."* Rules that hold regardless of exposure:

- **Publishing is the default end of a build, not a separate request** — the gate
  above decides what it costs (low → direct; high → confirm + latch). The only thing
  that keeps a build at a draft is the user explicitly opting out (*"just save a draft"*).
- **Fail safe on unknown exposure.** If the live revision's traffic can't be read
  (API error), treat it as over-threshold and run the full guarded flow.
- **Never switch kinds to dodge the gate.** A publish request can't be made "safer"
  by retargeting to `test` (the API rejects it anyway). Publish the requested kind.
- `workflow_api.py publish` is the backstop: it independently re-measures exposure and
  requires `SUMSUB_ALLOW_WORKFLOW_PUBLISH=1` **only** when exposure is over-threshold
  or unreadable — letting a low-exposure publish through unlatched.

## Auth — App Token + secret (sandbox only)

Each request is signed with App Token + secret (HMAC-SHA256). Full signing details
and `401` debugging: [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md).

> **⚠️ Sandbox only.** A workflow routes real applicants, so production tokens are
> refused — the scripts reject anything not prefixed `sbx:`. Mint a sandbox pair in
> the dashboard (switch the workspace to **Sandbox** → App tokens → Create; both are
> shown once).

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

> **Not a credential:** publishing a **high-exposure** `default`/`actions` revision
> (live traffic above the threshold, or unreadable) is armed by
> `SUMSUB_ALLOW_WORKFLOW_PUBLISH=1`, but that is **not** a configured env var —
> it is a per-command arming token you type inline on the publish call (step 8),
> nothing else. **Never** add it to `settings.local.json` or any persistent env:
> doing so leaves the gate permanently open, which defeats its only purpose. It
> belongs on exactly one command line, at the moment you publish, and nowhere else.

## Principles

These three govern every step below; the procedure points back here where each one bites. They share one spine — **the user's intent and the workspace's real entities are the ground truth; your job is to wire them faithfully, never to invent or improve.**

1. **Build exactly what the user specified.** Their level names, node structure, branch logic, and chosen `kind` are fixed constraints — not raw material to improve. If your own reasoning concludes a choice is redundant or suboptimal — often resting on a wrong assumption about how levels or the engine behave (e.g. chained levels *don't* re-capture already-collected data — see [references/workflow-patterns.md](references/workflow-patterns.md)) — **build it literally and flag the concern in your report**, never silently substitute a design you prefer. Validation catches what's *invalid*; "suboptimal" is not "invalid," and is never license to change their design.
2. **Wire entities; don't own them.** Every level, client list, and tag a node references must resolve to something real before you build on it — a name the user gave you, one you confirmed via `GET /resources/applicants/-/levels`, or one explicitly being created (by you, a companion skill, or the user). An ungrounded reference is a **stop, not a blank to fill**: reuse what exists, get it created, or mark it explicitly pending — **never invent a plausible name to make the graph look complete** (that a missing reference blocks only *publish*, not the draft, is no license to fabricate one). Ground *proactively* — read the existing levels and reuse a real one before asking or inventing.
3. **Aim at the reference, not the green checkmark.** Structural/builder errors are yours to fix — iterate until clean. But a missing-entity error (`levelNotFound`, `tagDoesNotExist`, unknown client list) is cleared only by **grounding** the reference — never by repointing it at a convenient entity to make validation pass. And **report the territory, not the map you wish were true**: a draft with unresolved references is **unfinished**, and structure you bent to fit an existing entity is a **change to the user's policy** — surface both plainly, never as a clean success.

## Procedure

0. **Resolve the workflow `kind` from the user's own words, and state it back.** If the user named no kind, it is **`default`** (the spec default). Use `test` or `actions` **only when the user explicitly names them.** Never infer, default to, or substitute a kind the user didn't ask for. **State the kind as an assumption and proceed** — say e.g. *"treating this as `default` since you didn't specify a kind"* so it's visible and correctable; don't turn the kind into a multiple-choice question. **Never offer `test` as a "safe place to build" a `default` workflow** to avoid touching an existing draft: `test` is for manual, per-applicant test runs, has its own separate draft, **cannot be published**, and has **no promotion path** into `default`. An existing `default` draft is never a reason to build elsewhere — just overwrite it (step 3).
1. **Translate the user's flowchart into the compact spec** (below). One node per box / decision diamond, one edge per arrow. Use `id`s that read like labels (`country-check`, `route`, `idv`, `reject-region`). If the user gives a *policy* rather than a flowchart ("build me a KYC/KYB workflow"), don't start from a blank page — decompose it with the canonical pipeline spine and primitives in [references/workflow-patterns.md](references/workflow-patterns.md), then stamp that spine per segment. Build only what the user specified, and ground every level / list / tag reference before building on it (**Principles 1–2**).
2. **Validate the graph:** every edge `from`/`to` resolves to a node id; every `applicantLevel` / `actionApplicantLevel` references a real level by name; every `exclusiveChoice` has ≥1 branching out-edge (`condition:` or `on:`); final-rejection nodes carry `labels` or `buttonIds`. (A level — and every non-choice node — has a **single, unconditional** out-edge; only an `exclusiveChoice` may branch — see Edge `on:`.) The graph is a directed **acyclic forest**: edges point only forward (no cycles/back-edges — document resubmission is **not** a back-edge; the engine retries in place), while fan-in and shared downstream nodes are fine and several entry levels may root independent flows. **Never bridge different applicant types** (KYC individual vs KYB company) with an edge — an applicant's type can't change. Full graph rules: *Constraints* in [references/workflow-schema.md](references/workflow-schema.md); resubmission in [references/workflow-patterns.md](references/workflow-patterns.md).
3. **Check current state** with `${CLAUDE_SKILL_DIR}/scripts/workflow_api.py state <name>` for the target workflow `name`, then pick the write mode: **no revisions** → create (POST without `id`); **a draft already exists** → update it **in place** (POST with that `id`; a no-`id` POST would `409`); **a published revision but no draft** → seed a draft with `${CLAUDE_SKILL_DIR}/scripts/workflow_api.py fork <id>`, or just POST a fresh one. **Overwriting an existing draft is the normal, expected operation — do it silently.** The draft is a scratch surface the skill evolves across multiple runs, so don't ask before overwriting and don't back it up by default. **Only** if the user explicitly asks to preserve their current draft, first read it with `${CLAUDE_SKILL_DIR}/scripts/workflow_api.py get <id>` and save the JSON body to a file (the command appends a trailing `HTTP <code>` line — keep only the JSON), then overwrite. When editing, **preserve existing node and edge ids** — `get <id>` the revision you're basing on and carry its ids through, minting new ids only for new nodes/edges (the engine matches in-flight runs on those ids; rationale in *Revision continuity*, [references/workflow-schema.md](references/workflow-schema.md)).
4. **Generate payload** with `${CLAUDE_SKILL_DIR}/scripts/build_workflow.py` — spec on stdin → full payload on stdout. The builder assembles the payload from the real node types and edge `condition` ASTs, and validates node types, operators, and action `targetType` against its built-in known sets — so typos and unsupported constructs error here, before any network call (the API's validate is authoritative for the rest — levels, client lists, labels). Set the draft's `id` in the spec when updating in place (step 3).
5. **Validate (dry-run, stores nothing).** Pipe the payload to `${CLAUDE_SKILL_DIR}/scripts/workflow_api.py validate` → `notices[]`. `info` = advisory; `warning` = non-blocking but usually a real bug; `error` = publish-blocker. Look up any notice's meaning, severity, params, and how to act in [references/workflow-notices.md](references/workflow-notices.md). Clear a missing-entity error by **grounding** the reference, not by repointing it to pass validation (**Principle 3**). Always validate before persisting.
6. **POST** via `${CLAUDE_SKILL_DIR}/scripts/workflow_api.py post` — create (no `id`) or update in place (with the `id` from step 3). Response carries the persisted draft with `id`, `clientId`, `notices[]`.
7. **Build the dashboard link** from `clientId` in the response body:

   ```
   https://cockpit.sumsub.com/checkus/sdkIntegrations/workflows/active/applicant?clientId=<clientId>&sbx=true
   ```

   `sbx=true` targets the Sandbox workspace. ⚠️ Not a per-`id` deep link — it shows the current draft; tell the user to click promptly.
8. **Publish — the default end of a build, gated by exposure.** Skip only if the user opted out (*"just save a draft"*) — a draft routes no traffic, so it's not a useful end state on its own. The draft must have last validated clean (step 5) — the API refuses to publish a revision with any `error` notice. Run `${CLAUDE_SKILL_DIR}/scripts/workflow_api.py publish <draft-id>`; it owns the **live-exposure gate** (defined in Danger) and does one of two things:
   - **Low exposure** → it **publishes directly**; you're done.
   - **High exposure** → it **refuses before changing anything**, printing the exposure count and the currently-published revision's `id` (your one-command rollback point). To proceed, run the guarded flow: diff the draft against that published revision, disclose the change **and that count** to the user (*"makes revision N live for ALL real production traffic; the current published revision — whose levels have ~M recent applicants — will be auto-archived"*), get an **explicit "yes"**, then re-run prefixed with `SUMSUB_ALLOW_WORKFLOW_PUBLISH=1`.

   **Rollback:** re-publish the previously-published `id` — `SUMSUB_ALLOW_WORKFLOW_PUBLISH=1 ${CLAUDE_SKILL_DIR}/scripts/workflow_api.py publish <previous-published-id>` (keep the latch — once it's live again, the revision you're replacing may itself be over-threshold). `test` is never published — see Danger.
9. **Report** (lead with the human-readable identity) — and report the territory, not the map you wish were true: flag any unresolved reference or bent structure plainly, never as a clean success (**Principle 3**). Lead with the workflow `name` (`default`/`actions`/`test`) and `revision` — e.g. «default» revision 14 — then `revisionStatus`; node/edge counts and the sorted unique level names referenced (so misspellings show); the **dashboard link** (step 7) as a clickable markdown link. If you published, say so, name the now-`published` revision, note the auto-archived previous revision, and give its id as the rollback point. End with a single `Workflow ID: <id>` line — the one place a raw id belongs. On failure, surface Sumsub's `description` / `errorName` verbatim (builder validation errors already print a precise message).

## Compact spec format (JSON or YAML on stdin)

> **`kind` selects which workflow you're editing** (see *Concepts* for what each kind
> means and how revisions/drafts work). It is set **only** by the user's explicit
> request (see step 0); the default is `default`. ⚠️ `default`/`actions` intercept real
> traffic once published — see the Danger section. (The schema has a `title` field, but
> the engine ignores it — the skill neither sets nor relies on it.)

Nodes use the **real schema node-type** in `type`; edges carry the **real Sumsub
`condition` AST** directly (no expression mini-language). `on:` is a shorthand for
`reviewDecisions`.

```yaml
kind: default                   # optional — default | test | actions (the workflow to edit)
revisionStatus: draft           # optional; only `draft` on create. Publishing is a separate, gated step (see Danger).

nodes:
  - id: country-check
    type: applicantLevel
    levelName: "Country Selector"
  - id: route
    type: exclusiveChoice
    name: "Country router"
  - id: idv
    type: applicantLevel
    levelName: "IDV"
  - id: idv-result
    type: exclusiveChoice
    name: "IDV result"
  - id: reject-region
    type: finalRejection
    labels: ["WRONG_USER_REGION"]
  - id: manual
    type: manualReview

edges:
  # A level's out-edge is single & unconditional — branch only at an explicit exclusiveChoice.
  - { from: country-check, to: route }                  # plain: level → choice
  - from: route                                         # embargo first (any decision)
    to: reject-region
    condition: { or: [ { and: [ { op: in, args: [ {exp: "applicant.country"}, {lit: "[\"UZB\", \"DEU\"]"} ] } ] } ] }
  - from: route                                         # approved & allowed → IDV
    to: idv
    on: approved
    condition: { or: [ { and: [ { op: eq, args: [ {exp: "applicant.country"}, {lit: "\"USA\""} ] } ] } ] }
  - { from: idv, to: idv-result }                       # plain: level → choice
  - { from: idv-result, to: manual, on: rejected }      # resubmission unhandled → engine retries (the default)
```

### Node types

A node is `{ id, type, name?, <body> }`, where `type` is the **real schema node
type**. Body fields may be flattened (shown below) or written in the real nested
form (`applicantLevel: { levelName }`).

**Standard verification workflow** (`kind: default｜test`):

| `type` | Body |
|---|---|
| `applicantLevel` | `levelName` (string); optional `disableGoBack` |
| `exclusiveChoice` | — (branches via outgoing edges) |
| `actions` | `actions:` list (see below) |
| `manualReview` | — |
| `finalRejection` | `labels` OR `buttonIds` |

**Action workflow** (`kind: actions` only): each `action*` type mirrors its standard counterpart — `actionApplicantLevel`, `actionExclusiveChoice`, `actionActions`, `actionManualReview`, `actionFinalRejection` take the same body as the names without the `action` prefix. Plus one extra: `actionApplicantTransition` (`levelName` — the `default`-workflow level to hand the verification back into; it must exist in the **published `default` workflow**, or validate raises `missingLevelsForTransition`).

`action*` types are valid **only** inside an action workflow (a graph that runs after a primary verification — typically tagging / noting / changing source key, or transitioning the applicant back into `default`); standard types only in `default`/`test`. Mixing them is rejected; the builder catches it before POST.

### Actions block

Inside an `actions` or `actionActions` node:

```yaml
- id: tag-and-note
  type: actions
  actions:
    - tag: ["High risk", "Manual review"]    # adds tags
    - note: "Flagged by workflow"            # adds applicant note
    - sourceKey: "manual-flow"               # overrides applicant source key
```

Each item must contain exactly one of: `tag`, `note`, `sourceKey`. Tag/note also take a
richer object form for the niche cases:

```yaml
    - tag:  { add: ["VIP"], remove: ["pending"], target: applicantAction }
    - note: { text: "Auto-note", target: applicantAction }
```

- `target` (`targetType`) is `applicant` by default. `applicantAction` targets the
  triggering action and is **only valid in an action workflow** (`kind: actions`).
- Not supported: `kytCase` (postponed — no public API for its `blueprintId` yet),
  `riskScore`, `recheck`. (The old `riskLevel` action never existed — removed.)

### Edge conditions (`condition:`)

An edge may carry a `condition:` — the **real Sumsub condition AST, written directly** (there is no expression mini-language):

```yaml
condition:
  or:                                  # OR of AND-groups; branches evaluated in order, first match wins
    - and:
        - { op: eq, args: [ {exp: "applicant.country"}, {lit: "\"USA\""} ] }
        - { op: in, args: [ {exp: "poi.country"}, {exp: "clientLists.high_risk"} ] }
```

- **`{exp: "<path>"}`** — an expression path, verbatim. Anything the engine accepts works, including bracket/quoted segments: `applicant.metadata["balance"]`, `clientLists["luhansk_people's_republic"]`. It's the left side of a comparison, and also the **right** side for field-to-field and **client-list** checks (`{exp: "clientLists.high_risk"}`).
- **`{lit: "<json>"}`** — a literal, supplied **already JSON-encoded as a string** (the form the API stores): `"\"USA\""`, `"3"`, `"true"`, `"[\"UZB\", \"DEU\"]"`. An un-encoded literal (`{lit: "USA"}`) is rejected by the API with `syntaxError`, so the encoding is required.
- **`op`** is one of the comparison operators (`eq ne lt lte gt gte in notIn contains notContains containsAny containsAll startsWith endsWith match empty notEmpty eqIgnoreCase …`; full set in [references/workflow-schema.md](references/workflow-schema.md)). The builder validates every `op` against its known set and rejects unknown or reserved ones (`call`).
- **Negation** is expressed with the `not*` operators (`notIn`, `notContains`, `ne`, `notEmpty`, …) — do **not** set a `negate` flag; a top-level `Condition.negate` is rejected (UI-unsupported).

> **Client lists** (`clientLists.<name>`) are **tenant-defined named lists** maintained in the Sumsub dashboard, used as an expression RHS with `in` / `notIn` / `containsAny`. This skill does **not** create them. An unknown list validates as an `invalidExpression` error notice (a missing-entity error, like `levelNotFound`) — the construct is valid, the list just isn't defined in that workspace.

The full `Condition`/`And`/`Criterion` AST, literal-encoding rules, and operator list live in [references/workflow-schema.md](references/workflow-schema.md); valid `exp` paths are in [references/workflow-expressions.md](references/workflow-expressions.md).

### Edge `on:` (review-decision routing)

`on: approved` gates a transition on a level's **review decision** (`approved` / `rejected` / `resubmission`; pass an array for several) — a shorthand for the real `reviewDecisions:` field. **`on:`/`condition:` are honored only on edges leaving an `exclusiveChoice`** (or `actionExclusiveChoice` in an action workflow; the `reviewDecisions` match the upstream level's decision); a level's own out-edge is a **single, unconditional** transition. So to branch on a level's outcome you author the choice yourself: point the level at an `exclusiveChoice` with one plain edge, then put the `on:`/`condition:` branches on the **choice's** out-edges (evaluated in declared order, first match wins). The builder does **not** synthesize choices — it **rejects** `on:`/`condition:` on a level edge (and a level with >1 out-edge), with a message telling you to insert the choice. `on:` and `condition:` can coexist on a choice's out-edge.

Two primitives govern omitted decisions: **(1)** omitting `on:` makes an edge **decision-agnostic** — it doesn't check the decision; **(2)** a resubmitter **stays on its level** unless some branch on the immediate post-level choice names `resubmission`. Together, a no-`on:` edge in practice serves **approved + rejected** while resubmission retries by default (it's a deduction from these two, not a stored default set). **Leave resubmission to the engine: don't name `resubmission` anywhere unless the user explicitly asks to cap or otherwise act on repeated attempts.** It is not part of a standard workflow — the engine's automatic retry is what almost everyone wants. Only if asked, see *Iteration without cycles: the resubmission gate* in [references/workflow-patterns.md](references/workflow-patterns.md) (and note: naming `resubmission` on a choice changes how its **other** edges behave — that section explains the interlock).

## Worked examples

- [`examples/country-routing.json`](examples/country-routing.json) — entry level → eligibility gate (region-reject vs IDV) → IDV → a second choice → manual-review on a rejected IDV. Two choices, because a level sits between them (the most common topology).
- [`examples/action-workflow.json`](examples/action-workflow.json) — small action-workflow that tags and notes after a level completes.
- [`examples/aml-routing.json`](examples/aml-routing.json) — client-list geo gate + post-AML routing on `applicant.review.rejectLabels` (PEP / SANCTIONS / ADVERSE_MEDIA) with `containsAny` and tag-driven fan-in (mirrors real-world AML topologies).

## See also

- [references/workflow-schema.md](references/workflow-schema.md) — reference for every node type's body, the action model, the `Condition` AST + operators, the lifecycle, and the live-traffic guard.
- [references/workflow-expressions.md](references/workflow-expressions.md) — the expression-path lookup dictionary.
- [references/workflow-notices.md](references/workflow-notices.md) — the validation-notice catalog: every `notices[]` key the `validate`/`post` endpoints return, with severity, params, and how to act (ground a reference vs. fix the spec). Look up any notice you get here.
- [references/workflow-patterns.md](references/workflow-patterns.md) — composition patterns: how to decompose a KYC/KYB policy into the canonical pipeline spine and reusable primitives (strategy, not schema). Start here when the ask is "build me a workflow" rather than "fix this node".
