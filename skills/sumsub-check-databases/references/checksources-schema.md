# Check-sources response — schema reference

Source: Sumsub OpenAPI (`components.schemas.AgentCheckSourceDto`).

Envelope: `AgentCheckSourcesResponse` = `{ "checkSources": AgentCheckSourceDto[] }`. **KYC (individual) sources only** — company/KYB sources are not returned.

## Fields — `AgentCheckSourceDto`

| Field | Type | Notes |
|---|---|---|
| `sourceId` | string | Stable id, `{country}_{provider}_{subject}` (e.g. `arg_gov_dni`). |
| `name` | string | Human-readable source name. |
| `description` | string | Optional. One-line description of what the source verifies. |
| `dataSources` | string[] | Optional. Underlying registries / providers the source draws on. |
| `country` | string | ISO alpha-3 the source covers. |
| `checkType` | enum `BackgroundCheckType` | Internal check category — informational. KYC values: `E_KYC_CHECK`, `PERSON`, `TIN`. Use `validationReady` / `stepsReady`, not this, to decide placement. |
| `confirmationType` | enum `CheckConfirmationType` | How the applicant confirms a non-document check: `otp` (one-time code) · `oAuth` (authorises in an external service — bank account, national digital ID, …) · `eID` (NFC read of an eID card). Absent when the source needs no confirmation step. Informational — tells you what the applicant will be asked to do, not where the source goes in the level. |
| `status` | enum `AgentCheckSourceStatus` | Per-tenant enablement, **the usability gate**: `ENABLED` (licensed in production, and therefore in sandbox too — usable everywhere) · `SANDBOX_ONLY` (licensed in sandbox only — usable for sandbox testing, will not run in production; flag the prod gap before go-live) · `DISABLED` (not licensed anywhere — not usable). Environment-independent: the same value comes back whether the request was made in sandbox or prod. A workspace admin must request/enable anything not `ENABLED` — see [Enabling a source](../SKILL.md#enabling-a-source). |
| `validationReady` | boolean | `true` if the source can cross-validate a document already being collected — see *placement* below. |
| `stepsReady` | enum[] `IdDocSetType` | Which level step type(s) the source can be used as a non-document check for (e.g. `E_KYC`, `IDENTITY`) — **drives non-doc placement**, see below. Empty if the source has no non-doc use. |
| `supportedDocuments` | enum[] `IdDocType` | Doc types validated (e.g. `ID_CARD`, `PASSPORT`); non-document sources report a placeholder such as `OTHER3`. |
| `requiredInputFields` | string[] | Background-check input-data field **names** the applicant must supply (e.g. `number`, `dob`, `address.postCode`) — machine keys, not display labels. Sorted alphabetically. Never includes the selfie. |
| `optionalInputFields` | string[] | Same, but optional. |
| `selfieRequirement` | enum `FieldRequirement` | `REQUIRED` (the check cannot run without a selfie) · `ADDITIONAL` (optional; supplying one strengthens the match) · absent (no selfie involved). The selfie is reported **only** here — never look for it in the input-field lists. |
| `outputFields` | string[] | Fields returned on a match (e.g. `firstName`, `dob`, `addresses`). |
| `violations` | enum[] `BackgroundCheckViolation` | Mismatch reasons the source can raise — common ones below. |

## Enums

Only the two that need more than a line live here; every other enum's values are in the `Notes` column above.

### `validationReady` / `stepsReady` (drive placement)
| Field | Level placement |
|---|---|
| `validationReady: true` | Document + DB cross-check → keep the applicant's document step (e.g. `IDENTITY`) and attach the source at the **level's top-level `checkSourceSettings`**. |
| `stepsReady` contains a step type (e.g. `E_KYC`, `IDENTITY`, `PAYMENT_METHODS`) | Non-document use → attach the source inside **that docSet's own `checkSourceSettings`**. A dedicated docSet with no `types` (e.g. standalone `E_KYC`) means database-only, no upload; nesting it inside an existing `IDENTITY` docSet (which still keeps `types`) means the applicant can upload a document **or** pass the database check in the same step. `E_KYC`/`IDENTITY` non-doc identity also needs the `E_KYC_TARGET` entitlement — gate via [`sumsub-check-permissions`](../../sumsub-check-permissions/SKILL.md). |

A source can be `validationReady` and/or have entries in `stepsReady` — check both; they're independent. If `stepsReady` lists more than one step type, that's a menu of valid homes for the same source, not a mandate to use all of them — pick the one that matches the user's intent (keep document upload optional vs. go fully doc-free).

### `violations` — `BackgroundCheckViolation` (common database-check subset)
`DATA_NOT_FOUND` / `NO_APPLICANT_DATA` (no record) · `NAME_MISMATCH` · `BDATE_MISMATCH` · `GENDER_MISMATCH` · `TIN_MISMATCH` · `ID_NUMBER_MISMATCH` / `INVALID_DOC_NUMBER` · `ADDRESS_MISMATCH` · `SELFIE_MISMATCH` · `DEAD` · `PERSON_IS_MINOR` · `INVALID_STATUS`. The full enum is large and mostly OCR/MRZ-specific.
