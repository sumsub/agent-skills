# KYT Rule Schema Reference

## KytTxnRule — All Fields

### Identification & Metadata

| Field | Type | Description |
|---|---|---|
| `id` | String | Auto-assigned primary key. **Never send on create.** |
| `name` | String | Immutable slug auto-generated from `title` on creation. Max 64 chars. |
| `title` | String | Required. Human-readable name shown in UI. Max 128 chars. |
| `desc` | String | Optional detailed description. |
| `bundleName` | String | Bundle this rule belongs to. Max 128 chars. |
| `clientId` | String | Set from auth context. **Never send.** |

### Execution

| Field | Type | Default | Description |
|---|---|---|---|
| `types` | `List<String>` | — | Required. Transaction types (see below). Min 1 value. |
| `stage` | String | `eval` | `eval` only (do not set `pre` or `post` via this skill). |
| `priority` | Integer | — | Higher value = evaluated first. |
| `stopOnMatch` | Boolean | `false` | Stop processing remaining rules on match (only when not in dryRun). |
| `sourceKeys` | `List<String>` | — | Top-level source-key filter. If set and non-empty, rule only fires if the transaction's source key is in this list. |

### Conditions

| Field | Type | Description |
|---|---|---|
| `conditionEl` | String | SumScript boolean expression. Required for non-scheduled eval rules. |
| `varDefinitions` | Object | Variable definitions for parameterized rules. Omit unless needed. |
| `varValues` | Object | Variable runtime values. Omit unless needed. |

### Actions on Match

| Field | Type | Default | Description |
|---|---|---|---|
| `score` | Integer | `0` | Risk score added when rule matches. Use `0` when using `addScoreIf`. |
| `action` | String | `score` | `score` \| `onHold` \| `awaitUser` \| `reject`. Strongest action across all matched rules wins. |
| `tags` | `List<String>` | — | Tags assigned to the transaction on match. Auto-created in KYT settings if new. |
| `caseAction` | Object | — | Case creation config (see Case Action below). Omit if not needed. |
| `applicantChange` | Object | — | Applicant workflow change on match. Required for scheduled rules. |
| `applicantActions` | Object | — | Additional applicant actions. Required for scheduled rules if no `applicantChange`. |
| `txnActions` | `List<Object>` | — | Transaction property actions (e.g. `setProp`). |

### Scheduling (scheduled rules only)

| Field | Type | Description |
|---|---|---|
| `noEventTrigger` | Object | Trigger config for `scheduledEvent` rules (see Scheduled Rules section below). |

### Server-assigned (never send)

`actual`, `revision`, `scope`, `bgCheckTargets`,
`createdAt`, `modifiedAt`, `archivedAt`, `createdBy`, `modifiedBy`

---

## Transaction Types

Transaction types, their descriptions, and the combination rules: see the
`Transaction Types` section of [`../SKILL.md`](../SKILL.md).

Entitlements are gated per type, and each type is enabled by **any one** of several keys.
The mapping lives in one place only — the `Tenant Entitlements` section of
[`../SKILL.md`](../SKILL.md). Do not restate it here.

---

## Rule Statuses

| Status | `disabled` | `dryRun` | Behaviour |
|---|---|---|---|
| `testMode` (default) | `false` | `true` | Evaluates; result goes to `dryScore` only |
| `active` | `false` | `false` | Live — affects real score and action |
| `inactive` | `true` | — | Not evaluated |

**All new rules start in testMode.** Activate in the dashboard.

---

## SumScript Expression Root (`KytTxnExpressionRoot`)

The root context available inside `conditionEl`:

