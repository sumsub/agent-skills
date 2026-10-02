# Composition patterns — how to decompose a verification policy

The schema (in [workflow-schema.md](workflow-schema.md)) tells you what's *legal*. This
file is about what's *idiomatic*: how to turn "build me a KYC/KYB workflow" into a graph,
based on recurring shapes in real production workflows. It is **strategy, not schema** —
node-graph structure first, expression paths only as illustration. Don't treat the paths
here as an authoritative vocabulary; reach for the discovery API / [workflow-expressions.md](workflow-expressions.md)
for that.

These idioms shape what the user left **unspecified**. They never license dropping, merging,
or renaming a level or node the user explicitly named — if an idiom seems to conflict with an
explicit input, the input wins; surface the tension, don't resolve it silently.

## Start at the macro shape: a workflow is a forest of *segment pipelines*

A large workflow is the cross-product **{segment} × {policy}**, where a segment is
`{region} × {applicant type / entity class}` — e.g. *US-individual*, *CA-regulated-KYB*,
*LT-tech-provider-KYB*. Each cell is a near-identical **pipeline**, and the pipelines are
**replicated, not shared** — same spine, segment-specific client lists. A consolidated
real workflow is ~20 copies of one spine, each its own disconnected component (a root
level with no incoming edge). See the forest / fixed-applicant-type constraint in
[workflow-schema.md](workflow-schema.md#constraints-product-semantics).

So the first decomposition question is never "what nodes" — it's:

1. **What are my segments?** (regions × applicant types / entity classes)
2. **What is the one pipeline I'll stamp per segment?**
3. **What differs per segment?** (usually just which named client lists / levels it points at)

## The canonical pipeline spine

A KYC flow is a linear spine with branch-offs, in this order (cheapest/most-decisive
gates first):

1. **Entry level** — collect + verify identity (`applicantLevel`).
2. **Eligibility gate** — geo / prohibited-country → *hard stop*. First, because it's the
   cheapest decisive check.
3. **Screening gate** — PEP / sanctions / adverse-media → manual review.
4. **Data-quality gates** — missing DoB, declared-vs-document mismatch, bad email domain →
   remediation level or reject.
5. **Risk scoring** — questionnaire score → tier → tag (and optionally an EDD level upgrade).
6. **Conditional EDD** — age / score / geo → route into a heavier level.
7. **Terminal** — implicit approve, manual review, or final reject.

**KYB** is the same spine with two swaps: step 1 becomes *entity classification* (tag
Regulated / Non-regulated / Tech-provider, then run a class-specific score ladder), and it
adds a *"not found in external DB"* gate. Everything else mirrors KYC.

## Chaining levels is cheap: transitions capture only the diff

A flow with several sequential `applicantLevel`s does **not** make the applicant re-submit
anything. When an applicant moves from level A to level B, Sumsub captures only the **diff** —
what B requires that A hasn't already satisfied. This is core level-transition behaviour (it
fires whenever a level changes — workflow, API, or operator — it is **not** a workflow feature):

- Already collected and approved on A, also needed by B → **reused automatically**, no applicant
  involvement.
- Same item, but B's verification settings differ → **re-verified** under B's settings (process
  only, no re-capture).
- A's capture method can't satisfy B's → the applicant **re-captures**, but only that item.

Applies to all level settings, not just ID documents. So **never merge or drop a level to avoid
"double capture"** — sequential levels are not redundant.

