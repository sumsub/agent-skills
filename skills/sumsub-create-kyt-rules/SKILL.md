---
name: sumsub-create-kyt-rules
description: Configure KYT transaction monitoring rules with tags, applicant risk scoring and risk levels. TRIGGER when the user says "create / add / set up KYT rules / TM rules", "configure transaction monitoring", describes scoring logic (flag/block/hold transactions by amount, country, direction, peer, or other conditions), wants to "update / change / edit an existing rule" (by name or title), asks to "configure applicant scoring / risk scoring / assessment", "set up tags", "define risk levels / thresholds", or "configure applicant risk". SKIP for applicant levels, questionnaires, PoA presets, workflows, or non-TM tasks.
allowed-tools: Read, Write, Bash
---

# Sumsub — KYT Rules, Applicant Scoring & Risk Levels

Configures the full KYT transaction monitoring stack:

- **Rules** — translates user intent into `KytTxnRule` payloads and POSTs them one at a time. Supports creating new rules and modifying existing ones (by posting a new revision). New rules always start in **testMode** (`dryRun: true`) — they appear in `dryScore` but do not affect the live outcome until activated in the dashboard.
- **Tags & applicant scoring** — creates and configures tags (named risk markers) and the assessment that maps tag weights into a composite applicant risk score.
- **Risk levels** — configures the score thresholds that translate a numeric risk score into a human-readable label (e.g. Low / Med / High).

Rules, tags, and risk levels form a single pipeline: a rule fires → applies tags → tags accumulate a weighted score → score maps to a risk level.

## Endpoints

| Method | Path | Description | Response |
|---|---|---|---|
| `GET` | `/resources/api/agent/tm/rules/-/installed` | List existing rules. Supports `?limit=<n>` and `?offset=<n>`. Requires `seeKytRules`. | `{ list: { items: [...] } }` |
| `POST` | `/resources/api/agent/tm/rules` | Create a new rule or a new revision. For creation omit `id` and `name`. For a revision include the existing `name` slug and `"id": null`. Requires `manageKytRules`. | 200 rule object · 400 error message |
| `GET` | `/resources/api/agent/tm/rules/-/bundle/{bundleName}/{category}` | List rules in a bundle by name and installation status. `category`: `installed`, `available`, `archived`. Requires `seeKytRules`. | `{ list: { items: [...] } }` |
| `GET` | `/resources/api/agent/tm/rules/{id}` | Read one rule by id. Requires `seeKytRules`. | rule object |
| `GET` | `/resources/api/agent/tm/settings/tags` | List all KYT tags with their assessment configuration and linked rules. | `{ tags: [...] }` |
| `POST` | `/resources/api/agent/tm/settings/tag` | Create or update a KYT tag. Body: `{"tag": {"name": "...", "styleClass": "...", "color": "#RRGGBBAA", "scorable": true, "includeInReporting": true, "scoreWeight": 1.0}}`. `color` must be 8-digit hex. Requires `manageKytSettings`. | 200 empty body |
| `GET` | `/resources/api/agent/tm/settings/applicantAssessment` | Get current applicant assessment scoring configuration (tag weights, hierarchy, company beneficiary weights). | assessment settings object |
| `PATCH` | `/resources/api/agent/tm/settings/applicantAssessment` | Replace applicant assessment scoring configuration. Requires `manageKytSettings`. | 200 updated assessment settings |
| `GET` | `/resources/api/agent/tm/settings/riskLevel` | Get current applicant risk level thresholds. | risk level settings object |
| `PATCH` | `/resources/api/agent/tm/settings/riskLevel` | Replace risk level thresholds. Body: min 2 items, each with `label` (≤256), `rangeFrom` (≥0), `styleClass` — one of: `grey`, `black`, `blue`, `green`, `cyan`, `teal`, `lime`, `yellow`, `orange`, `volcano`, `red`, `pink`, `fuchsia`, `purple`, `purpleLight`. Requires `manageKytSettings`. | 200 updated risk level settings |
| `GET` | `/resources/api/agent/tm/clientLists/{listName}` | Fetch a client list by name. 404 if not found. Requires `seeClientLists`. | client list object |
| `POST` | `/resources/api/agent/tm/clientLists/{listName}` | Create a client list (idempotent). Requires `manageClientLists`. | client list object |

See [`references/kyt-rule-schema.md`](references/kyt-rule-schema.md) for the full rule SumScript expression field reference and type system.

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