| Field | Type | Description |
|---|---|---|
| `data` | `TxnDataExpressionData` | Transaction data provided by the client |
| `txn` | `TxnExpressionData` | Sumsub-side transaction metadata |
| `applicant` | `KytTxnApplicantExpressionData` | Applicant as known to Sumsub |
| `counterparty` | `TxnParticipantExpressionData` | The other party in the transaction |
| `remitter` | `TxnParticipantExpressionData` | Sender (applicant on outgoing, counterparty on incoming) |
| `beneficiary` | `TxnParticipantExpressionData` | Receiver (applicant on incoming, counterparty on outgoing) |
| `txns` | `KytTxnExpressionTypes` | Transaction aggregates (lazy-loaded). See Aggregation section. |
| `clientLists` | `ClientLists` | Named client lists — `clientLists.listName.contains(value)` or `value IN clientLists.listName` |
| `poi` | `PoiExpressionData` | Applicant proof of identity |
| `poa` | `PoaExpressionData` | Applicant proof of address |
| `questionnaires` | Object | Questionnaire answers, nested by questionnaire → section → item. Dot notation only — see the `questionnaires` section below. |
| `service` | `ServiceExpressionData` | Service-level data enriched during pre-scoring (e.g. crypto screening, AML, travel rule) |
| `preScoringContext` | `ServiceExpressionData` | **Deprecated alias of `service`** — emit `service.*` instead |
| `checks` | `KytBackgroundChecksExpressionData` | Background checks information |
| `currentRule` | `TxnMatchedRuleExpressionData` | The rule currently being evaluated — `.name`, `.title`, `.id`, `.score`, `.tags`, `.dryRun`, `.revision`, `.sourceKeys` |
| `currentFailedRules` | `STRING[]` | Names of rules failed during the current rule matching process |
| `applicantAction` | `ApplicantActionExpressionData` | The applicant action that triggered the current scoring |
| `currentScore` | INT | Accumulated score from preceding rules |
| `currentMatchedRuleNames` | `STRING[]` | Names of already-matched rules this session |
| `txnFraudInfo` | `KytTxnFraudExpressionData` | Fraud analysis data (behavioral, device, IP, email, phone) |

---

## `data` — Transaction Data (`TxnDataExpressionData`)

| Field | Type | Description |
|---|---|---|
| `data.info` | `TxnInfoExpressionData` | Financial info (see below) |
| `data.type` | STRING | Transaction type: `finance`, `kyc`, `travelRule`, `userPlatformEvent`, `scheduledEvent` |
| `data.txnId` | STRING | Client-supplied transaction ID |
| `data.txnDate` | DATE | Transaction date (client-side UTC) |
| `data.sourceKey` | STRING | Source key assigned to the transaction |
| `data.applicant` | `TxnParticipantExpressionData` | Applicant as reported in the transaction payload |
| `data.userPlatformEventInfo` | Object | For `userPlatformEvent` type: `.type` (`login`\|`failedLogin`\|`signup`\|…), `.twoFaUsed`, `.passwordHash` |

### `data.info` — Financial Info (`TxnInfoExpressionData`)

| Field | Type | Description |
|---|---|---|
| `data.info.amount` | FLOAT | Amount in source currency |
| `data.info.amountInDefaultCurrency` | FLOAT | Amount normalized to tenant default currency **Use this for threshold checks** |
| `data.info.currencyCode` | STRING | Source currency code (e.g. `USD`, `EUR`) |
| `data.info.defaultCurrencyCode` | STRING | Tenant default currency code |
| `data.info.currencyType` | STRING | `fiat` \| `crypto` |
| `data.info.direction` | STRING | `in` (received) \| `out` (sent) |
| `data.info.type` | STRING | Transfer subtype: `transfer`, `deposit`, `withdrawal` |
| `data.info.paymentDetails` | STRING | Free-text payment comment |
| `data.info.mcc` | INT | Merchant category code |

---

## `applicant` — Applicant (`KytTxnApplicantExpressionData`)

