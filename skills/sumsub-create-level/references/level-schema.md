# ApplicantLevel — schema reference

Source: Sumsub OpenAPI (`components.schemas.ApplicantLevel`).

## Top-level fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | **Required**, ≤ 256 chars. Must be unique within the client. Shown in the dashboard and used by SDKs via `levelName`. |
| `type` | enum | `standalone` (default — applicant onboarding), `actions` (one-off step like a re-verification), `module` (composable). |
| `applicantType` | enum | `individual` (default) or `company`. Choose `company` for KYB-style flows; the dashboard then expects `COMPANY` doc-set steps. |
| `desc` | string | ≤ 2048 chars. Optional description. |
| `requiredIdDocs.docSets` | array | **Required**. Ordered list of `ApplicantIdDocSet` entries — see below. The order is the order the SDK walks the applicant through. |
| `requiredIdDocs.includedCountries` / `excludedCountries` | array | Optional ISO-alpha-3 lists to restrict where the level is valid. |
| `requiredIdDocs.videoIdent` | boolean | Toggles the video-ident container. Set `videoIdentSettings` alongside if needed. |
| `crossCheckPresetId` | bsonObjectId | Optional — attach a cross-check preset for image/face deduplication. |
| `rejectUsaResidents` | boolean | Hard block on US residents. |
| `ipRestrictionSettings`, `applicantInsightSettings`, `deviceIntelligenceSettings`, `kytSettings`, `watchListCheckSettings`, `agreementSettings`, `checkSourceSettings` | objects | Pass-through; each has its own sub-schema in the OpenAPI spec. |

Server-populated, never send: `id`, `_id`, `clientId`, `key`, `createdAt`, `createdBy`, `modifiedAt`, `created`, `modified`.

## ApplicantIdDocSet (one entry in `docSets`)

| Field | Type | Notes |
|---|---|---|
| `idDocSetType` | enum | The step kind — see *IdDocSetType* below. **Required**. |
| `types` | string[] | Allowed `IdDocType` values (e.g. `PASSPORT`, `ID_CARD`). Required for identity / selfie / proof-of-residence; ignored for verification-only steps. |
| `subTypes` | string[] | Optional `IdDocSubType` narrowing. |
| `videoRequired` | enum | IDENTITY: `disabled` (file upload), `docapture` (live capture) — other values fall through to null in the read-mapper. SELFIE: `disabled`, `enabled`, `photoRequired`, `passiveLiveness` (public); `staticLiveness`, `liveness`, `optional` (non-public / deprecated but accepted on round-trip). **This is the persistent toggle** — backend's `captureParams` block is a derived read-only view, do not send it. |
| `captureMode` | enum | `manualAndAuto`, `manualOnly`, `seamless` (public); `manualAfterTimeout` (deprecated, still accepted on write — legacy levels may carry it). Sub-option for IDENTITY's `docapture` mode (auto vs manual photo). |
| `uploaderMode` | enum | `always`, `never`, `fallback`. Sub-option for IDENTITY's `docapture` mode (allow falling back to file upload). |
| `mode` | enum | `single`, `any`, `all` — how `types` are required. |
| `nfcVerificationSettings` | object | `{mode: disabled\|optional\|required}` — Mobile SDK only. `required` auto-rejects Web SDK applicants. |
| `fields` | `ApplicantIdDocSetField[]` | For `APPLICANT_DATA` and `COMPANY.steps[].fields`. Each: `{name, required, prefill, immutableIfPresent}`. |
| `customFields` | `ApplicantIdDocSetCustomField[]` | `{name, displayName, required, immutableIfPresent}`. |
| `questionnaireDefId` | string | **Required** for `QUESTIONNAIRE*` types — the questionnaire `id` (slug). The level-skill builder also accepts `questionnaireId` as an alias. Pass the `id` returned by `sumsub-create-questionnaire`. |
| `poaStepSettingsId` | bsonObjectId | **Required** on `PROOF_OF_RESIDENCE*` types — the server rejects the level with an error if omitted ("PoA preset can't be null"). Attaches a POA preset (`PoaStepSettings`) to govern accepted POA document types, validity windows, POI-as-POA, and cross-validator rules. The level-skill builder accepts `poaPresetId` as a friendlier alias. Pass the `id` returned by `sumsub-create-poa-preset`. |
| `paymentMethods` | array | **Legacy.** Do not set on new levels — pass `[]` or omit. The active configuration lives in `paymentSourceSettings` below. |
| `paymentSourceSettings` | object | **Required** for `PAYMENT_METHODS` docSets. Contains `skipOwnershipCheck` (bool), `skipRiskScoreCheck` (bool — cannot both be true), `walletScreeningProvider` (enum), `typeSettings` (per-type config object — see *Payment source type settings* below). The builder always emits this; the API rejects the level without it. |
| `steps` | `ApplicantIdDocSetStep[]` | For `COMPANY` — see *KYB steps*. |
| `emailVerificationSettings` / `phoneVerificationSettings` | object | Provider/template selection for verification steps. |
| `esignSettings` | object | E-sign document configuration. |
| `restrictCountries` | boolean | Per-step country restriction toggle. |
| `skipAllowed` | boolean | Whether the applicant can skip this step. |