## Tenant Entitlements

Entitlements are gated **per transaction type**, not globally. Each `types` value needs
**any one** of the keys listed for it — not all of them. There is no baseline entitlement
that every rule requires: `KYT` is the entitlement for the `finance` type, nothing more.

| Rule `types` value | Enabled by **any one** of |
|---|---|
| `finance` | `KYT` |
| `travelRule` | `TRAVEL_RULE` |
| `kyc` | `TM_INDIVIDUAL_APPLICANT_SCORING` · `TM_COMPANY_APPLICANT_SCORING` · `KYT_ANTI_FRAUD` · `KYT` · `DEVICE_INTELLIGENCE` |
| `userPlatformEvent` | `KYT_ANTI_FRAUD` · `KYT` |
| `scheduledEvent` | `TM_SCHEDULED_EVENTS` · `KYT` |

A tenant that has only `TRAVEL_RULE` can create `travelRule` rules. A tenant that has only
`DEVICE_INTELLIGENCE` can create `kyc` rules. Neither needs `KYT`. Do not require `KYT` for a
type whose row does not list it.

Before creating or modifying a rule, run `bash scripts/check_permissions.sh` from the
[`sumsub-check-permissions`](../sumsub-check-permissions/SKILL.md) skill directory. The response
body is `{"allowedChecks": {"<KEY>": "<description>", ...}}` — the **keys** of `allowedChecks`
are the enabled entitlements. There is no `allowed` array.