| Field | Type | Description |
|---|---|---|
| `applicant.externalUserId` | STRING | Client-side user ID |
| `applicant.country` | STRING | ISO 3166-1 alpha-3 country |
| `applicant.fullName` | STRING | Full name |
| `applicant.email` | STRING | Email address |
| `applicant.phone` | `PhoneExpressionData` | `.number`, `.country` |
| `applicant.type` | STRING | `individual` \| `company` |
| `applicant.tags` | `STRING[]` | Applicant-level tags |
| `applicant.riskLabels.aml` | `STRING[]` | AML risk labels: `pep`, `sanctions`, `terrorism`, `crime`, `adverseMedia`, `fitnessProbity` |
| `applicant.riskLabels.crossCheck` | `STRING[]` | Cross-check signals: `addressCountryVsIpCountryMismatch`, `manyAccountDuplicates`, … |
| `applicant.riskLabels.device` | `STRING[]` | Device risk: `vpnUsage`, `torUsage`, `highRiskIp`, … |
| `applicant.review.decision` | STRING | `approved` \| `rejected` \| `resubmission` |
| `applicant.assessment.totalScore` | FLOAT | Aggregated applicant risk score |
| `applicant.fixedInfo` | `ApplicantInfoExpressionData` | Basic applicant information **as provided to the SDK / API / dashboard** |
| `applicant.info` | `ApplicantInfoExpressionData` | Applicant information **extracted from documents** |
| `applicant.emailDomain` | STRING | Email domain name |
| `applicant.countryOfBirth` | STRING | ISO 3166-1 alpha-3 |
| `applicant.registrationDate` | `DateExpressionData` | When the client started the relationship with the applicant |
| `applicant.allMemberRoles` | `STRING[]` | `shareholder`, `representative`, `director`, `ubo`, … |
| `applicant.metadata` | `MAP<STRING, STRING>` | Applicant metadata |
| `applicant.checks.watchlist.matchStatuses` | `STRING[]` | Watchlist results: `unknown`, `no_match`, `potential_match`, `false_positive`, `true_positive` |

---

**`info` vs `fixedInfo`** — same type, different provenance: `fixedInfo` is what the client sent,
`info` is what was read off the documents. A condition on one will match different applicants than
the same condition on the other, so pick deliberately.

Both carry: `.firstName`, `.lastName`, `.middleName` (+ `.firstNameEn` / `.lastNameEn` / `.middleNameEn`),
`.dob`, `.age`, `.gender`, `.country`, `.nationality`, `.residenceCountry`, `.taxResidenceCountry`,
`.countryOfBirth`, `.address` / `.addresses`, `.phone`, `.tin`, `.tinCountries`.

---

## `counterparty` / `remitter` / `beneficiary` (`TxnParticipantExpressionData`)

| Field | Type | Description |
|---|---|---|
| `.fullName` | STRING | Full name |
| `.externalUserId` | STRING | Client-side ID |
| `.email` | STRING | Email |
| `.phone` | STRING | Phone number |
| `.type` | STRING | `individual` \| `company` |
| `.residenceCountry` | STRING | ISO 3166-1 alpha-3 |
| `.address.country` | STRING | ISO 3166-1 alpha-3 |
| `.paymentMethod.accountId` | STRING | Bank account / card / crypto address |
| `.paymentMethod.type` | STRING | `card`, `account`, `crypto` |
| `.institutionInfo.code` | STRING | Bank BIC/SWIFT code |
| `.institutionInfo.name` | STRING | Bank name |
| `.device.ipInfo.country` | STRING | IP country (alpha-3) |
| `.firstName` / `.lastName` | STRING | Given / family name |
| `.dob` | DATE | Date of birth |
| `.placeOfBirth` | STRING | Place of birth |
| `.nameType` | STRING | `aliasName`, `birthName`, `maidenName`, `legalName`, `shortName`, `other` |
| `.idDoc.number` | STRING | Identity document number |
| `.idDoc.country` | STRING | Document issuing country (alpha-3) |
| `.idDoc.idDocType` | STRING | `ID_CARD`, `PASSPORT`, `TRAVEL_PASSPORT`, `DRIVERS`, `SNILS`, `RESIDENCE_PERMIT`, … |
| `.idDoc.registrationAuthority` | STRING | Issuing authority |
| `.registrationNumber` | STRING | Company registration number |
| `.licenseNumber` | STRING | Licence number |
| `.leiCode` | STRING | Legal Entity Identifier |