## IdDocSetType (enum — all valid `type` values)

```
APPLICANT_DATA, EMAIL_VERIFICATION, PHONE_VERIFICATION,
IDENTITY, IDENTITY2, IDENTITY3, IDENTITY4,
SELFIE, SELFIE2,
PROOF_OF_RESIDENCE, PROOF_OF_RESIDENCE2, PROOF_OF_PAYMENT,
PAYMENT_METHODS, INVESTABILITY,
COMPANY, COMPANY_DATA, COMPANY_DOCUMENTS, COMPANY_BENEFICIARIES,
ACCREDITED_INVESTOR, E_SIGN,
QUESTIONNAIRE, QUESTIONNAIRE2, QUESTIONNAIRE3, QUESTIONNAIRE4,
E_KYC, OTHER_DOCS, TR_RECIPIENT_INFORMATION, DEVICE_CHECK,
SOLANA_ATTESTATION, LINEA_ATTESTATION, CHAINLINK_ATTESTATION
```

Use `IDENTITY2`/`3`/`4` when you need *additional* identity captures in the same level (e.g. a video-ident flow that needs front + back + recapture).

## Common `IdDocType` values

`PASSPORT`, `ID_CARD`, `DRIVERS`, `RESIDENCE_PERMIT`, `VIDEO_SELFIE`, `SELFIE`, `UTILITY_BILL`, `BANK_STATEMENT`, `COMPANY_DOC`, `POWER_OF_ATTORNEY`, `TAX_RETURN`, `RENTAL_AGREEMENT`, etc. (Full enum is `IdDocType` in the OpenAPI.)

## Payment source type settings (`paymentSourceSettings.typeSettings`)

Each key in `typeSettings` enables a payment source category. Omit a key entirely to disable that type.

**`bankCard`**

| Field | Type | Notes |
|---|---|---|
| `allowed` | bool | Enable bank card verification. |
| `countImages` | enum | `"one"` / `"two"` / `"some"` — number of card photos required. |
| `extractIban` | bool | Extract IBAN from card image. |
| `extractNationalBankAccountNumbers` | bool | Extract national bank account numbers. |
| `requireBankAccountNumber` | bool | Require successful account number extraction. |

**`bankAccount`**

| Field | Type | Notes |
|---|---|---|
| `allowed` | bool | Enable bank account verification. |
| `allowBankStatementUpload` | bool | Allow uploading a bank statement. |
| `allowExternalSourcesCheck` | bool | Enable online banking check. Requires `E_KYC_TARGET` entitlement. |

**`cryptoWallet`**

| Field | Type | Notes |
|---|---|---|
| `allowed` | bool | Enable crypto wallet verification. |
| `satoshiTestAllowed` | bool | Enable Satoshi test for ownership proof. |
| `unhostedWalletFormType` | enum | Jurisdiction-specific form: `"DEFAULT"` / `"SIMPLE"` / `"KAZ"` / `"TUR"` / `"SGP"` / `"POL"` / `"ITA"`. |

**`eWallet`**

| Field | Type | Notes |
|---|---|---|
| `allowed` | bool | Enable e-wallet verification. |

**`walletScreeningProvider`** (top-level on `paymentSourceSettings`, not inside `typeSettings.cryptoWallet`):

`"crystal"` / `"merkle"` / `"trmLabs"` / `"chainalysis"` / `"elliptic"` / `"cyvers"`

## KYB steps (`COMPANY.steps[]`)