**The flip side: an escalation / EDD target must be a *superset*.** Because the transition reuses
everything already collected and approved, a level that requires *less* than the applicant already
has adds nothing — the diff is trivial and they breeze through. An "EDD" or "enhanced" level that
only adds a questionnaire, with **no** new document/verification requirements, actually **lowers**
the bar: the applicant fills a form and is approved on reused data. Escalation must *add*
requirements — more documents, stricter verification settings, or screening not yet run — or it is
toothless. (And if the applicants you route there still need a check the target omits — e.g. AML —
they now **skip** it: the target's *contents*, not its name, decide what actually runs.)

**Stage expensive work behind gates.** Because chaining is cheap and each level only does its own
work, pull a *costly* verification into its own level and gate it behind a condition: run the
cheap, decisive checks first, then incur the expensive one only for applicants who need it. E.g.
do basic identity first and run **AML / watchlist screening** (or liveness, EDD, a paid
data-source lookup, …) only when a condition warrants — higher risk score, specific countries, a
self-declared questionnaire answer. (The trigger must be data you already have — you can't gate AML
on a PEP flag, since that flag *is* AML's output; see *Place each gate at the earliest point*.)
Low-risk applicants finish faster and you don't pay for checks they didn't trigger.
(This is the level-level form of the spine's cheapest-first ordering. *Whether* a given check may
be deferred is a policy call — some screening is mandatory for everyone — but the graph makes the
gating possible.)

**Place each gate at the earliest point its inputs exist — and split gates that mix.** A condition
that reads a level's *output* (e.g. `applicant.review.rejectLabels`, produced by AML) must come
*after* that level; a condition that doesn't (geo / declared country / `poi.country`) belongs
*before* it, so the expensive level is gated. The common mistake is collapsing both into one choice
*after* the costly level. Split them: in the AML pattern, the **embargo** and **high-risk-*country***
checks read only country, so they gate **before** the AML level (you don't pay for AML on someone
you're embargo-rejecting); only the **sanctions / PEP `rejectLabels`** checks — which consume AML's
output — go **after**. Lumping the country checks after AML both wastes the AML run on applicants
you'll reject anyway and flattens the cheapest-decisive-gate-first ordering into a single late
node. A gate reading data nothing upstream has produced yet is also what the validator's
data-availability warnings catch (e.g. `idDocWarning`) — see [workflow-notices.md](workflow-notices.md).

## The reusable primitives

Each idiom is a tiny sub-graph. Compose the spine out of these.

| Idiom | Sub-graph | Node types |
|---|---|---|
| **Hard gate** | condition → final reject | `exclusiveChoice` → `finalRejection` |
| **Soft gate** | condition → manual review | `exclusiveChoice` → `manualReview` |
| **Remediation** | condition → extra level → rejoin the spine **downstream** (forward fan-in — never a back-edge) | branch-off `applicantLevel` |
| **Risk-tier ladder** | else-cascade of conditions, each → tag | one `exclusiveChoice` (ordered out-edges) + `actions` |
| **Flag / workflow-local state** | action writes a tag … a later condition reads it | `actions` → … → `exclusiveChoice` |
| **Escalation** | condition + `on:[approved]` → heavier (superset) level | `exclusiveChoice` → `applicantLevel` |
| **Classification** | tag the class → class-specific sub-pipeline | `actions` → branch |

Two that aren't obvious from the schema:

- **Tags as inter-node state.** A flag pair like `… pending` / `… completed` is a
  hand-rolled state machine: an `actions` node sets the tag, a downstream `exclusiveChoice`
  routes on `tags contains …`. Tags aren't only output — they're how stages communicate.
  Reach for this instead of trying to thread data structurally between nodes.
- **The risk-tier ladder is an else-cascade on one choice.** A single `exclusiveChoice` whose
  out-edges are `High` *else→* `Medium` *else→* `Low`, each routing to its own tag action.
  Out-edges are evaluated in declared order (first match wins); the final edge with **no**
  `condition:`/`on:` is the implicit *else*. This is the idiomatic if / elif / else — one node,
  not a chain.

## Iteration without cycles: the resubmission gate

> **Opt-in only — do not build this unless the user explicitly asks for it.** Resubmission
> handling is **not** part of a standard workflow. The engine already retries automatically, and
> that is what almost every workflow wants. Build a gate **only** when the user asks in so many
> words to cap, limit, or otherwise act on repeated attempts ("after 3 tries send to manual
> review", "stop letting them retry forever"). Absent that explicit ask, **never mention
> `resubmission` at all** — leaving it out *is* the correct, complete design. If you're adding it
> "to be thorough" or "because a good KYC flow has it," stop: you're introducing a bug surface
> (see the interlock below) for behavior the user didn't request.

The graph is a **DAG** — no back-edges — so you never draw a "try again" loop. Iteration is the
**engine's** job: when a level returns `resubmission`, it **holds the applicant on that level**
for another attempt (`applicant.review.attemptCnt` counts them). You get this for free by simply
*not* mentioning `resubmission`.

The rest of this section applies **only** once the user has asked for an attempt cap (or similar).
The canonical case is "after N tries, send to manual review instead of looping."

Two primitives make it work:

1. Omitting `on:` makes an edge **decision-agnostic** — it doesn't check the review decision.
2. A resubmitter **stays on the level** unless some branch on the **immediate** post-level choice
   names `resubmission` (naming it anywhere opens the gate — an interlock so an approved-oriented
   condition can't accidentally release a half-verified applicant).

Together they explain the everyday case: a plain edge effectively serves **approved + rejected**,
and resubmission falls through to retry — not because the edge has a default decision set, but
because resubmission stays put until you open the gate.

So to cap attempts, **name `resubmission` only on the branch that intercepts it, with the
intercept condition on that same branch — on the immediate post-level choice:**

```
idv  → gate                                              # plain: level → its choice
gate → manual   on:[resubmission]  cond: attemptCnt > 3  # cap → escalate to human
gate → approve  on:[approved]                            # verified → continue
# resubmission ≤3 matches nothing on gate → stays on the level & retries
```

**Don't split it.** An unconditional `on:[resubmission]` release feeding a *downstream*
`attemptCnt` gate breaks retry silently: the resubmitter exits on attempt 1 — past the only node
that can hold it — and flows on *as if verified*. The scope is the immediate choice only; once an
applicant leaves the level, normal routing applies.

**The interlock — opening the gate changes every sibling edge.** This is the trap. The moment one
edge on a choice names `resubmission`, the gate is open and resubmission decisions are matched
against **all** of that choice's edges in declared order — including any **decision-agnostic** one.
So a conditioned decision-agnostic edge (e.g. an embargo reject: no `on:`, just a country
condition) will **catch a resubmitter** whose condition is true — an embargoed applicant's *first*
resubmission gets terminally region-rejected instead of being allowed to retry. Therefore:

> **On a choice whose gate is open, every edge must be decision-scoped.** Once you add an
> `on:[resubmission]` branch, give every *other* edge an explicit `on:` (`[approved]`,
> `[rejected]`, …). Only a **bare, condition-less else** is safe to leave open — anything with a
> condition will pull a resubmitter the moment that condition holds. (On a choice with **no**
> `resubmission` branch — the normal case — decision-agnostic terminal rejects are fine; see the
> conventions below. The hazard exists *only* once the gate is open.)

The approve/continue path is `on:[approved]`, not a plain else, for the same reason — a plain else
would also swallow `rejected`.

## Authoring conventions the examples agree on

- **OR the verified and declared slots.** Any user-supplied field is checked in both its
  verified form and its entered form (e.g. `fixedInfo.*` OR `info.*`) — testing only one
  leaks cases. Geo gates typically OR residence **and** nationality **and** country across
  both slots.
- **Policy lives in tiered named client lists**, not hardcoded country arrays — e.g.
  per-region `…_low/medium/high_risk_level` and `…_prohibited_and_sanctioned_countries`.
  The graph just references the lists; updating policy = editing the list, not the workflow.
  Build and populate them with [`sumsub-manage-client-lists`](../../sumsub-manage-client-lists/SKILL.md).
- **Keep a small, consistent tag taxonomy** reused across segments: risk-level tags,
  process-state flags, entity-class tags.
- **Gate every sequential level transition through a condition node** — a level's own
  out-edge is unconditional, and progressing resets verification state, so branching always
  happens at an `exclusiveChoice`.
- **One choice per gating point — don't chain choices.** All the gating between the same two
  levels belongs on a **single** `exclusiveChoice`: ordered out-edges, first match wins (the
  if/elif/else). Two choices with no level or `actions` node between them collapse into one — a
  new choice is *earned* only when a level/action sits between the gates. "Two separate policy
  gates" is **not** a reason to split: several checks evaluable at the **same point** — e.g.
  embargo + high-risk-country + re-attempt right after the entry level — are **one** choice with
  ordered branches, not three chained nodes. (What counts as the "same point" is set by data
  dependency: a check needing a *later* level's output lives at a later point — see *Place each
  gate at the earliest point its inputs exist*.)
  Splitting *is* legitimate when it genuinely helps — several paths fanning into one shared
  condition (reuse via multiple in-edges), readability, or breaking up an oversized node — but
  default to one. (This is an authoring choice now, not the builder's: it no longer
  auto-inserts choices, so the chain you write is the chain you get.)
- **A branch that routes onward into a further level or approval carries `on:[approved]`.**
  Sending an applicant *deeper into verification* — an EDD/escalation level, a continue path, an
  approve action — should gate on `on:[approved]`: only an approved applicant should proceed. The
  trap is a decision-agnostic branch that routes *onward*: it silently pulls `rejected` applicants
  into a verification/approve path, the same leak as routing `rejected` into auto-approve.
- **Decision-agnostic terminal rejects are safe — but only while the choice's gate is closed.**
  On a normal choice (no `resubmission` branch), a hard-stop reject (embargo, sanctions) or a
  manual-review escalation (sanctions/PEP label → human review) *should* fire on any decision.
  **The instant any edge on that choice names `resubmission`, that stops being safe** — every edge
  must then be `on:`-scoped (see *the interlock* under *Iteration without cycles* for why). Since
  you only ever open a gate when the user explicitly asked for resubmission handling, this only
  arises there.

## Worked topologies in this skill

- [`examples/country-routing.json`](../examples/country-routing.json) — the spine in
  miniature: entry → eligibility gate (region-reject vs IDV) → IDV → result choice →
  manual-review on rejection (two choices, because the IDV level sits between them).
- [`examples/aml-routing.json`](../examples/aml-routing.json) — eligibility gate +
  screening gate + tag-driven fan-in to manual review.
- [`examples/action-workflow.json`](../examples/action-workflow.json) — post-verification
  tagging in an action workflow.