---

## `txn` — Sumsub Transaction Metadata (`TxnExpressionData`)

| Field | Type | Description |
|---|---|---|
| `txn.createdAt` | DATE | When the transaction was received by Sumsub |
| `txn.externalUserId` | STRING | Applicant external ID |
| `txn.tags` | `STRING[]` | Transaction-level tags already assigned |
| `txn.review.decision` | STRING | `approved` \| `rejected` \| `resubmission` |
| `txn.scoringResult.score` | INT | Final score after all rules |
| `txn.travelRuleInfo.status` | STRING | Travel rule state: `completed`, `counterpartyVaspNotFound`, `awaitingCounterparty`, … |

---

## `txns` — Aggregates (`KytTxnExpressionTypes`)

Access transaction aggregates via `txns.<type>.<groupBy>.<timeWindow>.<op>(...)`.

### Types

| Root field | Covers |
|---|---|
| `txns.finance` | Finance transactions |
| `txns.travelRule` | Travel Rule transactions |
| `txns.kyc` | KYC events |
| `txns.userPlatformEvent` | Platform events |

### Group By (chain after type)

| Modifier | Groups by |
|---|---|
| `.all` | All transactions |
| `.byApplicant` | Same applicant |
| `.byIp` | Same IP address |
| `.byDevice` | Same device fingerprint |
| `.byRemitter` | Same remitter |
| `.byCounterparty` | Same counterparty |
| `.byBeneficiary` | Same beneficiary |

### Direction / Status Filters (chain after group by)

| Modifier | Effect |
|---|---|
| `.in` | Incoming only |
| `.out` | Outgoing only |
| `.sameDirection` | Same direction as current |
| `.sameCounterparty` | Same counterparty external ID |
| `.excludeCurrent` | Exclude the current transaction |
| `.rejected` | Only rejected transactions |
| `.approved` | Only approved transactions |

### Time Windows (chain after filters)

| Modifier | Description |
|---|---|
| `.allTime` | All time |
| `.lastHours(n)` | Last N hours |
| `.lastDays(n)` | Last N days |
| `.lastWeeks(n)` | Last N weeks |
| `.lastMonths(n)` | Last N months |
| `.currentCalendarMonth` | This calendar month |
| `.lastCalendarMonth` | Previous calendar month |

### Aggregate Operations (terminal)

| Operation | Description |
|---|---|
| `.count()` | Number of matching transactions |
| `.sum(it.data.info.amountInDefaultCurrency)` | Sum of amounts |
| `.distinctCount(it.data.applicant.externalUserId)` | Distinct count |

**Examples:**
```
# More than 5 outgoing transfers by same applicant in last 24h
txns.finance.byApplicant.out.lastHours(24).count() > 5

# Total outgoing amount in last 30 days
txns.finance.byApplicant.out.lastDays(30).sum(it.data.info.amountInDefaultCurrency) > 100000

# Number of distinct counterparties in last week
txns.finance.byApplicant.lastWeeks(1).distinctCount(it.data.counterparty.externalUserId) > 10
```

---

## `questionnaires` — Questionnaire Answers

Answers are nested **questionnaire id → section id → item id**:

```
questionnaires.myQuestionnaireId.mySectionId.myItemId
```

**Dot notation only.** The bracket form `questionnaires[qId][sectionId][itemId]` does **not** compile
here — never use it.

**A segment containing a dash must be wrapped in backticks**, otherwise the dash parses as
subtraction and the expression breaks:

```
questionnaires.`my-quest-id`.mySectionId.myItemId
```

Real ids frequently contain dashes, so check every one of the three segments before writing the
path — not just the questionnaire id.

**All three segments are required.** Item ids are not unique across the sections of one
questionnaire, so the section segment carries meaning and the path cannot be shortened.

