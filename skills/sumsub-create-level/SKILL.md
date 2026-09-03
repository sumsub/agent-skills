---
name: sumsub-create-level
description: Create or update a Sumsub applicant level. POST `/resources/applicants/-/levels` to create new, PATCH same path to update (id in body), GET `/resources/applicants/-/levels/{id}` to read one back. TRIGGER when the user asks to "create / add / build / update / edit a Sumsub level", supplies a list of required steps for an applicant flow (identity / selfie / proof-of-residence / questionnaire / payment methods / email or phone verification / KYB / e-sign), or wants a level wired to a specific questionnaireDefId. SKIP for other Sumsub entities (questionnaires, workflows, applicants) or for one-off subsetting tweaks not covered by the compact spec (use `sumsub-api-generic` for those).
allowed-tools: Read, Write, Bash
---

# Sumsub — Create Level

Builds an `ApplicantLevel` JSON payload from a compact spec, POSTs (or PATCHes) it to the Sumsub API, and reports the resulting `name` / `id`.

## Endpoints

| Method | Path | When |
|---|---|---|
| `POST` | `/resources/applicants/-/levels` | Create a new level. Body must NOT include `id` or `key` — server assigns them. |
| `PATCH` | `/resources/applicants/-/levels` | Update an existing level (by `id` in body). |
| `GET` | `/resources/applicants/-/levels/{id}` | Read one level. Use this to verify what landed (tenant gates may silently drop fields) or to resolve `name` from a known `id`. |
| `GET` | `/resources/applicants/-/levels` | List all levels (use to reuse existing levels before creating duplicates). |

Body: [`ApplicantLevel`](references/level-schema.md). Returns the persisted level with `id`, `createdAt`, audit trails.

## Auth — App Token + secret (sandbox only)

This skill talks to the public Sumsub API and signs each request per
[the authentication reference](https://docs.sumsub.com/reference/authentication).
The full how-it-works writeup lives in the [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md)
skill — read it if you hit `401 Invalid signature`.

> **⚠️ Sandbox tokens only.** Do **not** accept or use a production App Token
> here — creating a level is a workspace-visible write. If the user offers a
> prod token, refuse and ask them to generate a sandbox pair at
> <https://cockpit.sumsub.com/checkus/home?sbx=true> (**Connect Sumsub to
> your AI agent** -> **Build & configure** -> **Generate token**). Token +
> secret are shown once — copy both before closing the dialog. The helper script
> enforces this — it rejects tokens that don't start with `sbx:`.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

## Procedure