Each step represents a sub-flow inside the KYB. Typical step names:

- `company` — capture company docs (`minDocsCnt: 1`), fields like `companyName`, `registrationNumber`.
- `ubos` — capture ultimate beneficial owners. `applicantLevelName` here links to a *child level* used to verify each UBO; pass the child level's `name`.
- `representatives` — directors / legal representatives. Typically takes `POWER_OF_ATTORNEY` docs.
- `branches`, `shareholders` — less common but supported.

Each step accepts `{name, minDocsCnt, applicantLevelName, idDocTypes, idDocSubTypes, fields, customFields, captureMode}`. The `name` is the contract; the dashboard uses it to render the section header.

## Common gotchas

- **Name collisions** — Sumsub fails with 400 if `name` already exists for the client. Pick a unique one.
- **QUESTIONNAIRE without `questionnaireDefId`** — silent fail in the dashboard later. The builder rejects this upfront.
- **`PROOF_OF_RESIDENCE*` without `poaStepSettingsId`** — the server rejects the level ("PoA preset can't be null"). This field is enforced in practice even though it may appear optional. Always create a POA preset first (`sumsub-create-poa-preset`) and pass its `id` before POSTing the level.
- **Duplicate `idDocSetType` in the same level** — Sumsub will reject. Use `IDENTITY` / `IDENTITY2` if you really need two identity captures.
- **`applicantType: company` + non-COMPANY docSets** — allowed but odd; the WebSDK skips KYB-specific UI.
- **`crossCheckPresetId`** must be an existing preset (create one via `sumsub-create-cross-check-preset`, or omit and Sumsub auto-applies the tenant default).
- **VideoIdent flows** — set `requiredIdDocs.videoIdent: true` and put captures under `videoIdentSettings`. `videoRequired` does **not** accept a `videoIdent` value (the backend enum has no such member).
- **Don't send `captureParams` on writes** — the field is `@Transient` server-side (Jackson accepts it on POST and the response echoes it back, but Mongo never persists it; on the next GET it's gone). For IDENTITY, the persisted toggle for File-upload ↔ Live-capture is the flat `videoRequired` on the docSet (`disabled` vs `docapture`), with `captureMode` and `uploaderMode` as docapture sub-options. The dashboard's `captureParams` view is derived from those three on read.
- **PATCH replaces `requiredIdDocs.docSets` wholesale.** Top-level Level fields merge via Morphia partial update, but `requiredIdDocs` (which holds the `docSets` array) is overwritten as a single chunk. A PATCH with only `{videoRequired: docapture}` on a docSet WIPES any previously-stored `captureMode` / `uploaderMode` / `nfcVerificationSettings` on that same docSet. **Always send the full intended state of each docSet on PATCH.** Read the current level via `get_level.sh` first if you want to preserve untouched fields.
- **IDENTITY docapture is types-sensitive on read.** `ApplicantHelper.getCaptureParams` only renders the docapture projection if `docSet.types` intersects `PERSON_ID_DOCS_WO_TRAVEL_PASSPORT = {ID_CARD, PASSPORT, RESIDENCE_PERMIT, DRIVERS}`. A `videoRequired: docapture` step with `types: [TRAVEL_PASSPORT]` only would NOT live-capture in the dashboard — it'd fall through to null. Stick to the standard four types unless you know what you're doing.
- **`videoRequired: disabled` (IDENTITY): `captureMode`/`uploaderMode` are silently dropped** by this builder when the input also includes them, matching the dashboard's Vue watcher that deletes both on toggle to File upload. Sending them is not an API error — just dead state — and this skill cleans them out before POST.
- **Country restrictions** — `includedCountries` is allowlist semantics, `excludedCountries` is blocklist. Both are ISO-3166 alpha-3.
- **AML / watchlist screening depends on the `WATCHLISTS` tenant entitlement first, then the level flag.** Two gates, in order:
  - **Tenant gate:** screening exists only if `WATCHLISTS` is in the tenant's `allowedChecks` (from `sumsub-check-permissions`). If it's **absent**, AML/PEP/sanctions screening is **off for the whole tenant** and **no level setting turns it on** — the feature needs to be enabled by the tenant's CSM.
  - **Level gate (when the tenant has `WATCHLISTS`):** It runs on a level unless you switch it **off** via the **inverted, top-level** Level field **`disableWatchlists`** (a sibling of `watchListCheckSettings`, not a member of it): `disableWatchlists: true` turns screening **off** for that level; absent or `false` leaves it **on**.
  - So for a policy that *requires* AML screening: confirm `WATCHLISTS` is entitled, then send nothing extra (it's already on), and GET the level back to check `disableWatchlists` is not `true`.
- **AML provider is tenant-gated** — `amlCaseType` (inside `watchListCheckSettings`) selects the screening provider and must match one the tenant is provisioned for, or POST returns 400 (e.g. *"Failed to update settings: amlwSearch is not allowed."*). This is separate from on/off (above). Safe fallback: omit `amlCaseType` and set `useCustomWatchListCheckSettings: false` — the level inherits the tenant's default provider.
- **`deviceIntelligenceSettings.enabled: true` is silently downgraded** to `false` unless the tenant has the Device Intelligence entitlement. The API accepts the field and returns 200, but the stored value is `false`. Always GET the level back and report any discrepancy.
- **Every POST creates a new entity** — the server does not deduplicate by name. Always list existing levels/presets/questionnaires first and reuse ids if a match is found.
- **Always GET the level back after writing** — several fields land differently from what was sent (server-assigned `key`, silently dropped entitlement-gated fields, AML overrides). Compare sent vs returned and surface any discrepancy.

## Selfie liveness (`docSets[SELFIE].videoRequired`)

Always include `videoRequired` on a SELFIE docSet:

- `passiveLiveness` — **default**. Advanced passive liveness, no head movement required.
- `staticLiveness` — single-frame analysis; use only when explicitly requested.
- `photoRequired` — photo-only selfie, no liveness; use only when explicitly requested.
- `enabled` — short video fragment (pronounce displayed digits); use only when explicitly requested.
- `liveness` — **deprecated** backend value. Do not generate for new levels.
- `disabled` — do not use as a default; use `photoRequired` if liveness is unwanted.

## AML providers (`watchListCheckSettings.amlCaseType`)

`caSearch` (ComplyAdvantage) | `wcCase` (World-Check One) | `djAssociation` (Dow Jones) | `quantifindSearch` (Quantifind) | `amlwSearch` (AML Watcher) | `caMeshSearch` (ComplyAdvantage Mesh)

Each tenant is provisioned for one or two — sending any other value returns 400.

## AML risk labels

`sanctions | pep | adverseMedia | terrorism | crime | fitnessProbity`

## Country-specific `IdDocType` mappings

Sumsub uses generic types for country-specific documents:
- Brazil RG → `ID_CARD`; Brazil CNH → `DRIVERS`
- India Aadhaar → `ID_CARD`
- US driver's license → `DRIVERS`
- US Social Security — no dedicated type; use `OTHER_DOCS` step.

## `websdkNext`

**New levels must be WebSDK 2.0 (`websdkNext: true`); existing levels are left alone.** WebSDK 1.0 is deprecated, and omitting the flag on a raw API create leaves the level on the legacy SDK. So on **create** (no `id` in the spec) `build_level.py` **defaults `websdkNext` to `true`** — you can't accidentally ship a 1.0 level, and the only way to get 1.0 is to set `websdkNext: false` explicitly (don't). On **update** (spec has an `id`) the builder does **not** touch `websdkNext`: omitting it lets the PATCH merge keep the level's current value, because upgrading an existing level from 1.0 to 2.0 is a significant client-side migration that must not happen as a side effect. Change an existing level's `websdkNext` only when the user explicitly asks.

## Error recovery

| Error | Likely cause | Fix |
|---|---|---|
| 400 `Invalid questionnaire id: null` | No `id` on POST questionnaire | Add a stable `id` slug to the body |
| 400 `…<value> is not valid, must be one of: a, b, c` | Wrong enum value | Pick from the listed set and retry |
| 400 `Failed to update settings: <provider> is not allowed` | Tenant not provisioned for that AML provider | Drop `amlCaseType`, set `useCustomWatchListCheckSettings: false` |
| 403 `Invalid {CLIENT_ID=…, KEY=…} fields value` | Sent `key` on level create | Remove `key` from body |
| Stored value differs from sent | Tenant entitlement gate (e.g. Device Intelligence) | Report to user; needs tenant-level enable |
| 401 / 403 with no body | Missing or expired credentials / missing headers | Check token and signature |