**Any rule type can read `questionnaires`.** The `types` value selects which event triggers
evaluation, not which data is reachable — a `finance` rule and a `kyc` rule can both test the same
answer. Pick the type by the event that should fire the rule: a transaction, or a verification
session on the applicant.

### Finding the three ids

1. **List questionnaires** — `GET /resources/api/questionnaires/list`. Note the path: unlike the
   questionnaire write endpoints, this one is **not** under `/api/agent/`.
2. **Read one back** — `GET /resources/api/agent/questionnaires/{id}`.
3. **Walk the response** — `sections[].id` is the section segment, `sections[].items[].id` is the
   item segment. Prefer each entity's `title` when talking to the user, and the `id` in the path.

### Compare against the option value, not its label

`GET /resources/api/agent/questionnaires/{id}` returns each option as an object:

```json
"options": [{ "value": "a", "title": "Bank statements", "localizedTitle": { … }, "score": null }]
```

Compare against **`value`** — that is what an answer stores. `title` and `localizedTitle` are display
text for the applicant and never appear in an answer. So the condition for "source of funds is bank
statements" is `== 'a'`, **not** `== 'Bank statements'`.

Comparing against the title produces a rule that saves cleanly, sits in testMode looking healthy,
and never matches — there is no error to alert you. Item and section `title` are often empty in a
definition, which makes the option title the only human-readable string in sight and the mistake
easy to make.

Do not confuse an option's `score` with the rule's `score`: the former is questionnaire-native
scoring, a separate feature gated by the `QUESTIONNAIRE_SCORING` entitlement, and it does not feed
the rule's score.

Note: the two-element `[value, title]` form appears in this repo's questionnaire **input** examples —
`sumsub-create-questionnaire` expands it into the object above. It is not what a read returns.

---

## SumScript Operators

| Operator | Use |
|---|---|
| `AND` | Logical and (short-circuit) |
| `OR` | Logical or (short-circuit, stops at first true) |
| `EOR` | Eager OR — evaluates ALL branches (use for addScoreIf chains) |
| `NOT` | Logical not |
| `IN` | List membership: `"value" IN someList` |
| `==`, `!=` | Equality |
| `>`, `<`, `>=`, `<=` | Numeric comparison |
| `+`, `-`, `*`, `/` | Arithmetic |
| `addScoreIf(expr, score)` | Add score if expr is true; returns BOOL (side-effect function) |

String literals use single quotes: `'out'`, `'rejected'`.

### Functions

Signatures from the EL type schema. Selected subset — the ones that come up when translating a
client's wording into a condition.

| Function | Signature | Use |
|---|---|---|
| `fuzzyMatchValue` | `(str1: STRING, str2: STRING): FLOAT` | Normalised Levenshtein similarity — "names look alike" |
| `matches` | `(s: STRING, pattern: STRING): BOOL` | Regex match |
| `equalsIgnoreCase` | `(s: STRING, p: STRING): BOOL` | Case-insensitive equality |
| `startsWith` / `endsWith` | `(s: STRING, prefix\|suffix: STRING): BOOL` | Prefix / suffix test |
| `between` | `(value: FLOAT, min: FLOAT, max: FLOAT): BOOL` | Inclusive range |
| `isNotNull` | `(value: OBJECT): BOOL` | Presence test |
| `notNull` | `(value: V): V` | Assert non-null |
| `if` | `(expression: BOOL, v1: V, v2: V): V` | Inline conditional |
| `abs` | `(n: INT): INT` | Absolute value |
| `trim` | `(s: STRING): STRING` | Strip whitespace |
| `arrayFilter` | `(filter: (V) => BOOL, array: V[]): V[]` | Filter an array |
| `arrayCount` | `(filter: (V) => BOOL, array: V[]): INT` | Count matching elements |
| `hoursAgo` / `daysAgo` | `(value: INT): DATE` | Point in the past, for date comparisons |
| `diffHours` / `diffMinutes` | `(date1: DATE, date2: DATE): INT` | Elapsed time between dates |
| `toStartOfDay` | `(date: DATE): DATE` | Truncate to midnight |
| `greatCircleDistance` | `(lat1, lon1, lat2, lon2: FLOAT): FLOAT` | Distance between coordinates — geo anomalies |