**Stop only when the requested type is not enabled** — i.e. none of the keys on that type's row
appear in `allowedChecks`. Do not build or POST that rule. Name the type **as the user sees it**
(see [Transaction Types](#transaction-types) — `kyc` is "Verification session events", never
"kyc"), list the keys that would enable it joined by "or", and tell the user to contact their CSM
or Sumsub support. Do not offer a
different transaction type as a workaround — if the user wants a `travelRule` rule, a `finance`
rule is not a substitute.

**If the entitlement request itself fails** (non-200, timeout), warn the user that entitlements
could not be verified and proceed anyway. The backend is the authority and enforces the same gate
on `POST` — see the `No allowed transaction types found` row in step 6.

> **Note on scheduled rules.** The scheduled *trigger mode* is licensed by `TM_SCHEDULED_EVENTS`
> specifically, while the `scheduledEvent` *type* is also enabled by `KYT`. A tenant with only
> `KYT` may therefore pass this gate and still be refused by the backend on `noEventTrigger`.
> Build the rule as usual and surface the backend error verbatim if that happens.

## Procedure

0. **Fetch tenant entitlements — only when creating or modifying a rule.** Run
   `sumsub-check-permissions` and keep the keys of `allowedChecks`. Once you know the rule's
   `types`, check that row in [Tenant Entitlements](#tenant-entitlements) and abort if none of
   its keys are present.

   **Skip this step entirely** for work that is not a rule: tags, applicant assessment, risk
   levels, and client lists need no entitlement. Do not look for an entitlements endpoint other
   than the one `sumsub-check-permissions` calls — there is no other one.

1. **Determine mode — create or modify.**

   - **Modify mode:** the user provides a rule `name` (immutable slug, e.g. `fin-ben-pep-ter-list-abo-thr-WoGD`) or enough context to identify one. Run `bash ${CLAUDE_SKILL_DIR}/scripts/get_kyt_rules.sh`, find the rule by `name` or `title`, and store the full current document. Show the user the existing `conditionEl`, `score`, `action`, and `types`, then collect only the fields they want to change. Skip to step 2a.
   - **Create mode:** the user describes a new rule. Run `bash ${CLAUDE_SKILL_DIR}/scripts/get_kyt_rules.sh` and check for a title collision — the server creates a duplicate on every POST with no deduplication. If a rule with a matching title already exists, offer to skip creation and modify the existing one instead.

2. **Translate user intent to compact specs.** For each rule the user wants to create, collect:
   - `title` (≤128 chars, required)
   - `types` — one or more transaction types (see table below)
   - A plain-English description of the condition (used to generate `conditionEl` in step 3)
   - `score` (integer, default 0), `action` (`score` | `onHold` | `awaitUser` | `reject`)
   - Optional: `desc`, `tags`, `bundleName`, `priority`, `stopOnMatch`, `sourceKeys`

2a. **Ensure client lists exist** — if any rule will reference `clientLists.<name>` in its `conditionEl`,
    verify each list exists before generating or validating expressions:
    ```bash
    bash ${CLAUDE_SKILL_DIR}/scripts/get_kyt_client_list.sh <listName>
    ```
    - HTTP 200 → list exists; proceed.
    - HTTP 404 → list does not exist; create it:
      ```bash
      bash ${CLAUDE_SKILL_DIR}/scripts/create_kyt_client_list.sh <listName>
      ```
    The POST is idempotent — it succeeds even if the list was created in the meantime.
    **Do not proceed to validation or rule creation** until every referenced client list is confirmed.

3. **Generate `conditionEl`.** For each rule that needs a condition:
   - Construct the SumScript boolean expression using the type definitions in
     [`references/kyt-rule-schema.md`](references/kyt-rule-schema.md).
   - **Do not guess field paths.** Only use fields confirmed in the schema — verify the path
     from root to leaf before writing the expression.
   - For default-currency amount checks use `data.info.amountInDefaultCurrency` (normalized amount),
     not `data.info.amount` (source-currency amount) — unless the user explicitly asks for
     source-currency filtering.
   - Scheduled rules (`types: ["scheduledEvent"]`) do NOT use `conditionEl` for their trigger —
     use `noEventTrigger` instead (see [references/kyt-rule-schema.md](references/kyt-rule-schema.md)).
   - For multi-branch scoring (different score per sub-condition), use `addScoreIf` inside
     `conditionEl` and set the payload-level `score: 0`, `action: "score"` (see Scoring section).

3a. **Validation is built into POST** — the server validates `conditionEl` syntax during the create call (step 6). No separate pre-flight step is needed. If validation fails the server returns HTTP 400 with an error message describing the problem — fix the expression and re-POST.

4. **Build payload.** Assemble the JSON for each rule following these constraints:

   **Create mode:**
   - **Required fields only:** `title`, `types` (min 1 value).
   - For `eval` rules: include `conditionEl`, `score`, and `action` when relevant.
   - **Never send** `id` or `name` — the server assigns both.

   **Modify mode (new revision):**
   - Include `"name": "<existing-slug>"` — the immutable slug from the existing rule.
   - Include `"id": null` — an explicit null. This signals the server to create a new revision rather than a new rule. Do **not** use `"id": ""` (empty string) — Jackson will reject it as an invalid ObjectId and return HTTP 400.
   - Carry over all unchanged fields from the existing rule document. Only change the fields the user asked to modify.
   - `title` and `types` remain required.

   **Both modes — always apply:**
   - **Never send** server-assigned or audit fields: `clientId`, `actual`, `revision`,
     timestamps (`createdAt`, `modifiedAt`, `archivedAt`), author fields.
   - **Never send** `scope` or `bgCheckTargets` — license-control fields managed by the server.
   - **Create mode:** never send `dryRun` or `disabled`; the server initialises them to `true` and `false`.
   - **Modify mode:** carry over `dryRun` and `disabled` from the existing rule document — the server uses the sent values to preserve the rule's current activation and test-mode state across the revision.
   - **Omit empty optional containers:** `sourceKeys: []`, `caseAction: {}`,
     `applicantChange: {}`, `applicantActions: {"actions": {}}`,
     `varDefinitions: {"definitions": []}`, `varValues: {"values": {}}`.
   - Do not mix `scheduledEvent` with other transaction types.

5. **Show each payload to the user and ask for explicit confirmation** before any POST.

6. **POST each rule** via `bash ${CLAUDE_SKILL_DIR}/scripts/post_kyt_rule.sh < payload.json`.
   Rules are created one at a time. Check the exit code:
   - **Exit 0** → HTTP 200; the response body is the created `KytTxnRuleView`. Proceed to step 7.
   - **Exit 1** → HTTP 4xx/5xx; the response body contains the error message. Surface it verbatim,
     fix the expression, and re-POST.

   The backend enforces the entitlement gate too. Two error messages mean the payload is fine and
   retrying it unchanged will never work — stop retrying that rule and report:
   - `No allowed transaction types found` → the tenant is not licensed for the `types` you sent.
     Tell the user which types their `allowedChecks` does enable, and advise contacting their CSM.
     Do not silently switch to a different type.
   - `Unable to enable a rule without a specified condition` → the rule needs a `conditionEl`
     (or, for `scheduledEvent`, a `noEventTrigger`).

   **Retry cap:** allow at most **10 POST attempts per rule**. If the 10th attempt still fails,
   mark that rule as **failed**, record the last error message, and move on to the next rule —
   do **not** abort the entire batch. Report all failed rules in step 9.

7. **GET each created rule back** via `bash ${CLAUDE_SKILL_DIR}/scripts/get_kyt_rule.sh {id}`.
   Compare `conditionEl` and key fields to what was sent. Report any discrepancy.

8. **Build the dashboard link** for each rule:
   ```
   https://cockpit.sumsub.com/checkus/kyt/rulesManager/rulesList/{name}?clientId={clientId}&sbx=true
   ```
   `name` and `clientId` come from the POST response body. Render as a clickable markdown link.

9. **Report** — for each rule, lead with its human-readable title:
   - **Title** and auto-generated `name` (the short immutable slug)
   - **Status:** testMode — must be activated in the dashboard to go live
   - `types`, `action`, `score`
   - Dashboard link as a clickable markdown link
   - Rule `id` on its own final line

   For rules that exhausted all 10 attempts, report them in a **Failed rules** section with the
   title and the last HTTP 400 error message.

   Surface 4xx errors verbatim.

> **⚠️ testMode default.** Every new rule starts with `dryRun: true`. It evaluates against
> transactions and its result appears in `dryScore`, but does not affect the real score or
> action. To make a rule live, open it in the dashboard and set it to "Active".

## Compact Spec Format

Express each rule as a JSON object before generating the full payload:

```jsonc
{
  "title": "Hold large outgoing transfers",         // required, ≤128 chars
  "desc": "Holds outgoing transactions over 50 000 in default currency",
  "types": ["finance"],                             // required
  "condition": "outgoing AND amount > 50 000 default currency",  // natural language → conditionEl
  "score": 100,                                     // 0 if using addScoreIf
  "action": "onHold",                              // score | onHold | awaitUser | reject
  "tags": ["HighAmount"],                           // optional; auto-created if new
  "bundleName": "AML Compliance",                   // optional group
  "priority": 10,                                   // optional; higher = evaluated first
  "stopOnMatch": false,                             // optional
  "sourceKeys": ["payment-gateway-1"]               // optional top-level filter
}
```

## Transaction Types

| Type (API value) | Name to use with the user | When to use | `conditionEl` required? | Notes |
|---|---|---|---|---|
| `finance` | finance transactions | Payment transfers, deposits, withdrawals | Yes | Most common type |
| `travelRule` | Travel Rule transactions | Travel-rule transactions | Yes | |
| `kyc` | **Verification session events** | Verification session events on an applicant | Yes | Never write "kyc" in user-facing text |
| `userPlatformEvent` | User platform events | Login, password reset, 2FA events | Yes | |
| `scheduledEvent` | Scheduled events | Periodic applicant re-checks | No (use `noEventTrigger`) | Must be alone in `types` |

Types may be combined in one rule except `scheduledEvent` which must be the only type.

**The first column is the API value; the second is what the user reads.** Put the API value in
`types` and nowhere else — in reports, refusals, and clarifying questions use the second column,
the name the dashboard shows. `kyc` is the one that actually misleads: the dashboard has no "kyc"
label anywhere, so a message naming it that way sends the user looking for something that does not
exist. The other four are only prettified, but the dashboard's wording is still the one to use.

Which types this tenant may use is gated per type — see
[Tenant Entitlements](#tenant-entitlements), the single source for that mapping.

## Rule Actions

| Action | Priority | Effect |
|---|:---:|---|
| `score` | 0 | Adds score only (default) |
| `onHold` | 5 | Holds the transaction for review |
| `awaitUser` | 7 | Awaits user action before proceeding |
| `reject` | 10 | Rejects the transaction outright |

Across all matched rules, the **strongest action wins** and scores **accumulate**.

## Scoring & `conditionEl`

**Simple rule (single threshold, one score):** Put the score in `score` and keep `conditionEl` as a pure boolean.

```json
{
  "title": "Hold high outgoing finance",
  "types": ["finance"],
  "conditionEl": "data.info.direction == 'out' AND data.info.amountInDefaultCurrency > 50000",
  "score": 100,
  "action": "onHold"
}
```

**Multi-branch scoring (different scores per sub-condition):** Use `addScoreIf` inside `conditionEl`.
Set payload `score: 0` and `action: "score"` — otherwise the payload score is double-counted.

- **`EOR` (eager OR):** every branch is evaluated, all matching branches accumulate score. Use for independent flags.
- **`OR` (short-circuit):** stops at the first matching branch. Use for mutually exclusive tiers (strictest first).

```
addScoreIf(data.info.amountInDefaultCurrency > 100000, 50) EOR
addScoreIf(applicant.country IN clientLists.sanctioned_countries, 100) EOR
addScoreIf("pep" IN applicant.riskLabels.aml, 75)
```

## Common `conditionEl` Patterns

```
# Finance: outgoing transfer over threshold
data.info.direction == 'out' AND data.info.amountInDefaultCurrency > 50000

# Finance: applicant in a client list
applicant.country IN clientLists.high_risk_countries

# Finance: incoming from specific payment type
data.info.direction == 'in' AND data.info.type == 'transfer'

# Finance: crypto transaction
data.info.currencyType == 'crypto'

# KYC: applicant review rejected
applicant.review.decision == 'rejected'

# Travel Rule: counterparty VASP not found
txn.travelRuleInfo.status == 'counterpartyVaspNotFound'

# Aggregation: applicant sent > 3 transactions in last 24 hours
txns.finance.byApplicant.out.lastHours(24).count() > 3

# Aggregation: total outgoing amount in last 30 days
txns.finance.byApplicant.out.lastDays(30).sum(it.data.info.amountInDefaultCurrency) > 100000

# KYC: questionnaire answer — nested questionnaire.section.item, dot notation only
questionnaires.myQuestionnaireId.mySectionId.myItemId == 'salary'

# KYC: same, when a segment contains a dash — backtick-quote that segment
questionnaires.`my-quest-id`.mySectionId.myItemId == 'salary'
```

Conditions on questionnaire answers have two traps that produce a rule which saves cleanly and
never matches: the bracket form does not compile, and the compared value is the option's stored
value, not the label shown to the applicant. Read
[`references/kyt-rule-schema.md`](references/kyt-rule-schema.md) → `questionnaires` before writing
one, including how to look up the three ids.

For the full type system and all available fields, see [`references/kyt-rule-schema.md`](references/kyt-rule-schema.md).

## Client Lists

Client lists are named sets of values (countries, currencies, peer IDs, etc.) referenced in `conditionEl` as `clientLists.<listName>`. A list must exist before a rule that references it can be validated or created.

### Checking and creating a list

```bash
# Check if a list exists
bash ${CLAUDE_SKILL_DIR}/scripts/get_kyt_client_list.sh high_risk_countries

# Create a list (idempotent)
bash ${CLAUDE_SKILL_DIR}/scripts/create_kyt_client_list.sh high_risk_countries
```

The POST creates an empty list if it doesn't exist and returns the list document either way.

### Required permissions

| Operation | Permission |
|---|---|
| GET (read) | `seeClientLists` |
| POST (create) | `manageClientLists` |

If the GET returns 403, `seeClientLists` is missing. If the POST returns 403, `manageClientLists` is missing. In both cases, tell the user the missing permission and stop.

### Usage in `conditionEl`

Reference a list by its exact name after the `clientLists.` prefix:

```
# Country in a named list
applicant.country IN clientLists.high_risk_countries

# Peer wallet not in an allowlist
NOT (txn.counterparty.wallet IN clientLists.approved_wallets)

# Combined
applicant.country IN clientLists.sanctioned_countries AND data.info.amountInDefaultCurrency > 1000
```

List contents are managed separately in the Sumsub dashboard (KYT → Client Lists) — the API endpoints only create an empty list; adding values is a dashboard-only operation.

## Tags

Tags link rule matches to applicant-level risk assessment:

- Add `tags: ["TagName"]` to a rule — the tag name auto-creates in KYT settings if new.
- When the rule matches, each tag accumulates the rule's score for the applicant.
- The `applicantAssessment` post-scoring runner aggregates tag scores into the applicant risk profile.

## Scheduled Rules (`scheduledEvent`)

Scheduled rules fire without an incoming transaction. They find applicants based on trigger criteria
and generate synthetic events. See [`references/kyt-rule-schema.md`](references/kyt-rule-schema.md)
for the full `noEventTrigger` structure.

Key constraints:
- `types` must be exactly `["scheduledEvent"]` — cannot be combined with other types.
- Must include `applicantChange` or `applicantActions` (at least one).
- `conditionEl` is optional (use for secondary filtering, not as the primary trigger).
- `noEventTrigger.type` is either `byLevelName` (approved applicants at a level, N days after review)
  or `byCustomExpression` (free-form applicant filter expression).

Minimal scheduled rule:
```json
{
  "title": "Annual KYC refresh",
  "types": ["scheduledEvent"],
  "noEventTrigger": {
    "type": "byLevelName",
    "levelParams": {
      "levelName": "basic-kyc-level",
      "days": 365
    }
  },
  "applicantChange": {
    "type": "applicantLevel",
    "applicantLevel": {
      "levelName": "re-verification-level"
    }
  }
}
```

## Case Creation on Match

To automatically create a compliance case when a rule matches, add `caseAction`:

```json
{
  "caseAction": {
    "createCase": true,
    "groupByType": "byApplicant",
    "blueprintId": "<case-blueprint-id>",
    "priority": "high",
    "deadlineHours": 24
  }
}
```

`groupByType`: `byRule` (one case per rule) or `byApplicant` (one case per applicant, transactions grouped).
`blueprintId` is optional — omit to use the default case template.

## Modifying an Existing Rule

To update a rule, POST a new revision to the same endpoint used for creation. The server replaces the current revision atomically and increments `revision`.

### Identify the rule

The user must supply the rule's `name` (immutable slug) or enough context to identify it by title. List all rules and find the match:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/get_kyt_rules.sh | python3 -c "
import json, sys
items = json.load(sys.stdin).get('list', {}).get('items', [])
for r in items:
    if r.get('name') == 'fin-ben-pep-ter-list-abo-thr-WoGD':
        print(json.dumps(r, indent=2))
"
```

Or search by title substring:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/get_kyt_rules.sh | python3 -c "
import json, sys
items = json.load(sys.stdin).get('list', {}).get('items', [])
for r in items:
    if 'PEP' in r.get('title', '').upper():
        print(json.dumps(r, indent=2))
"
```

Show the matching rule's current `conditionEl`, `score`, `action`, and `types` to the user before proceeding.

### Payload shape

Take the existing rule document, apply only the user's requested changes, then:
- Set `"id": null` — explicit null (signals new revision, not new rule). Never use `""` — it fails Jackson ObjectId deserialization with HTTP 400.
- Keep `"name": "<slug>"` — the existing immutable slug.
- Strip server-managed fields: `clientId`, `actual`, `revision`, `scope`, `bgCheckTargets`, timestamps, author fields.
- **Keep** `dryRun` and `disabled` from the existing document — they preserve the rule's current activation and test-mode state across the revision.

```json
{
  "id": null,
  "name": "fin-ben-pep-ter-list-abo-thr-WoGD",
  "title": "Finance — Beneficiary in PEP and terror list above threshold",
  "types": ["finance"],
  "conditionEl": "beneficiary.fullName IN clientLists.pep_and_terror AND data.info.amountInDefaultCurrency > 5000",
  "score": 100,
  "action": "onHold",
  "dryRun": true,
  "disabled": false
}
```

### Validate before posting

If `conditionEl` changed, the POST validates it automatically. If the server returns HTTP 400, fix the expression and re-POST (same 10-attempt cap as create mode applies).

### After posting

- The response contains the new `id` (the latest revision gets a new id), old `name`, `revision` number, and all rule fields.
- GET the rule back by the new `id` to verify.
- The dashboard link uses the old `name`:
  ```
  https://cockpit.sumsub.com/checkus/kyt/rulesManager/rulesList/{name}?clientId={clientId}&sbx=true
  ```
- Report the new `revision` number alongside the title and updated fields.

## Applicant Risk Scoring

Applicant risk scoring calculates a composite risk score for each applicant based on the transaction monitoring rules that matched them. The score is built from three layers configured independently:

```
Rules (produce tags on match)
  └─ Tags (each carries a score weight)
       └─ Assessment (maps tags → weighted score)
            └─ Risk Levels (score thresholds → Low / Med / High label)
```

### How it works

1. **Rules fire** — when a TM rule matches a transaction, it applies its `tags` to the applicant.
2. **Tags accumulate** — each tag carries a `scoreWeight`. Multiple rule matches sum tag scores.
3. **Assessment aggregates** — the assessment config controls which tags count toward the total score (`includeInTotalScore`), their relative weights (`scoreWeight`), and optional hierarchy (`items`).
4. **Risk level assigned** — the total score is compared against `riskLevelThresholds` to produce a human-readable risk label (e.g. Low / Med / High).

For companies, `companyBeneficiarySettings` in the assessment applies role-based weights (UBO, director, shareholder…) so the applicant's score accounts for the risk of their associated parties.

### Configuring applicant scoring — step by step

**Step 1 — Create/update tags**

```bash
echo '{"tag": {"name": "HighValue", "styleClass": "red", "color": "#FF000080", "scorable": true, "scoreWeight": 1.0}}' \
  | bash scripts/post_kyt_tag.sh
```

Read back all tags to confirm:
```bash
bash scripts/get_kyt_tags.sh
```

**Step 2 — Configure assessment**

Map tags to weighted scores. `id` is a client-assigned stable identifier for the entry.

```json
{
  "scores": [
    {
      "id": "high-value-score",
      "tag": "HighValue",
      "includeInTotalScore": true,
      "scoreWeight": 1.0
    }
  ],
  "companyBeneficiarySettings": [
    { "beneficiaryType": "ubo",      "weight": 1.0 },
    { "beneficiaryType": "director", "weight": 0.5 }
  ]
}
```

Valid `beneficiaryType` values: `shareholder`, `representative`, `director`, `ubo`, `companyOfficer`, `secretary`, `founder`, `investor`, `legalAdvisor`, `authorizedSignatory`, `trustee`, `trustBeneficiary`, `trustSettlor`, `trustProtector`, `payer`.

```bash
# Read current
bash scripts/get_kyt_applicant_assessment.sh

# Apply new config
echo '<payload>' | bash scripts/patch_kyt_applicant_assessment.sh
```

**Step 3 — Configure risk level thresholds**

```bash
# Read current
bash scripts/get_kyt_risk_level_settings.sh

# Apply new thresholds (min 2 required)
echo '{"riskLevelThresholds": [
  {"label": "Low",  "rangeFrom": 0,   "styleClass": "green"},
  {"label": "High", "rangeFrom": 75,  "styleClass": "red"}
]}' | bash scripts/patch_kyt_risk_level_settings.sh
```

### Tags in rules

Add `tags` to a rule's payload to connect rule matches to the assessment:

```json
{
  "title": "Flag high-value transfers",
  "types": ["finance"],
  "conditionEl": "data.info.amountInDefaultCurrency > 10000",
  "score": 50,
  "action": "score",
  "tags": ["HighValue"]
}
```

When this rule matches, the `HighValue` tag is applied to the applicant and its weight contributes to their risk score.

## See Also

- [`references/kyt-rule-schema.md`](references/kyt-rule-schema.md) — full field reference and SumScript type system
- [`examples/minimal.json`](examples/minimal.json) — bare-minimum working payload
- [`examples/eval-finance-hold.json`](examples/eval-finance-hold.json) — complete finance hold rule
- [`scripts/get_kyt_bundle.sh`](scripts/get_kyt_bundle.sh) — list rules in a bundle by name and category (`installed` | `available` | `archived`)
- [`scripts/get_kyt_tags.sh`](scripts/get_kyt_tags.sh) — list all KYT tags with assessment config and linked rules
- [`scripts/post_kyt_tag.sh`](scripts/post_kyt_tag.sh) — create or update a KYT tag (requires `manageKytSettings`)
- [`scripts/get_kyt_applicant_assessment.sh`](scripts/get_kyt_applicant_assessment.sh) — get applicant assessment scoring configuration
- [`scripts/patch_kyt_applicant_assessment.sh`](scripts/patch_kyt_applicant_assessment.sh) — replace applicant assessment scoring configuration (requires `manageKytSettings`)
- [`scripts/get_kyt_risk_level_settings.sh`](scripts/get_kyt_risk_level_settings.sh) — get current applicant risk level thresholds
- [`scripts/patch_kyt_risk_level_settings.sh`](scripts/patch_kyt_risk_level_settings.sh) — replace applicant risk level thresholds (min 2, requires `manageKytSettings`)
- [`scripts/get_kyt_client_list.sh`](scripts/get_kyt_client_list.sh) — check whether a client list exists by name
- [`scripts/create_kyt_client_list.sh`](scripts/create_kyt_client_list.sh) — create a client list (idempotent)
- [`sumsub-create-transaction`](../sumsub-create-transaction/SKILL.md) — submit test transactions to verify rules
- [`sumsub-check-permissions`](../sumsub-check-permissions/SKILL.md) — check tenant entitlements
- [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md) — authentication reference