0. **Fetch tenant entitlements.** Invoke the `sumsub-check-permissions` skill and parse the JSON result. Store the `allowedChecks` map (its keys are the enabled entitlements); use it for all feature-gate checks in step 2 and the entitlements section below. Do this before anything else.
1. **Check existing entities.** Before building anything, list existing levels, POA presets, and questionnaires (GET the respective list endpoints). If a matching entity already exists, offer to reuse its `id` and skip the POST — the server creates a duplicate on every POST with no name deduplication.
2. **Translate the user's request to the compact spec** below — name, applicant type, and a list of doc-set steps in the order they should appear in the WebSDK flow.
3. **Validate** — confirm every `type` is a real `IdDocSetType`, every `QUESTIONNAIRE` step has a `questionnaireDefId` that points to an existing questionnaire, every `PROOF_OF_RESIDENCE*` step has a `poaPresetId` / `poaStepSettingsId` (the server rejects the level if it's missing — run `sumsub-create-poa-preset` first if no preset exists), every `COMPANY` step has at least one named sub-step. Use the `allowedChecks` keys from step 0 to reject any entitlement-gated feature not present in it.
4. **Generate payload** — run `${CLAUDE_SKILL_DIR}/scripts/build_level.py` with the spec on stdin → full payload on stdout.
5. **Show the resolved payload to the user and ask for explicit confirmation** before the first POST.
6. **Create vs. update**:
   - **New level** — POST via `${CLAUDE_SKILL_DIR}/scripts/post_level.sh`. Returns response body + HTTP status.
   - **Update existing** — GET the current state via `${CLAUDE_SKILL_DIR}/scripts/get_level.sh` so the user sees the diff, then PATCH via `${CLAUDE_SKILL_DIR}/scripts/patch_level.sh`. **The spec passed to `build_level.py` must include `id: <level-id>`** — the builder preserves it into the payload, and PATCH refuses bodies without it. **PATCH replaces `requiredIdDocs.docSets` as a single array** — every docSet you send must carry the full intended state, since fields omitted from a docSet are wiped on the server. Copy preserved values from the GET response into your PATCH spec.
7. **GET the level back** via `${CLAUDE_SKILL_DIR}/scripts/get_level.sh` and compare to what was sent — several fields land differently from what was sent (see gotchas in [references/level-schema.md](references/level-schema.md)). Report any discrepancy to the user.
8. **Build the dashboard link.** Read `id`, `applicantType`, and `clientId` from the response body and format:

   ```
   https://cockpit.sumsub.com/checkus/sdkIntegrations/levels/<applicantType>Level/<id>?clientId=<clientId>&sbx=true
   ```

   The `<applicantType>Level` segment is literally `individualLevel` for `applicantType: individual` (confirmed) and `companyLevel` for `applicantType: company` (assumed by analogy — surface as the best guess and flag if it 404s). The `sbx=true` query param targets the **Sandbox** workspace — it is the canonical sandbox link param shared across all skills.
9. **Report** — lead with the human-readable name:
   - `name`, `applicantType`, ordered list of docSets created.
   - **Dashboard link** as a clickable markdown link.
   - Final line: `Level ID (for SDK access tokens / future PATCH): <id>`.

   Surface 4xx errors verbatim — they usually point to a missing `questionnaireDefId` or an unknown enum value.

## Tenant entitlements

Many level settings are gated behind tenant entitlements (`allowedChecks`). Before enabling a feature, check that the required `BackgroundCheckTarget` is present as a key in the `allowedChecks` map returned by [`sumsub-check-permissions`](../sumsub-check-permissions/SKILL.md) (fetched in step 0).

DocSet type → required permission (OR — any one suffices):

| DocSet type | Required (any one of) |
|---|---|
| `QUESTIONNAIRE` / `QUESTIONNAIRE2-4` | `QUESTIONNAIRE` |
| `COMPANY` / `COMPANY_DATA` | `COMPANY` \| `KYB_FULL` \| `KYB_AUTO_AML_AND_REGISTRY` \| `KYB_AUTO_AML_ONLY` |
| `SOLANA_ATTESTATION` / `LINEA_ATTESTATION` | `PAYMENT_METHOD_CRYPTO` |
| `PAYMENT_METHODS` | `PAYMENT_SOURCE` \| `PAYMENT_METHOD` \| `PAYMENT_METHOD_CRYPTO` \| `KYT_UNHOSTED_WALLET_VERIFICATION` |
| `INVESTABILITY` | `PROOF_OF_FUNDS` |
| `PROOF_OF_RESIDENCE` / `PROOF_OF_RESIDENCE2` | `POA` \| `ADVANCED_POA_TYPE_DETECTION` (often missing from `allowedChecks` even when the API actually allows it — proceed with a one-line warning; see below) |
| `E_KYC` | `E_KYC_TARGET` |
| `E_SIGN` | `E_SIGN_TARGET` |
| `TR_RECIPIENT_INFORMATION` | `TRAVEL_RULE` |
| `DEVICE_CHECK` | `DEVICE_INTELLIGENCE` |

Types not in this table (`IDENTITY`, `SELFIE`, `APPLICANT_DATA`, `EMAIL_VERIFICATION`, `PHONE_VERIFICATION`, etc.) are available to all tenants — no entitlement required.

**AML / watchlist screening → `WATCHLISTS`.** This isn't a docSet — it's level-wide behavior. When `WATCHLISTS` is in `allowedChecks`, AML/PEP/sanctions screening runs **on by default** on every level (turn it off per-level with `disableWatchlists: true`). When `WATCHLISTS` is **absent**, screening is off tenant-wide and no level setting enables it — treat a policy that needs AML screening as blocked on the missing entitlement (contact CSM), same as the docSet gates above.

**If a requested feature requires an entitlement the tenant doesn't have — stop immediately.** Do not build or POST the level. Tell the user which entitlement is missing, that the feature is unavailable on their account, and that they need to contact their CSM or Sumsub support to get it enabled. Resume only after the user confirms the entitlement has been added or explicitly decides to drop the feature.

**Exception — POA.** The `POA` / `ADVANCED_POA_TYPE_DETECTION` keys are often absent from `allowedChecks` even on tenants where the API actually accepts `PROOF_OF_RESIDENCE` levels (the entitlement seems to be baseline or covered by other keys; the documented mapping is stale on some tenants). When only `POA` is missing, **proceed with a one-line warning to the user** so they have context if support is later needed. Do NOT pause for explicit confirmation — Sumsub itself will reject the write if the tenant truly lacks the right, and that 4xx will be more informative than a pre-emptive halt. Surface any entitlement-related error verbatim if it comes back.

## Safety

Creating a level is a write to a shared workspace. Always:
- Show the resolved payload to the user before the first POST (step 4 above).
- After each successful POST, GET the entity back and compare to what was sent — silent overrides are common.
- Do not re-POST a dependency (PoA preset, questionnaire) if it already succeeded mid-session — reuse the returned `id`.
- Do not delete or modify levels you didn't create in this session unless the user explicitly names them.

## Names, not ids, in user-facing messages

This applies to **every** message you send the user about this level — not just the final report:

- **Pre-POST summary:** when you list which questionnaire and which POA preset will be attached, refer to each by `name` / `title` (e.g. "POA preset «POA — 60 days»", "questionnaire «Applicant basics»"). Do **not** paste the raw `id` ("`6a16bfd4ded0fe13aa48165d`") into prose — the user can't read it and it does not let them judge whether you picked the right entity.
- **Final report:** still ends with `Level ID (for SDK access tokens / future PATCH): <id>` on its own line — that line is the one place a raw id is correct, because the user needs to copy it for the next API call.
- **Diagnostic messages:** when a 4xx response references a dependency id (POA preset not found, etc.), translate it to the name before showing the user.

If you don't yet know an entity's name (e.g. user supplied only an id from outside this session), GET the entity first and surface its name; do not fall back to the id.

## Compact spec format

Accepts JSON or YAML on stdin. The builder fills in sensible defaults for each doc-set type (see [references/level-schema.md](references/level-schema.md)).

```json
{
  "name": "Basic KYC",
  "applicantType": "individual",
  "type": "standalone",
  "docSets": [
    {"type": "IDENTITY", "docTypes": ["PASSPORT","ID_CARD","DRIVERS"]},
    {"type": "SELFIE", "videoRequired": "passiveLiveness"},
    {"type": "PROOF_OF_RESIDENCE", "docTypes": ["UTILITY_BILL"]},
    {"type": "QUESTIONNAIRE", "questionnaireDefId": "source-of-funds"}
  ]
}
```

> **New levels must be WebSDK 2.0 (`websdkNext: true`).** On **create**, the builder sets `websdkNext: true` automatically — you don't need it in the spec; just never set `websdkNext: false` (that ships a deprecated WebSDK 1.0 level). On **update** of an existing level (spec has an `id`), the builder leaves `websdkNext` **untouched** and you should too: upgrading a live level's SDK is a heavy client-side migration, so never flip it as a side effect of an unrelated PATCH — change it only if the user explicitly asks.

### Supported `docSets[].type` values

`APPLICANT_DATA`, `EMAIL_VERIFICATION`, `PHONE_VERIFICATION`, `IDENTITY`, `IDENTITY2`/`3`/`4`, `SELFIE`, `SELFIE2`, `PROOF_OF_RESIDENCE`, `PROOF_OF_RESIDENCE2`, `PROOF_OF_PAYMENT`, `PAYMENT_METHODS`, `INVESTABILITY`, `COMPANY`, `COMPANY_DATA`, `COMPANY_DOCUMENTS`, `COMPANY_BENEFICIARIES`, `ACCREDITED_INVESTOR`, `E_SIGN`, `QUESTIONNAIRE`/`2`/`3`/`4`, `E_KYC`, `OTHER_DOCS`, `TR_RECIPIENT_INFORMATION`, `DEVICE_CHECK`.

### Per-type compact shortcuts

| `type` | Shortcut keys | Builder expands to |
|---|---|---|
| `IDENTITY*` | `docTypes`; `videoRequired` (`disabled` / `docapture`); `captureMode` & `uploaderMode` (sent only when docapture); `nfcVerificationSettings: {mode}` | flat fields on the docSet — only what you set. See [Dashboard ↔ API mapping](#dashboard--api-mapping-for-identity-step) below. |
| `SELFIE*` | `videoRequired` (default `passiveLiveness`; full set: `disabled` / `enabled` / `photoRequired` / `passiveLiveness` / `staticLiveness`), `docTypes` (default `["SELFIE"]`); `selfieProcessingSettings: {skipLivenessCheck, skipFaceMatchCheck}` (used with payment-method verification — see below) | bare docSet with `videoRequired` [+ `selfieProcessingSettings`] |
| `PROOF_OF_RESIDENCE*` | `docTypes` (default `["UTILITY_BILL"]`); **`poaPresetId`** (or `poaStepSettingsId`) to attach a POA preset by id | docSet + `poaStepSettingsId` |
| `QUESTIONNAIRE*` | **`questionnaireDefId`** (or `questionnaireId` alias) *— required* | bare docSet |
| `APPLICANT_DATA` | `fields` — array of strings or `{name, required, prefill, immutableIfPresent}` | `fields[]` with defaults |
| `PAYMENT_METHODS` | `typeSettings` (object — keys: `bankCard`, `bankAccount`, `cryptoWallet`, `eWallet` — see [Payment method verification](#payment-method-verification-step-or-action) below); `skipOwnershipCheck` (bool, default `false`); `skipRiskScoreCheck` (bool); `walletScreeningProvider` (enum — see schema) | `paymentSourceSettings` with validated structure; always emits `types: ["PAYMENT_SOURCE"]` |
| `EMAIL_VERIFICATION` / `PHONE_VERIFICATION` | — | bare docSet |
| `COMPANY` | `steps` — array of `{name, minDocsCnt?, idDocTypes?, idDocSubTypes?, fields?, applicantLevelName?}` | full KYB step structure |
| `E_SIGN` | `esignSettings` (pass-through) | as-is |

Unknown keys in a docSet are passed through to the API verbatim, so escape hatches are easy when you need an obscure field.

### Dashboard ↔ API mapping for IDENTITY step

Verbatim labels from the Sumsub dashboard sidebar, paired with the API value to write. Match the user's description to a label, then use the value.

| Dashboard control | Label (user-visible) | API value | Spec key |
|---|---|---|---|
| Capture method | File upload | `disabled` | `videoRequired` |
| Capture method | Live capture | `docapture` | `videoRequired` |
| Capture mode¹ | Both manual and auto capture work at the same time | `manualAndAuto` | `captureMode` |
| Capture mode¹ | Only manual capture is active | `manualOnly` | `captureMode` |
| Capture mode¹ | Seamless live capture | `seamless` | `captureMode` |
| Fallback to file upload¹ | Always available | `always` | `uploaderMode` |
| Fallback to file upload¹ | Available only if camera capture failed | `fallback` | `uploaderMode` |
| Fallback to file upload¹ | Not available | `never` | `uploaderMode` |
| NFC verification² | Disabled | `disabled` | `nfcVerificationSettings.mode` |
| NFC verification² | Optional | `optional` | `nfcVerificationSettings.mode` |
| NFC verification² | Required | `required` | `nfcVerificationSettings.mode` |

¹ Only meaningful with `videoRequired: docapture`. Silently dropped from the payload otherwise (matches the dashboard's own behavior — it deletes both keys when the radio is toggled to File upload).
² `required` auto-rejects Web SDK applicants; Mobile SDK only.

**Defaults emitted by the builder** (necessary for the dashboard to render — the controls bind to actual stored values, not implicit UI defaults; empty fields render as "Select" placeholder, not as the default option):

- `videoRequired: docapture` → `captureMode: manualAndAuto`, `uploaderMode: always` (unless caller overrides).
- IDENTITY always gets `nfcVerificationSettings: {mode: disabled}` unless caller overrides.

These match what the dashboard's own Vue watcher writes when the user first toggles Live capture. **Caveat on PATCH:** `requiredIdDocs.docSets` is replaced wholesale (only top-level Level fields merge) — every docSet in the PATCH spec must carry the full intended state, since omitted sub-fields are wiped. GET the level first and copy values you want to preserve.

### AML / watchlist screening: two separate gates

1. **Tenant gate — `WATCHLISTS` entitlement** (checked in step 0). If `WATCHLISTS` is in `allowedChecks`, AML screening is available and runs **by default** on every level. If it's **not**, screening is off for the whole tenant and **no level setting turns it on** — surface it as a missing entitlement (contact CSM), don't pretend the level enables it.
2. **Level gate — `disableWatchlists`** (only matters when the tenant has `WATCHLISTS`). To turn screening **off for this level**, send the top-level `"disableWatchlists": true`; omit it (or `false`) to keep it on. `watchListCheckSettings.amlCaseType` only selects the *provider* (tenant-gated), and `useCustomWatchListCheckSettings` only picks custom-vs-inherited config — neither is an on/off switch.

So for a policy that *requires* AML screening: confirm `WATCHLISTS` in step 0, then add nothing to the level and GET it back to confirm `disableWatchlists` isn't `true`. For a level that must **skip** AML, set `disableWatchlists: true`. Details: [references/level-schema.md](references/level-schema.md).

### Payment method verification (step or action)

Payment method verification — the `PAYMENT_METHODS` docSet, for verifying a bank card, bank account, crypto wallet, or e-wallet — runs in **two modes**:

- **As a step** in a normal verification level: add a `PAYMENT_METHODS` docSet alongside `IDENTITY` / `SELFIE` / `PROOF_OF_RESIDENCE` / etc. The level stays a regular `standalone` level with **no** `actionType`. Use this when payment verification is one part of a broader onboarding flow.
- **As an action** on an actions-type level: set `type: "actions"` and `actionType: "paymentMethod"`. Use this for a standalone, re-runnable payment-method check decoupled from onboarding.

Pick the mode from how the user frames it — "add card/wallet verification to my KYC level" → step; "create a standalone payment-method check / action" → action.

**Step mode** — inside a standard level (identity and payment coexist):

```json
{
  "name": "KYC + payment method",
  "type": "standalone",
  "applicantType": "individual",
  "docSets": [
    {"type": "IDENTITY"},
    {"type": "SELFIE", "videoRequired": "passiveLiveness"},
    {"type": "PAYMENT_METHODS",
     "typeSettings": {"bankCard": {"allowed": true, "countImages": "one"}}}
  ]
}
```

**Action mode** — inside an actions level:

```json
{
  "name": "Payment method check",
  "type": "actions",
  "actionType": "paymentMethod",
  "websdkNext": true,
  "docSets": [
    {"type": "PAYMENT_METHODS", "skipOwnershipCheck": false,
     "typeSettings": {"bankCard": {"allowed": true, "countImages": "one"}}}
  ]
}
```

**Constraints the builder enforces:**

- `actionType: "paymentMethod"` requires `type: "actions"`, and the level must include a `PAYMENT_METHODS` docSet.
- Cannot set both `skipOwnershipCheck: true` and `skipRiskScoreCheck: true` simultaneously.
- `walletScreeningProvider` goes at the `paymentSourceSettings` level, **not** inside `typeSettings.cryptoWallet` (the builder places it correctly).
- **`bankAccount` needs a concrete verification method.** Unlike `bankCard`, enabling a bank account with `allowed: true` alone is **rejected by the API** — it must enable at least one of `allowBankStatementUpload` (statement upload, no extra entitlement) or `allowExternalSourcesCheck` (external data-source check, uses the `E_KYC` entitlement). Ask the user which method(s) they want; don't offer a bare "standard" bank-account option.

**The `PAYMENT_METHODS` docSet (both modes):** the builder always emits `types: ["PAYMENT_SOURCE"]` plus a `paymentSourceSettings` object assembled from your compact spec — the API rejects the docSet without `paymentSourceSettings`, so the builder never omits it.

**`typeSettings` per payment source type:**

| Key | Fields |
|---|---|
| `bankCard` | `allowed` (bool); `countImages` (`"one"` / `"two"` / `"some"`); `extractIban` (bool); `extractNationalBankAccountNumbers` (bool); `requireBankAccountNumber` (bool) |
| `bankAccount` | `allowed` (bool); `allowBankStatementUpload` (bool); `allowExternalSourcesCheck` (bool — requires `E_KYC_TARGET` entitlement). **When `allowed`, at least one of these two methods must be `true`** — see constraints above. |
| `cryptoWallet` | `allowed` (bool); `satoshiTestAllowed` (bool); `unhostedWalletFormType` (`"DEFAULT"` / `"SIMPLE"` / `"KAZ"` / `"TUR"` / `"SGP"` / `"POL"` / `"ITA"`) |
| `eWallet` | `allowed` (bool) |

**`walletScreeningProvider` enum:** `crystal` / `merkle` / `trmLabs` / `chainalysis` / `elliptic` / `cyvers`

**Entitlement:** requires `PAYMENT_SOURCE` or `KYT_UNHOSTED_WALLET_VERIFICATION` (see [Tenant entitlements](#tenant-entitlements)).

**Dashboard link:** both modes live under `sdkIntegrations/levels/individualLevel/<id>` — the standard standalone-level URL pattern.

See [`examples/payment-methods.json`](examples/payment-methods.json) for a complete action-mode spec.

### Chaining with other Sumsub-* skills

This skill's `QUESTIONNAIRE` and `PROOF_OF_RESIDENCE` doc-sets accept ids produced by sibling skills, so a 3-step build-everything-from-scratch flow is natural:

| First run … | Pass the returned `id` as … |
|---|---|
| `sumsub-create-questionnaire` | `docSets[].questionnaireDefId` on a `QUESTIONNAIRE` doc-set |
| `sumsub-create-poa-preset` | `docSets[].poaPresetId` on a `PROOF_OF_RESIDENCE` doc-set |

See [`examples/with-presets.json`](examples/with-presets.json) for an end-to-end level that references both.

## Outputs

On success, lead with the human-readable info:
- `name`, `applicantType`, ordered list of `docSets[].idDocSetType`.
- **Dashboard link**: `https://cockpit.sumsub.com/checkus/sdkIntegrations/levels/<applicantType>Level/<id>?clientId=<clientId>&sbx=true`. Render as a clickable markdown link. The `<applicantType>Level` segment is `individualLevel` for individuals (confirmed) or `companyLevel` for companies (assumed pattern). All three fields (`id`, `applicantType`, `clientId`) come from the POST response body; `sbx=true` targets the Sandbox workspace.
- Finally, on its own line: `Level ID (for SDK access tokens / future PATCH): <id>`.

On failure: HTTP status + the `description`/`errorName` from Sumsub's error envelope.

## Worked examples

- [`examples/identity-selfie.json`](examples/identity-selfie.json) — the most common pattern.
- [`examples/identity-live-capture.json`](examples/identity-live-capture.json) — IDENTITY-only with Live capture + all docapture sub-options + NFC.
- [`examples/questionnaire-only.json`](examples/questionnaire-only.json) — pure data-collection level (like the SOF level in this repo).
- [`examples/full-kyc.json`](examples/full-kyc.json) — `APPLICANT_DATA + IDENTITY + SELFIE + PROOF_OF_RESIDENCE + QUESTIONNAIRE`.
- [`examples/kyb-company.json`](examples/kyb-company.json) — KYB level with company + UBOs + representatives steps.
- [`examples/with-presets.json`](examples/with-presets.json) — references both a questionnaire (`questionnaireDefId`) and a POA preset (`poaPresetId`) returned by sibling skills.
- [`examples/payment-methods.json`](examples/payment-methods.json) — payment method action level with bank card, bank account, crypto wallet, and e-wallet.

## See also

- [references/level-schema.md](references/level-schema.md) — full `ApplicantLevel` schema, all enum values, gotchas.