Aggregate operations (`sum`, `min`, `max`, `avg`, `count`) are documented in the `txns` section as
terminal operations on a stream, not as standalone functions.

---

## `addScoreIf` Pattern

Use when different sub-conditions should contribute different scores. Set payload `score: 0` and
`action: "score"` to avoid double-counting.

**EOR (independent flags — all evaluated):**
```
addScoreIf(data.info.amountInDefaultCurrency > 100000, 50) EOR
addScoreIf(applicant.country IN clientLists.sanctioned_countries, 100) EOR
addScoreIf("pep" IN applicant.riskLabels.aml, 75)
```

**OR (mutually exclusive tiers — stops at first match, highest tier first):**
```
addScoreIf(data.info.amountInDefaultCurrency > 1000000, 100) OR
addScoreIf(data.info.amountInDefaultCurrency > 100000, 50) OR
addScoreIf(data.info.amountInDefaultCurrency > 10000, 20)
```

---

## Scheduled Rules (`noEventTrigger`)

Used when `types: ["scheduledEvent"]`. Defines which applicants the rule fires for.

### Structure

```json
{
  "noEventTrigger": {
    "type": "byLevelName",
    "levelParams": {
      "levelName": "basic-kyc-level",
      "days": 365
    },
    "activateAt": "2025-01-01T00:00:00.000Z"
  }
}
```

| Field | Type | Description |
|---|---|---|
| `type` | String | `byLevelName` or `byCustomExpression` |
| `levelParams.levelName` | String | Required for `byLevelName`. Applicant level to target. |
| `levelParams.days` | Integer | Required for `byLevelName`. Days after review date. |
| `customExpressionParams.applicantFilter` | String | Required for `byCustomExpression`. SumScript expression. |
| `activateAt` | Date | Only process applicants created after this date. |

### Required Applicant Action (at least one)

```json
{
  "applicantChange": {
    "type": "applicantLevel",
    "applicantLevel": {
      "levelName": "target-level-name",
      "resetDocSets": [{"idDocSetType": "SELFIE"}]
    }
  }
}
```

`applicantChange.type` options: `applicantLevel`, `finalRejection`, `manualReview`.

---

## Case Action (`caseAction`)

| Field | Type | Default | Description |
|---|---|---|---|
| `createCase` | Boolean | `false` | Enable case creation on rule match |
| `groupByType` | String | `byRule` | `byRule` (one case per rule) or `byApplicant` (one case per applicant) |
| `blueprintId` | String | — | Case blueprint id (optional; uses default template if omitted) |
| `priority` | String | — | `low`, `medium`, or `high` |
| `deadlineHours` | Integer | — | Investigation deadline in hours |

---

## Transaction Action (`txnActions`)

Set a custom property on the transaction when the rule matches:

```json
{
  "txnActions": [
    {
      "type": "setProp",
      "setPropertyActionParams": {
        "propName": "riskCategory",
        "elExpression": "'high'"
      }
    }
  ]
}
```

---

## Payload Constraints Summary (create mode)

| Must include | Must NOT include |
|---|---|
| `title` (non-empty, ≤128 chars) | `id`, `name`, `clientId` |
| `types` (min 1 value) | `scope`, `bgCheckTargets`, `dryRun`, `disabled` |
| `conditionEl` for non-scheduled eval rules | `actual`, `revision`, timestamps, author fields |
| `noEventTrigger` + applicant action for scheduled rules | Empty containers (`sourceKeys: []`, etc.) |

Modify mode differs: send `"id": null`, the existing `name`, and the current `dryRun` / `disabled` — see SKILL.md, section "Modifying an Existing Rule".
