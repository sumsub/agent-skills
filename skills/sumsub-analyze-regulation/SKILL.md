---
name: sumsub-analyze-regulation
description: Analyze a regulation document (PDF or text) and produce a Sumsub configuration plan — mapping regulatory requirements to Sumsub entities (levels, questionnaires, PoA presets, TM rules, workflows, AML resolution rules). TRIGGER when the user provides a regulation PDF, legal act, or compliance requirement document and wants to know what to configure in Sumsub. Acts as the entry point before invoking sumsub-create-level, sumsub-create-questionnaire, sumsub-create-poa-preset, sumsub-create-workflow, sumsub-create-aml-resolution-rules, and other skills. SKIP for direct entity creation requests (no regulatory context) or Sumsub API calls.
allowed-tools: Read
---

# Sumsub — Analyze Regulation

Reads a regulation document and produces a structured Sumsub configuration plan — mapping each regulatory requirement to the Sumsub entities that satisfy it, with a clear split between what can be configured **now via skills** and what requires the **Sumsub Dashboard**.

This is a **planning skill only**. It produces a text description, never JSON payloads or API calls.

## Workflow

### Step 1 — Gather context

Before analyzing, collect:
- **Jurisdiction** — if the document covers multiple countries or is ambiguous, ask explicitly:
  _"This regulation covers [list of countries]. Which jurisdiction should the plan focus on?"_
  Do not generate a plan for all jurisdictions simultaneously without a direct request to do so.
- **Business type** — crypto exchange, neobank, iGaming, fintech, or other. Ask if not clear from the document.
- **Client types** — individuals, companies, or both.
- **Existing Sumsub setup** — has the user already configured anything? Avoid suggesting duplicates.

### Step 2 — Analyze (think before responding)

Use extended thinking before formulating the response. Extract from the document:
- Customer identification requirements (who must be identified, what data is required)
- Acceptable identity documents (national ID, passport, tax number, etc.)
- Address verification requirements (what documents are accepted, maximum age)
- Enhanced Due Diligence conditions (what triggers EDD)
- Source of funds / wealth / PEP data collection requirements
- AML screening obligations (PEP / sanctions / adverse media) and how screening hits must be handled (false-positive clearing, PEP review policy, escalation of confirmed matches)
- Transaction monitoring requirements (thresholds, suspicious patterns, crypto Travel Rule)
- Periodic re-KYC obligations (how often customers must be re-verified)
- What is **out of scope for Sumsub** (data retention timelines, regulatory reporting, sanctions list maintenance)

### Step 3 — Validate understanding first

After analysis, present a short **"My Understanding"** block — bullet points of extracted requirements — and ask:
_"Have I understood the key requirements correctly? Anything to add or correct?"_

**Do not generate the full plan until the user confirms.** This is mandatory.

### Step 4 — Generate the plan

