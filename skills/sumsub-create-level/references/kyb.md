# KYB (company) levels — reference

What `build_level.py` builds for `applicantType: company`, the rules it enforces, and what it
rejects in this first KYB iteration. All shapes are the WebSDK 2.0 KYB structure — the one the
dashboard creates today.

## Level shape

| Part | Value |
|---|---|
| `applicantType` | `company` |
| `type` | `standalone` (the only type the skill builds for companies) |
| `websdkNext` | `true` (builder default on create; the API sets it on every new level). The builder rejects `websdkNext: false` on a company level, and `--base` refuses a WebSDK 1.0 company level. |
| KYB steps | `COMPANY_DATA` (required, the first step of a new level), `COMPANY_DOCUMENTS`, `COMPANY_BENEFICIARIES` |
| Other allowed steps | `EMAIL_VERIFICATION`, `PHONE_VERIFICATION`, `PAYMENT_METHODS` (same entitlement as on a KYC level), `QUESTIONNAIRE` / `2` / `3` / `4` |
| `kybType` (compact key) | Written to `autoCheckGeneratorSettings.kybType`. **Required on create.** |
| `kybSettings` (compact key) | Written to `requiredIdDocs.kybSettings`. Defaults to 25 / 25 on create — both at `uboThreshold` when only that is set lower. |
| `name` | Never `company-zero` — Sumsub's reserved default company level. The builder refuses to create or update it. |

A tenant may already have Sumsub's default levels — for example `id-and-liveness` (KYC),
`basic-kyb-level` and `company-data-only` (KYB). Offer to reuse them before creating look-alikes.

## `kybType` — KYB check mode

| Value | Dashboard label | What Sumsub does | Entitlement (any of) |
|---|---|---|---|
| `autoAndManual` | Full KYB | Registry check, AML screening, manual review of the company and its documents | `KYB_FULL`, `COMPANY` |
| `auto` | Registry and AML Check | Registry check and AML screening; declines on missing registry data or AML matches | `KYB_FULL`, `KYB_AUTO_AML_AND_REGISTRY`, `COMPANY` |
| `amlOnly` | AML Check | AML screening only; declines on AML matches | `KYB_FULL`, `KYB_AUTO_AML_AND_REGISTRY`, `KYB_AUTO_AML_ONLY`, `COMPANY`, `KYB_APPLICANTS` (data collection only — see below) |

- Pick a mode the tenant is entitled to: company applicants can't be created on a level whose
  mode the tenant doesn't have (403 "This type of KYB checks is not enabled"). Pick the mode the
  user asked for, and only if an entitlement from its row is in `allowedChecks`. If the user
  didn't say, pick the most thorough mode the tenant has and say which one.
- Always set `kybType` — the builder requires it on create.
- A tenant with only `KYB_APPLICANTS` has no check mode. It can collect company data only: use
  `kybType: amlOnly` together with the level-wide `disableWatchlists: true`.
- With `auto` or `amlOnly`, `COMPANY_DOCUMENTS` are collected but **not verified** — the dashboard
  warns about this. Tell the user.
- With `amlOnly` the builder sets `kybSettings.disableCompanySearchAndPrefill: true` (the dashboard
  forces company search off in this mode) and rejects an explicit `false`. When an update turns
  company search off this way, the builder prints a `note:`.
- In sandbox, checks are simulated — a sandbox applicant tells you nothing about real registry /
  AML results. Full KYB (`autoAndManual`) runs no automated checks there: the applicant stays
  `pending` until a decision is set in the dashboard.

## `kybSettings`

| Key | Rule |
|---|---|
| `uboThreshold` | 0–100. Ownership share (%) from which a person counts as a UBO in the SDK. Default 25. |
| `shareholderThreshold` | 0–100, must be `<= uboThreshold`. Default 25, or `uboThreshold` when that is lower. On update, changing one threshold past the level's other one is rejected — set both. |
| `disableCompanySearchAndPrefill` | Optional boolean — turns off the registry company search and prefill in the SDK. |
| `enableBeneficiariesAutoCheck` | Optional boolean — cross-checks the associated parties against the corporate registry. Rejected in the spec with `amlOnly`, which runs no registry check; if an `amlOnly` level already has it on, the builder prints a `note:`. |