Only after user confirmation, produce the full configuration plan using the [output format](#output-format) below.

---

## Sumsub Capability Map

### A. Verification Levels — `sumsub-create-level`

Defines the sequence of verification steps an applicant must complete. Each step is a `docSet`.

**Available docSet types:**

| Type | Purpose |
|---|---|
| `IDENTITY` | Document verification: PASSPORT, ID_CARD, DRIVERS, RESIDENCE_PERMIT, VOTER_ID, etc. Can be restricted by issuing country. |
| `SELFIE` / `SELFIE2` | Biometrics and liveness. |
| `APPLICANT_DATA` | Personal data collection: full name, date of birth, address, nationality, tax number (TIN/CPF/CNPJ/etc.). |
| `PROOF_OF_RESIDENCE` / `PROOF_OF_RESIDENCE2` | Address document verification. References a PoA preset by `poaStepSettingsId`. |
| `PHONE_VERIFICATION` / `EMAIL_VERIFICATION` | Contact verification via OTP. |
| `QUESTIONNAIRE` / `QUESTIONNAIRE2–4` | Custom form. References a questionnaire definition by `questionnaireDefId`. |
| `E_KYC` | Non-document electronic verification against external databases. See [E-KYC section](#e-kyc-non-document-electronic-verification). |
| `DEVICE_CHECK` | Device intelligence and fingerprinting. Requires `DEVICE_INTELLIGENCE` license. |
| `COMPANY` | KYB: company info collection. |
| `COMPANY_DATA` | KYB: company data fields. |
| `COMPANY_DOCUMENTS` | KYB: corporate documents upload. |
| `COMPANY_BENEFICIARIES` | KYB: UBOs and representatives verification. |
| `ACCREDITED_INVESTOR` | Accredited investor qualification. |
| `E_SIGN` | Electronic signature capture. |
| `TR_RECIPIENT_INFORMATION` | Travel Rule recipient data collection. |

**Level properties:**
- `applicantType`: `individual` or `company`
- `requiredIdDocs`: the ordered list of docSets + optional `includedCountries` / `excludedCountries`
- `disableWatchlists`: set to `true` if tenant has `WATCHLISTS` entitlement but needs to disable AML Screening for a particular level
- `crossCheckPresetId`: cross-check preset for AML screening


#### IDENTITY — document type codes

Sumsub uses generic `IdDocType` values regardless of what the document is locally called. Map the regulation's document names to these types:

| Generic document class | Sumsub `IdDocType` |
|---|---|
| International / biometric passport | `PASSPORT` |
| National identity card (any country) | `ID_CARD` |
| Driver's licence | `DRIVERS` |
| Residence / immigration permit | `RESIDENCE_PERMIT` |
| Voter ID | `VOTER_ID` |
| Documents with no dedicated Sumsub type (e.g. tax cards, social security cards) | `OTHER_DOCS` |

`includedCountries` / `excludedCountries` use ISO-3166 alpha-3 (e.g. `BRA`, `USA`, `DEU`).

Two-sided capture should be specified whenever a mandatory identifier (tax number, national number) appears on the back of the document.

#### SELFIE — liveness options (`videoRequired`)

| Value | Description | Use when |
|---|---|---|
| `passiveLiveness` | **Default.** Advanced passive liveness, no movement required. | Standard KYC — no stricter regulatory mandate. |
| `activeLiveness` | Active motion challenge (head movement detection). | Regulation explicitly requires active/dynamic liveness. |
| `enabled` | Short video — applicant pronounces displayed digits. | Regulation requires video identity check. |
| `photoRequired` | Photo-only selfie, no liveness. | Use only when explicitly requested; generally insufficient for AML compliance. |
| `staticLiveness` | Single-frame analysis. | Use only when explicitly requested. |

For most AML/KYC regulations without a specific liveness requirement, default to `passiveLiveness`.

#### APPLICANT_DATA — common field names

Standard personal-data fields:

| Field name | Meaning |
|---|---|
| `firstName` | First / given name |
| `lastName` | Last / family name |
| `dob` | Date of birth |
| `country` | Country of residence (ISO-3166 alpha-3) |
| `town` | City / town |
| `street` | Street address |
| `postCode` | Postal / ZIP code |
| `nationality` | Nationality (ISO-3166 alpha-3) |
| `placeOfBirth` | Place of birth |
| `tin` | Tax identification number (TIN, CPF, SSN, BSN, etc.) |

When a regulation mandates collection of a national tax or identity number, map it to `tin` and mark it `required: true`.

#### DEVICE_CHECK — what it detects

When `DEVICE_INTELLIGENCE` license is active, this step flags: emulators, rooted/jailbroken devices, VPN/proxy/Tor connections, remote-desktop software, and crypto-mixer tools. Always note in the plan that this step silently falls back to disabled if the tenant lacks the entitlement — add a GET-back verification step.

### B. Questionnaires — `sumsub-create-questionnaire`

Custom forms for collecting applicant data not captured by document checks.

**Common use cases:** source of funds, source of wealth, employment, PEP self-declaration, trading experience, risk profile.

**Question types:** `text`, `textArea`, `date`, `dateTime`, `bool`, `select`, `selectDropdown`, `multiSelect`, `phone`, `countrySelect`, `countryMultiSelect`, `fileAttachment`, `multiFileAttachments`.

**Conditional logic:** sections and items can be shown/hidden based on previous answers.

**Risk scoring:** each answer option can carry a `score` (0–100); scores sum automatically and can be referenced in downstream transaction monitoring rules.

**One questionnaire per level.** Group distinct topics (source of funds, PEP self-declaration, risk profile…) as separate **sections within a single questionnaire** — not as separate questionnaires. Default to one `QUESTIONNAIRE` step per level. A *separate* level legitimately gets its own questionnaire (e.g. an EDD level with an extended questionnaire) — that is still one-per-level, not an exception. Only plan multiple questionnaires on the *same* level if the user explicitly asks for it.

### C. Proof of Address Presets — `sumsub-create-poa-preset`

Reusable configuration for what documents are accepted as proof of address.

**Document categories:**
- `governmentOrganization` — government-issued (voter registration, tax bill, etc.)
- `utilityProvider` — utility bills
- `bank` — bank statements and letters
- `mobileOperator` — telecom bills
- `other`

**Key settings:**
- `maxMonths` per category — maximum document age
- **Cross-validation:** name/address comparison between identity document (POI) and address document (POA) — fuzzy or strict mode
- **PoI-as-PoA:** accept the identity document itself as proof of address
- **Neobank blocklist:** exclude documents from specific institutions (Revolut, N26, Wise, etc.)
- **Country-specific overrides:** different rules per country

### D. E-KYC (Non-Document Electronic Verification)

**⚠️ Requires separate activation per country through a Sumsub Customer Success Manager (CSM). License: `E_KYC_TARGET`.**

Configured via `sumsub-create-level` once activated.

**How it works:** the applicant submits unique identifiers (TIN, document number, bank login) which are validated against external databases — no document photo required.

**Two configuration modes:**
1. **Standalone `E_KYC` docSet** — electronic verification only; applicant cannot upload documents instead
2. **`IDENTITY` with `ekycAllowed: true`** — applicant chooses: upload document photo OR complete E-KYC

**Available database types:** `GOVERNMENT` (national registries), `CREDIT` (credit bureaus), `TELCO` (telecom providers), `BANKING`, `COMMERCIAL` (business registries), `CONSUMER`, `UTILITY`, `POSTAL`, `PROPRIETARY`.

**Verification methods:** `ENRICHMENT`, `ONE_X_ONE_MATCHING`, `TWO_X_TWO_MATCHING`, `VALIDITY_CHECK`.

**Configuration rules:**
- Country coverage depends entirely on client's license activations — there is no universal list
- Recommended to pair with a `SELFIE` step for biometric verification against database records

**Activation steps:** (1) contact CSM to request per-country activation, (2) run `sumsub-create-level`.

### E. Transaction Monitoring — `sumsub-create-kyt-rules`

**⚠️ Requires `KYT` license** (and `TRAVEL_RULE` for crypto, `TM_SCHEDULED_EVENTS` for periodic re-KYC, `KYT_ANTI_FRAUD` for platform events).

Describes what to configure at plan time in plain language. `sumsub-create-kyt-rules` translates each rule into a `conditionEl` SumScript expression and POSTs it to the API. New rules always start in test mode (`dryRun: true`) — activating them requires the dashboard.

**Transaction types:**
- `finance` — financial transactions (fiat and crypto)
- `travelRule` — crypto transactions subject to Travel Rule (FATF / VASP)
- `kyc` — KYC-related events
- `userPlatformEvent` — login, signup, password reset, 2FA changes
- `scheduledEvent` — periodic triggers (requires `TM_SCHEDULED_EVENTS` license)

**Rule anatomy:**
- **Condition** — trigger (e.g., "incoming crypto transaction > $10,000")
- **Action:** `score` (add risk points), `onHold` (freeze transaction), `awaitUser` (request confirmation), `reject` (block)
- **Risk score** (0–100) — cumulative; multiple rules sum their scores
- **Applicant change** — move applicant to another level, trigger final rejection, or route to manual review
- **Case creation** — auto-create a compliance investigation case on rule match

**Automated pre-scoring enrichments** (active for licensed tenants):
- AML watchlists (PEP, sanctions, adverse media)
- Crypto screening: Chainalysis, Elliptic, TRM Labs, Merkle Science, Crystal
- Travel Rule processing
- Device intelligence and fingerprinting
- BIN lookup and payment method analytics

**Periodic Re-KYC (Scheduled Rules):**
- Trigger: applicants on level X for N days → reassign to a new level (triggers re-verification)
- Requires `TM_SCHEDULED_EVENTS` license

**Required licenses for TM features:** `KYT`, `TRAVEL_RULE`, `TM_SCHEDULED_EVENTS`, `KYT_ANTI_FRAUD`, `DEVICE_INTELLIGENCE`.

### F. Workflows — `sumsub-create-workflow`

Graph-based routing logic: determines which level an applicant goes through next based on conditions.

**Node types:** `applicantLevel` (run a level), `exclusiveChoice` (condition branch), `manualReview`, `finalRejection`, `actions` (tags, notes, source-key changes).

**Edge conditions:** by applicant country, number of attempts, review decision (approved / rejected / resubmission), custom expressions.

Use when regulation requires risk-based routing (standard KYC for low-risk, EDD for high-risk), re-verification flows, or multi-stage onboarding.

### G. AML Resolution Rules — `sumsub-create-aml-resolution-rules`

The **AML Resolution Rule Chain**: an ordered list of rules that auto-review AML screening hits. Each rule selects hits by condition (vendor match types, name/DoB compatibility, risk labels, previous reviews) and sets the hit's review — match status (`false_positive` / `potential_match` / `true_positive`), risk level, whitelisted flag, note — and/or tags the applicant.

Use when the regulation permits or requires systematic hit disposition: auto-clearing false positives, carrying over prior review decisions, PEP out-of-office handling, or flagging nuanced cases for routing.

**Relationship to other entities:** the screening runs on an applicant level when the tenant has `WATCHLISTS` entitlement and the level doesn't set `disableWatchlists: true`; the rule chain governs what happens to the AML matches it produces. Rule tags are common applicant tags and surface in workflow conditions as `checks.personWatchlist.tags` / `checks.companyWatchlist.tags` — e.g. a rule tags `youngPep`, a workflow routes those applicants to manual review.

Requires an AI-purpose App Token and tenant enablement (the skill detects and reports if the API is unavailable).

### H. Transaction Submission — `sumsub-create-transaction`

Sends transaction data to Sumsub's KYT monitoring system. Distinct from TM Rules:
- This skill handles **data submission** (what transaction data to send)
- TM Rules define **what to do** with that data (configured in the Dashboard)

Covers: finance transactions, Travel Rule (crypto counterparty data), platform events (login/signup).

---

## Analysis Framework

| Regulation requirement | Sumsub entity | Skill / action |
|---|---|---|
| Identify the customer (name, DOB, nationality) | `APPLICANT_DATA` + `IDENTITY` | `sumsub-create-level` |
| Document verification (passport, national ID) | `IDENTITY` (types, issuing countries) | `sumsub-create-level` |
| Biometrics / liveness check | `SELFIE` (passiveLiveness / activeLiveness) | `sumsub-create-level` |
| Address verification | `PROOF_OF_RESIDENCE` + PoA preset | `sumsub-create-level` + `sumsub-create-poa-preset` |
| Tax number collection (TIN, CPF, CNPJ, SSN…) | `APPLICANT_DATA` (fields) or E-KYC | `sumsub-create-level` |
| Source of funds / source of wealth | `QUESTIONNAIRE` (SOF/SOW section) | `sumsub-create-questionnaire` |
| PEP self-declaration | `QUESTIONNAIRE` + AML `watchListCheckSettings` | `sumsub-create-questionnaire` + `sumsub-create-level` |
| Enhanced Due Diligence (EDD) | Separate EDD level + extended questionnaire | `sumsub-create-level` + `sumsub-create-questionnaire` |
| PoA document age limit | PoA preset `maxMonths` per category | `sumsub-create-poa-preset` |
| Electronic / non-document verification | `E_KYC` docSet | `sumsub-create-level` *(CSM activation required)* |
| KYB — company verification | `COMPANY` / `COMPANY_DATA` / `COMPANY_BENEFICIARIES` | `sumsub-create-level` |
| Risk-based routing (standard vs EDD) | Workflow with `exclusiveChoice` | `sumsub-create-workflow` |
| Auto-review of AML screening hits (false-positive clearing, PEP rules) | AML Resolution Rule Chain | `sumsub-create-aml-resolution-rules` |
| Screening-driven routing (e.g. flagged PEP → manual review) | AML rule tag + workflow condition on `checks.personWatchlist.tags` | `sumsub-create-aml-resolution-rules` + `sumsub-create-workflow` |
| Transaction monitoring (thresholds, patterns) | KYT rules | `sumsub-create-kyt-rules` *(requires `KYT` license)* |
| Crypto Travel Rule | `travelRule` transaction type + KYT rules | `sumsub-create-kyt-rules` *(requires `TRAVEL_RULE` license)* |
| Periodic re-KYC obligation | TM Scheduled rule `byLevelName` | `sumsub-create-kyt-rules` *(requires `TM_SCHEDULED_EVENTS` license)* |
| Compliance case management | TM rule `caseAction` | `sumsub-create-kyt-rules` |
| Transaction data submission | KYT submission | `sumsub-create-transaction` |
| Device check / fraud prevention | `DEVICE_CHECK` docSet | `sumsub-create-level` *(requires DEVICE_INTELLIGENCE license)* |
| WebSDK / front-end onboarding flow | WebSDK integration | `sumsub-integrate-websdk` |

---

## Output Format

Produce the plan as a structured markdown document with two clearly separated sections.

**Critical:** use actual Sumsub enum values and field names throughout — not prose descriptions. Every step must show the concrete parameters that will go into the API call.

```
# Sumsub Configuration Plan: [Regulation Name] — [Jurisdiction]

## My Understanding
- [Bullet: key requirement 1 from regulation]
- [Bullet: key requirement 2]
- …
[Ask for confirmation here before generating the rest]

---

## ✅ Configure via Skills (available now)

### 1. Verification Level(s)
#### Level: [name] — [purpose, e.g. "standard KYC"]
- `applicantType`: individual | company
- Steps (in order):
  1. `APPLICANT_DATA`
     - `fields`: `[firstName, lastName, dob, country, town, street, postCode]`
     - Tax identifier: `tin` — `required: true` _(Art. N — CPF mandatory for identification)_
  2. `IDENTITY`
     - `docTypes`: `[PASSPORT, ID_CARD, DRIVERS]`
     - `includedCountries`: `[BRA]` _(ISO-3166 alpha-3, or omit for all countries)_
     - Two-sided capture: yes — `ID_CARD` and `DRIVERS` carry CPF on the reverse _(Art. N)_
     - Regulation reference: Art. N
  3. `SELFIE`
     - `videoRequired`: `passiveLiveness` _(default; change to `activeLiveness` if regulation requires motion challenge)_
     - Regulation reference: Art. N
  4. `QUESTIONNAIRE` — `questionnaireDefId`: `[questionnaire-slug]` _(defined in section 2 below)_
  5. `PROOF_OF_RESIDENCE` — `poaPresetId`: `[preset-id]` _(defined in section 3 below)_
  6. `DEVICE_CHECK` — ⚠️ requires `DEVICE_INTELLIGENCE` license _(Art. N — emulators, VPN/Tor, rooted devices)_
- AML watchlist screening: requires the **`WATCHLISTS` tenant entitlement**; when present it is **on by default** — nothing to set _(Art. N — PEP/sanctions screening mandatory)_. If the tenant lacks `WATCHLISTS`, flag it as a blocking entitlement (CSM must enable it). Only note `disableWatchlists: false` if you want to be explicit; pick a provider with `watchListCheckSettings.amlCaseType` only if the regulation/tenant demands a specific one (tenant-gated).
- Countries in scope: `includedCountries: [XXX]` | all countries
→ Next: `sumsub-create-level`

#### Level: [name] — [e.g. "enhanced due diligence"]
- (same structure — add extra steps or stricter liveness as required)
→ Next: `sumsub-create-level`

### 2. Questionnaire(s)
#### Questionnaire: `[id-slug]` — [purpose, e.g. "Risk Profile & Compliance"]
- Sections:
  - `[section-id]` — [Section name, e.g. "Virtual Asset Experience"]
    - `[item-id]`: "[Question text]" — `type: select` — `required: true`
      Options: `[["novice","No experience"],["intermediate","Some experience"],["expert","Expert"]]`
    - `[item-id]`: "[Question text, e.g. risk acknowledgement]" — `type: bool` — `required: true`
      _(Art. N — client must confirm trades outside risk profile)_
  - `[section-id]` — [Section name, e.g. "Source of Funds"]
    - `[item-id]`: "[Question text]" — `type: select` — `required: true`
      Options: `[["employment","Employment/Salary"],["business","Business income"],["savings","Savings"],["investment","Investment returns"],["other","Other"]]`
    - `[item-id]`: "Specify other source" — `type: text` — condition: `[section-id].[item-id] = other`
→ Next: `sumsub-create-questionnaire`

### 3. Proof of Address Preset
- Accepted categories and max document age:
  - `governmentOrganization` — [N] months _(Art. N)_
  - `bank` — [N] months
  - `utilityProvider` — [N] months
  - `mobileOperator` — [N] months
- Cross-validation: enabled | disabled — _(name/address match between POI and POA)_
- POI-as-POA: yes | no
- Country overrides: [ISO-3 code — category/maxMonths changes, if any]
→ Next: `sumsub-create-poa-preset`

### 4. Workflow
- [Description of routing: standard KYC → if high-risk → EDD → manual review]
- Conditions: [by country / by questionnaire score / etc.]
→ Next: `sumsub-create-workflow`

### 5. AML Resolution Rules (AML Resolution Rule Chain)
[Include only if the regulation addresses AML hit handling]
- Rule: [name] — [plain language: which hits → what review/tag]
  e.g. "Hits whose name and date of birth both mismatch the applicant → false positive"
  e.g. "PEP hits under age 30 → tag `youngPep`" _(routed by the workflow in section 4)_
- Rule order: [decisive rules first, broad clean-up rules last]
- Regulation reference: Art. N
→ Next: `sumsub-create-aml-resolution-rules`

### 6. Transaction Data Submission (KYT)
- Transaction types to instrument: `finance` | `travelRule` | `userPlatformEvent`
- Required fields per transaction: [counterparty name, wallet address, etc.] — _(Art. N)_
→ Next: `sumsub-create-transaction`

### 6. Transaction Monitoring Rules
[Only include if regulation requires transaction monitoring. Requires `KYT` license.]

#### Rule: [name]
- `types`: `finance` | `travelRule` | `kyc` | `userPlatformEvent` | `scheduledEvent`
- Trigger: [plain language, e.g. "incoming transaction above $10,000"]
- `action`: `score [N]` | `onHold` | `awaitUser` | `reject`
- Case creation: yes | no — [group by applicant / by rule]
- Regulation reference: Art. N
→ Next: `sumsub-create-kyt-rules`

#### Periodic Re-KYC rule [if applicable — requires `TM_SCHEDULED_EVENTS` license]
- Trigger: customers at level [X] after [N] days
- Action: reassign to level [Y] for re-verification
- Regulation reference: Art. N
→ Next: `sumsub-create-kyt-rules`

---

## ⚠️ Configure in Sumsub Dashboard

### Activate TM rules
New rules are created in test mode (`dryRun: true`). To make them live: open each rule in the dashboard (KYT → Rules Manager) and set it to **Active**.

### KYT Client Lists
Adding values to client lists referenced in rule conditions (e.g., country blocklists, peer allowlists) is a dashboard-only operation: KYT → Client Lists.

---

## 🔒 E-KYC (electronic non-document verification)
[Include only if applicable to the jurisdiction]

- Jurisdiction: [country]
- Potentially available databases: GOVERNMENT | CREDIT | BANKING
- Configuration path: `sumsub-create-level` — after CSM activation
- Activation steps:
  1. Contact your Sumsub CSM to request activation for [country]
  2. Run `sumsub-create-level` with the `E_KYC` docSet

---

## Out of Scope for Sumsub
[List requirements from the regulation that Sumsub does not handle]
- [e.g. 5-year data retention — handle in your own infrastructure]
- [e.g. Reporting to [authority] — handle via your compliance team]

---

## Suggested Execution Order
1. `sumsub-create-questionnaire` (needed before level creation)
2. `sumsub-create-poa-preset` (needed before level creation)
3. `sumsub-create-level` (standard KYC level)
4. `sumsub-create-level` (EDD level, if needed)
5. `sumsub-create-workflow` (if risk-based routing needed)
6. `sumsub-create-aml-resolution-rules` (if AML hit auto-review needed; before the workflow when it routes on rule tags — the tag must exist first)
7. `sumsub-create-kyt-rules` (TM rules, if regulation requires transaction monitoring)
8. `sumsub-create-transaction` (instrument transaction submission)
9. Dashboard — activate TM rules (move from test mode to live)
```

---

## Rules

1. **Language:** respond in the same language as the user's request.
2. **Think first:** use extended thinking before formulating the response — regulation texts are dense and requirements are often implicit.
3. **One jurisdiction at a time:** if the document covers multiple jurisdictions, ask which one to plan for before proceeding. Do not produce multi-jurisdiction plans unprompted.
4. **Validate before generating:** after analysis, present the "My Understanding" summary and wait for user confirmation before producing the full plan.
5. **No JSON:** this skill produces text descriptions only. Never generate API payloads, JSON objects, or configuration code.
6. **Be concrete:** the plan must use actual Sumsub parameter names and enum values, not prose descriptions. Write `docTypes: [PASSPORT, ID_CARD, DRIVERS]`, not "Passport and national ID". Write `videoRequired: passiveLiveness`, not "advanced liveness". Write `fields: [firstName, lastName, dob, tin]`, not "name and tax number". Include country codes in ISO-3166 alpha-3 (`BRA`, not "Brazil"). Name questionnaire item types (`bool`, `select`, `text`). Use the country-specific document mapping table in the Capability Map to translate local document names to IdDocType codes.
7. **Mark the boundary clearly:** every item in the plan must be in either ✅ (skills available now) or ⚠️ (Dashboard / skill in development). Never leave the boundary ambiguous.
8. **E-KYC is always opt-in:** always mark E-KYC as requiring CSM activation. List the activation steps. Do not present it as a default option.
9. **TM and AML resolution rules in plain language only:** describe trigger conditions and actions in business language (e.g., "block transactions over $50,000", "hits with mismatching name and date of birth → false positive"). Do not write SumScript expressions, condition ASTs, or technical rule syntax — `sumsub-create-kyt-rules` and `sumsub-create-aml-resolution-rules` handle that translation.
10. **No TM rules without explicit requirement:** only include TM rules in the plan if the regulation explicitly requires transaction monitoring.
11. **Licenses:** flag `DEVICE_INTELLIGENCE`, `E_KYC_TARGET`, `KYT`, `TRAVEL_RULE`, `TM_SCHEDULED_EVENTS` as requiring license verification.
12. **Out of scope:** explicitly list requirements the regulation contains that Sumsub cannot fulfill (data retention, authority reporting, etc.).

---

## Related Skills

| Skill | When to invoke |
|---|---|
| `sumsub-create-level` | Always — core output of every regulation analysis |
| `sumsub-create-questionnaire` | Regulation requires SOF, PEP, wealth, employment, or risk profile collection |
| `sumsub-create-poa-preset` | Regulation requires address verification |
| `sumsub-create-workflow` | Regulation requires risk-based routing, EDD flow, or multi-stage onboarding |
| `sumsub-create-aml-resolution-rules` | Regulation addresses AML hit handling — false-positive clearing, PEP review policy, or screening-driven escalation |
| `sumsub-create-kyt-rules` | Regulation requires transaction monitoring rules (thresholds, suspicious patterns, periodic re-KYC, Travel Rule) |
| `sumsub-create-transaction` | Regulation requires transaction monitoring data submission |
| `sumsub-integrate-websdk` | Regulation has UX or front-end onboarding requirements |
| `sumsub-api-generic` | Check existing configuration before creating new entities |