Primary-contact settings (`primaryContactRequired`, `primaryContactLevelName`) are not supported
yet — the builder rejects them in the spec. An update keeps the level's current values.

## `COMPANY_DATA` — company information

```json
{"type": "COMPANY_DATA", "fields": ["country", "companyName", "registrationNumber", "incorporatedOn"]}
```

- The first step of a new company level, as in the dashboard. An update keeps the level's current
  order, and keeps `COMPANY_DATA` if the level has it.
- `fields`: strings or `{name, required, prefill, immutableIfPresent}` — no other keys (a string
  means `required: true`). Default: `country`, `companyName`, `registrationNumber` — all required and prefilled.
- Allowed names (the dashboard's list): `companyName`, `country`, `registrationNumber`,
  `registrationLocation`, `type`, `legalForm`, `incorporatedOn`, `alternativeNames`,
  `legalAddress`, `postalAddress`, `controlScheme`, `email`, `phone`, `taxId`, `leiCode`,
  `website`, `street`, `subStreet`, `buildingNumber`, `flatNumber`, `town`, `postCode`, `state`.
- `country` and `companyName` are always required and prefilled. The builder adds them when
  missing and rejects `required: false` / `prefill: false` on them.
- `customFields`: `[{name, displayName, required, immutableIfPresent}]` — no other keys; names must
  not repeat `fields`.
- The server gates this step: the tenant needs one of `COMPANY`, `KYB_FULL`,
  `KYB_AUTO_AML_AND_REGISTRY`, `KYB_AUTO_AML_ONLY`, `KYB_APPLICANTS`.

## `COMPANY_DOCUMENTS` — corporate documents

```json
{"type": "COMPANY_DOCUMENTS", "companyDocsGroupDefinitions": [
  {"label": "legalPresence"},
  {"label": "ownershipStructure", "subTypes": ["SHAREHOLDER_REGISTRY"], "required": false}
]}
```

- Each group: `label`, `subTypes` (default: every subtype of the group; `OTHER` for `other1` /
  `other2` / `other3`), `required` (default `true` — the applicant must upload at least one
  document of the group).
- Default when `companyDocsGroupDefinitions` is omitted: one `legalPresence` group, required.
- There is no per-group minimum document count.

| `label` | Allowed `subTypes` |
|---|---|
| `legalPresence` | `INCORPORATION_CERT`, `INCORPORATION_ARTICLES`, `STATE_REGISTRY`, `PARTNERSHIP_AGREEMENT`, `TRUST_AGREEMENT`, `TRADE_LICENSE` |
| `companyDetails` | `INFORMATION_STATEMENT`, `PROOF_OF_ADDRESS`, `STATE_REGISTRY`, `INCORPORATION_ARTICLES`, `INCORPORATION_CERT`, `INCUMBENCY_CERT`, `GOOD_STANDING_CERT`, `PARTNERSHIP_AGREEMENT`, `TRUST_AGREEMENT`, `OWNERSHIP_STRUCTURE_CHART`, `TRADE_LICENSE` |
| `ownershipStructure` | `SHAREHOLDER_REGISTRY`, `INFORMATION_STATEMENT`, `TRUST_AGREEMENT`, `INCUMBENCY_CERT`, `STATE_REGISTRY`, `PARTNERSHIP_AGREEMENT`, `INCORPORATION_ARTICLES`, `OWNERSHIP_STRUCTURE_CHART` |
| `controlStructure` | `DIRECTORS_REGISTRY`, `TRUST_AGREEMENT`, `INCORPORATION_ARTICLES`, `INCUMBENCY_CERT`, `INFORMATION_STATEMENT`, `STATE_REGISTRY`, `PARTNERSHIP_AGREEMENT` |
| `representativesAuthorization` | `POWER_OF_ATTORNEY`, `DIRECTORS_REGISTRY`, `STATE_REGISTRY`, `INCORPORATION_CERT`, `INCUMBENCY_CERT`, `PARTNERSHIP_AGREEMENT` |
| `other1` / `other2` / `other3` | `OTHER`, plus any subtype of the groups above |

`REGULATORY_LICENSE`, `TAX_CERT`, `PROOF_OF_NATURE_OF_BUSINESS` and `SELF_DECLARATION_FORM` are not
supported by this skill yet. An update keeps a step that has them with `keep: true`.

## `COMPANY_BENEFICIARIES` — associated parties

```json
{"type": "COMPANY_BENEFICIARIES", "companyBeneficiaryDefinitions": [
  {"category": "ubos", "individual": {"levelName": "Basic KYC"}},
  {"category": "shareholders", "canSkip": true, "individual": {}, "company": {}}
]}
```

- `category`: one of the 24 public roles below. Each role at most once.
- `minRequired` / `maxAllowed`: how many parties of the role the applicant must / may add — whole
  numbers 1–100, default 1 / 100, `minRequired` <= `maxAllowed`. Set them, and `canSkip`, only
  when the user asks — leave them out otherwise, even to spell out a default.
- `canSkip: true` lets the applicant skip the role (declare it has none); `minRequired` then
  doesn't apply. With `canSkip` on both `ubos` and `shareholders`, the WebSDK lets the applicant
  skip only one of them — at least one owner must be declared. The builder prints a `note:`.
- A role has an `individual` and/or a `company` party, each
  `{enabled (default true), levelName, fields, customFields}`. At least one must be enabled.
  Spell out only the parties the user asked for: the builder adds the other kinds the role takes
  switched off (`enabled: false`, default fields), as the dashboard does — the dashboard can't
  save a role without its `individual` party, even on a company-only role.
  - `levelName` set → every party of that kind is verified with that level. It must name an
    **existing standalone level of the matching applicant type** (individual level for
    `individual`, company level for `company`) — the server answers 409 otherwise.
  - `levelName` omitted → the SDK only collects the party's data (no verification).
  - `fields` default to the dashboard's: individual — `firstName`, `lastName` (required),
    `middleName`, `dob` (optional), `email`, `phone` (required); company — `country`,
    `companyName`, `registrationNumber` (required). Ownership roles also get a required `shareSize`.
  - An individual party needs at least one of `firstName` / `lastName` / `email` as a required field.
  - A company party always keeps `country` and `companyName` required.

Which parties each role takes — the dashboard's matrix:

| Roles | Parties | Notes |
|---|---|---|
| `ubos` | individual | Ownership role. Company UBOs are not supported by this skill yet. |
| `shareholders` | individual, company | Ownership role. |
| `investors` | individual, company | Ownership role. **Internal use only — not verified by Sumsub.** |
| `representatives` | individual | Company representatives are not supported by this skill yet. |
| `companyOfficers` | individual | **Internal use only — not verified by Sumsub.** |
| `authorizedSignatories` | individual | |
| `directors`, `secretaries`, `founders`, `legalAdvisors` | individual, company | |
| `trustees`, `trustBeneficiaries`, `trustSettlors`, `trustProtectors` | individual, company | Trust roles. |
| `managingPartners`, `equityPartners` | individual, company | Partnership roles. |
| `fundInvestors`, `fundManagers`, `investmentManagers`, `investmentAdvisers`, `fundAdministrators` | individual, company | Fund roles. |
| `depositaries`, `custodians`, `primeBrokers` | company only | Fund roles. |

- A party kind a role doesn't take is rejected when enabled; a disabled one (`enabled: false`)
  passes through as it is.
- The dashboard groups roles by structure type — company (`ubos`, `shareholders`, `directors`,
  `companyOfficers`, `secretaries`, `investors`), trust, partnership and fund — and warns when one
  step mixes types (a fund has no directors). The builder prints a `note:`: tell the user and
  offer the roles of one structure type (for a fund, `fundManagers` instead of `directors`).
- For `companyOfficers` and `investors`, tell the user these parties are for internal use only —
  Sumsub does not verify them. The builder prints a `note:` line for them.
- `accountUsers` is not supported by this skill.
- Allowed individual field names: `firstName`, `lastName`, `middleName`, `email`, `phone`,
  `countryOfBirth`, `stateOfBirth`, `dob`, `placeOfBirth`, `legalName`, `gender`, `nationality`,
  `taxResidenceCountry`, `tin`, plus address fields (`country`,
  `street`, `subStreet`, `buildingNumber`, `flatNumber`, `town`, `state`, `postCode`).
- Allowed company field names: the `COMPANY_DATA` company fields (`companyName`, `country`,
  `registrationNumber`, … `leiCode`) and the same address fields.
- `shareSize` and `natureOfControl` are allowed on the ownership roles only (`ubos`,
  `shareholders`, `investors`).

## Verification levels for parties

A party's `levelName` points at a separate level, so a KYB level usually depends on a KYC level:

1. List existing levels and pick a standalone `individual` level for individual parties (and a
   `company` level for company parties) by name.
2. If none fits, create it first with this skill (for example `IDENTITY` + `SELFIE`), then
   reference its `name`.
3. Never invent a level name; if the user didn't say whether a role must be verified, ask.
4. Build with `--levels <level list>` (`list_levels.sh` prints it): the builder refuses a
   `levelName` that names no level, a level of the other applicant type, or a non-standalone
   level. `post_level.sh` and `patch_level.sh` repeat the check against a fresh list.

If the party's level has an `APPLICANT_DATA` step, check that it includes every field the role
marks as required, and tell the user about any that are missing.

## Updating a KYB level (`--base`)

PATCH changes only the top-level fields in the body, but a nested object it gets replaces the
stored one whole. A KYB update always sends `requiredIdDocs` — its `docSets` and `kybSettings`
(thresholds, primary contact) — and, with a new `kybType`, `autoCheckGeneratorSettings`
(regulation questions). Built from the spec alone, they would drop every step and setting the spec
doesn't carry, `COMPANY_ADDRESSES` included. So a KYB update starts from the current level:

```bash
get_level.sh <id> > get.out                                  # last line must be HTTP 200
build_level.py --base get.out < spec.json > payload.json
```

The output is the GET body with:

- `requiredIdDocs.docSets` built from the spec, in the spec's order. `{"type": T, "keep": true}`
  copies the current `T` step as it is — use it for every step you don't change, and for steps
  the builder can't build (`COMPANY_ADDRESSES`, unsupported document subtypes). A step you change is
  spelled out in full. A step you leave out is deleted; the builder prints a `note:` naming it.
- `kybSettings` and `autoCheckGeneratorSettings`: the current keys, with the spec's keys on top.
- The level-wide pass-through keys in the spec (`disableWatchlists`, `watchListCheckSettings`, …)
  overwrite; every other field comes from the GET, `id` included — except the server-populated
  ones (`key`, `clientId`, audit fields), which are never sent.

`--base get.out` and the GET body put into the spec as `base` (SKILL.md, step 6) build the same
payload and go through the same checks. The spec needs only `id` plus whatever the user asked to
change; leave `docSets` out to keep every step as it is. The builder rejects a company spec with
an `id` but no base, an `id` that isn't the base level, and a rename — the API keeps a level's
name.

The builder refuses:

- a copy of another account's level (`copyOf`) — it is read-only; change the source level instead;
- a WebSDK 1.0 company level (`websdkNext` not `true`) — any change to it, not only to its KYB
  steps; edit it in the Sumsub dashboard.

The API may refuse to edit a level that many applicants used recently (409) — edit that level
in the dashboard.

## Sending a company level

Send the builder's output unchanged. `post_level.sh` and `patch_level.sh` run
`build_level.py --check` on every company-level payload (a PATCH against the level they read
first) and refuse — exit 4, nothing sent — a payload the builder wouldn't produce: one written or
edited by hand, a setup the builder rejected, a WebSDK 1.0 level, or a party `levelName` that
doesn't resolve. A builder error is final: tell the user what it rejected and what the skill can
build instead, or point them to the Sumsub dashboard — never send the setup another way.

## Not supported in this iteration

The builder rejects these with an explanatory error; point the user to the Sumsub dashboard.

- `COMPANY` — the legacy WebSDK 1.0 KYB step (one docSet with `steps`). The API rejects it on
  WebSDK 2.0 levels.
- Building `COMPANY_ADDRESSES` (an update keeps an existing one with `keep: true`).
- The `accountUsers` role, and company parties for `ubos` / `representatives`.
- Other steps on company levels (`IDENTITY`, `SELFIE`, `APPLICANT_DATA`, …) and company levels
  of type `actions` / `module`.
- Primary-contact settings.
- Updating a copy of another account's level (`copyOf`) or a WebSDK 1.0 company level.

Full example: [`examples/kyb-company.json`](../examples/kyb-company.json).
