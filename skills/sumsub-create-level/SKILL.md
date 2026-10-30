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
| `PATCH` | `/resources/applicants/-/levels` | Update an existing level (by `id` in body). A top-level field missing from the body keeps its stored value; a field you send replaces the stored one whole (see step 6). |
| `GET` | `/resources/applicants/-/levels/{id}` | Read one level. Use this to verify what landed (tenant gates may silently drop fields) or to resolve `name` from a known `id`. |
| `GET` | `/resources/applicants/-/levels` | List all levels (`list_levels.sh`; use to reuse existing levels before creating duplicates). |

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
1. **Check existing entities.** Before building anything, list existing levels with `${CLAUDE_SKILL_DIR}/scripts/list_levels.sh > levels.out` (the levels are under `list.items`, match on `name`), and POA presets and questionnaires (GET the respective list endpoints). If a matching entity already exists, offer to reuse its `id` and skip the POST — the server creates a duplicate on every POST with no name deduplication. For a KYB level, the level list is also where you find the verification levels for its associated parties (see [KYB (company) levels](#kyb-company-levels)).
2. **Translate the user's request to the compact spec** below — name, applicant type, and a list of doc-set steps in the order they should appear in the WebSDK flow. If the request implies database / non-document verification, resolve sources via `sumsub-check-databases` first (see [Database / non-document verification](#database--non-document-verification-kyc)).
3. **Validate** — confirm every `type` is a real `IdDocSetType`, every `QUESTIONNAIRE` step has a `questionnaireDefId` that points to an existing questionnaire, every `PROOF_OF_RESIDENCE*` step has a `poaPresetId` / `poaStepSettingsId` (the server rejects the level if it's missing — run `sumsub-create-poa-preset` first if no preset exists). On a KYB level, every associated-party `levelName` names an existing standalone level of the matching applicant type, and `kybType` is a mode the tenant is entitled to. Use the `allowedChecks` keys from step 0 to reject any entitlement-gated feature not present among them.
4. **Generate payload** — run `${CLAUDE_SKILL_DIR}/scripts/build_level.py` with the spec on stdin → full payload on stdout. If it refuses, do not write or offer a payload built around it: tell the user the reason and the options that do work (change the spec, enable the entitlement, switch the level to WebSDK 2.0).
5. **Show the resolved payload to the user and ask for explicit confirmation** before every write, POST or PATCH.
6. **Create vs. update**:
   - **New level** — POST via `${CLAUDE_SKILL_DIR}/scripts/post_level.sh`. Returns response body + HTTP status.
   - **Update existing** — GET the current state via `${CLAUDE_SKILL_DIR}/scripts/get_level.sh` first. **If it is a company level (`applicantType: company`) with `websdkNext` not `true` (WebSDK 1.0), or a copy of another account's level (`copyOf`), stop here:** this skill makes no change to it at all — no step, KYB or not (removing a phone or email step included). Tell the user to make the change in the Sumsub dashboard, and don't send it any other way. Otherwise show the user the diff, then PATCH via `${CLAUDE_SKILL_DIR}/scripts/patch_level.sh`. **The spec passed to `build_level.py` must include `id: <level-id>`** — the builder preserves it into the payload, and PATCH refuses bodies without it. **PATCH keeps every top-level field missing from the body**, but a field you send replaces the stored one whole. So **put the GET response body into the spec as `base`**: the builder copies it into the payload first (minus the server-populated fields such as `key` and `clientId`) and lays the built fields over it, so the body carries the whole level and `requiredIdDocs` keeps its other keys around the new docSets. To set a top-level field the builder does not model (`customPrivacyLink`, for example), put it in the spec, on create or update: it passes through as given and wins over `base`. It also takes `type`, `applicantType`, `actionType`, `websdkNext` and `useCustomFraudPreventionSettings` from `base` when the spec leaves them out, so the level keeps its kind. A field you do send always replaces the stored one whole: `requiredIdDocs.docSets` is one array, so every docSet you send must carry its full intended state (copy preserved values from the GET into the docSet specs); leave `docSets` out of the spec to keep the stored steps as they are, and `fraudPreventionSettings` is one object (see [Fraud Prevention checks](#fraud-prevention-checks-client-wide-default--per-level-override)). **A PATCH cannot remove a top-level field**: the server reads `null` as an omitted field and keeps the stored value. Clear it with its empty value where that means unset: `""` for `customPrivacyLink` and `customPrivacyNoteText` (the consent screen and the dashboard treat a blank value as none), `false` for a flag. A field with no such value (an id, an object) is removed in the Sumsub dashboard UI only: tell the user so.
     - **Company (KYB) level** — every change goes through [Updating a KYB level](#updating-a-kyb-level), a non-KYB step (email, phone, questionnaire) included: the builder lays the spec over the GET response (`--base`, the same as the spec's `base`), so the steps and KYB settings the spec doesn't carry survive. It refuses a copy of another account's level and WebSDK 1.0 levels.
7. **GET the level back** via `${CLAUDE_SKILL_DIR}/scripts/get_level.sh` and compare to what was sent — several fields land differently from what was sent (see gotchas in [references/level-schema.md](references/level-schema.md)). For fraud prevention flags compare against `get_level_fraud_prevention.sh <level name>`, not against `fraudPreventionSettings` (see [Fraud Prevention checks](#fraud-prevention-checks-client-wide-default--per-level-override)). Report any discrepancy to the user.
8. **Build the dashboard link.** Read `id`, `applicantType`, and `clientId` from the response body and format:

   ```
   https://cockpit.sumsub.com/checkus/sdkIntegrations/levels/<applicantType>Level/<id>?clientId=<clientId>&sbx=true
   ```

   The `<applicantType>Level` segment is literally `individualLevel` for `applicantType: individual` and `companyLevel` for `applicantType: company`. The `sbx=true` query param targets the **Sandbox** workspace — it is the canonical sandbox link param shared across all skills.
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
| `COMPANY_DATA` (every KYB level) | `COMPANY` \| `KYB_FULL` \| `KYB_AUTO_AML_AND_REGISTRY` \| `KYB_AUTO_AML_ONLY` \| `KYB_APPLICANTS` — plus the level's `kybType` needs its own entitlement, see [KYB (company) levels](#kyb-company-levels) |
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

**Fraud Prevention checks → five separate targets.** Also not docSets: the advanced email / phone / IP checks, identity enrichment and device intelligence are level-wide behavior gated by `EMAIL_RISK_ASSESSMENT`, `PHONE_RISK_ASSESSMENT`, `IP_ADDRESS_ANALYSIS`, `DIGITAL_FOOTPRINT_TARGET` and `DEVICE_INTELLIGENCE` respectively. See [Fraud Prevention checks](#fraud-prevention-checks-client-wide-default--per-level-override) below for the per-check mapping and the override fields.

**If a requested feature requires an entitlement the tenant doesn't have — stop immediately.** Do not build or POST the level. Tell the user which entitlement is missing, that the feature is unavailable on their account, and that they need to contact their CSM or Sumsub support to get it enabled. Resume only after the user confirms the entitlement has been added or explicitly decides to drop the feature.

**Exception — POA.** The `POA` / `ADVANCED_POA_TYPE_DETECTION` keys are often absent from `allowedChecks` even on tenants where the API actually accepts `PROOF_OF_RESIDENCE` levels (the entitlement seems to be baseline or covered by other keys; the documented mapping is stale on some tenants). When only `POA` is missing, **proceed with a one-line warning to the user** so they have context if support is later needed. Do NOT pause for explicit confirmation — Sumsub itself will reject the write if the tenant truly lacks the right, and that 4xx will be more informative than a pre-emptive halt. Surface any entitlement-related error verbatim if it comes back.

## Safety

Creating a level is a write to a shared workspace. Always:
- **Send only what `build_level.py` built.** Never write or edit a level payload by hand, and never offer to send a setup "directly to the API" (raw `curl`, `sumsub-api-generic`). A builder error is final: tell the user what it rejected and what the skill can build instead, or point them to the Sumsub dashboard. For company (KYB) levels `post_level.sh` and `patch_level.sh` enforce this — they re-check the payload with `build_level.py --check` and refuse anything the builder wouldn't produce (exit 4). Write levels only with these two scripts: the `sumsub-api-generic` and `sumsub-api-auth` curl wrappers refuse level writes.
- **Set only what the user asked for.** The spec carries the user's request and nothing else — the builder fills in the dashboard's defaults. Don't add settings on your own (`canSkip`, `minRequired` / `maxAllowed`, thresholds, optional fields, extra roles or steps), even ones that look harmless or equal to the default. If a setting seems needed, ask.
- Show the resolved payload to the user and get a yes before every write, POST or PATCH (step 5 above).
- After each successful write, GET the entity back and compare to what was sent — silent overrides are common.
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

`APPLICANT_DATA`, `EMAIL_VERIFICATION`, `PHONE_VERIFICATION`, `IDENTITY`, `IDENTITY2`/`3`/`4`, `SELFIE`, `SELFIE2`, `PROOF_OF_RESIDENCE`, `PROOF_OF_RESIDENCE2`, `PROOF_OF_PAYMENT`, `PAYMENT_METHODS`, `INVESTABILITY`, `COMPANY_DATA`, `COMPANY_DOCUMENTS`, `COMPANY_BENEFICIARIES`, `ACCREDITED_INVESTOR`, `E_SIGN`, `QUESTIONNAIRE`/`2`/`3`/`4`, `E_KYC`, `OTHER_DOCS`, `TR_RECIPIENT_INFORMATION`, `DEVICE_CHECK`.

The builder rejects `COMPANY` (the legacy WebSDK 1.0 KYB step) and builds no `COMPANY_ADDRESSES` (not supported yet — a KYB update keeps an existing one, see [Updating a KYB level](#updating-a-kyb-level)).

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
| `COMPANY_DATA` | `fields` (default `country`, `companyName`, `registrationNumber`); `customFields` | company-information step, the first step of a new company level — see [references/kyb.md](references/kyb.md) |
| `COMPANY_DOCUMENTS` | `companyDocsGroupDefinitions` — `[{label, subTypes?, required?}]` (default one `legalPresence` group) | corporate-documents step, grouped |
| `COMPANY_BENEFICIARIES` | **`companyBeneficiaryDefinitions`** — `[{category, canSkip?, minRequired?, maxAllowed?, individual?, company?}]` *— required* | associated-parties step — the 24 public roles: UBOs, shareholders, directors, representatives, officers, trust / partnership / fund roles, … |
| `E_SIGN` | `esignSettings` (pass-through) | as-is |

Unknown keys in a docSet are passed through to the API verbatim, so escape hatches are easy when you need an obscure field. KYB docSets (`COMPANY_*`) are the exception: the builder emits them completely and rejects unknown keys. On a KYB update, `{"type": "<step>", "keep": true}` copies that step from the current level as it is.

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

These match what the dashboard's own Vue watcher writes when the user first toggles Live capture. **Caveat on PATCH:** `requiredIdDocs.docSets` is replaced whole — every docSet in the PATCH spec must carry the full intended state, since omitted sub-fields are wiped. GET the level first, pass it as `base` (step 6) and copy values you want to preserve into the docSet specs.

### AML / watchlist screening: two separate gates

1. **Tenant gate — `WATCHLISTS` entitlement** (checked in step 0). If `WATCHLISTS` is in `allowedChecks`, AML screening is available and runs **by default** on every level. If it's **not**, screening is off for the whole tenant and **no level setting turns it on** — surface it as a missing entitlement (contact CSM), don't pretend the level enables it.
2. **Level gate — `disableWatchlists`** (only matters when the tenant has `WATCHLISTS`). To turn screening **off for this level**, send the top-level `"disableWatchlists": true`; omit it (or `false`) to keep it on. `watchListCheckSettings.amlCaseType` only selects the *provider* (tenant-gated), and `useCustomWatchListCheckSettings` only picks custom-vs-inherited config — neither is an on/off switch.

So for a policy that *requires* AML screening: confirm `WATCHLISTS` in step 0, then add nothing to the level and GET it back to confirm `disableWatchlists` isn't `true`. For a level that must **skip** AML, set `disableWatchlists: true`. Details: [references/level-schema.md](references/level-schema.md).

### Fraud Prevention checks: client-wide default + per-level override

Five checks run alongside the verification itself and feed risk labels into the applicant's review. They are
configured **client-wide**, with an opt-in override on a single level.

| Check | Flag in `fraudPreventionSettings` | Required entitlement |
|---|---|---|
| Advanced email check | `advancedEmailCheckEnabled` | `EMAIL_RISK_ASSESSMENT` (or legacy `APPLICANT_IDENTIFIERS_INSIGHTS`) |
| Advanced phone check | `advancedPhoneCheckEnabled` | `PHONE_RISK_ASSESSMENT` (or legacy `APPLICANT_IDENTIFIERS_INSIGHTS`) |
| Advanced IP check | `advancedIpCheckEnabled` | `IP_ADDRESS_ANALYSIS` |
| Identity enrichment (digital footprint) | `advancedIdentityEnrichmentEnabled` | `DIGITAL_FOOTPRINT_TARGET` |
| Device intelligence | `deviceIntelligenceEnabled` | `DEVICE_INTELLIGENCE` |

**The client-wide defaults are a dashboard UI setting** (Global Settings → Fraud Prevention). There is no
public-API equivalent, so never promise the user you can change the defaults from here. The same goes for the nine
default actions (the automatic rejections on fraud signals): they are client-wide, Sumsub dashboard UI only. What
this skill can do is the per-level override, through two top-level Level fields:

```json
{
  "id": "<level-id>",
  "useCustomFraudPreventionSettings": true,
  "fraudPreventionSettings": {
    "advancedIpCheckEnabled": false,
    "advancedEmailCheckEnabled": true
  }
}
```

Five rules decide what actually runs, in this order:

1. **`fraudPreventionSettings` is read only when `useCustomFraudPreventionSettings` is `true`.** Without it the
   level inherits the client-wide defaults and the stored object is ignored, silently, with a `200` back. The
   builder refuses that combination rather than letting it land.
2. **Each flag is tri-state.** Omit it to inherit the client-wide default for that one check; `true` / `false`
   pins it for this level. A check with no value anywhere **runs**, so switching one off always means an explicit
   `false`, never leaving it out. "Inherit" does not mean "on": when a tenant is moved to client-wide fraud
   prevention, every client-wide check starts as `false` and every existing level is pinned, so there an omitted flag
   means off. Before you leave a flag out, read the client-wide block with
   `${CLAUDE_SKILL_DIR}/scripts/get_level_fraud_prevention.sh` (no argument) and tell the user what the check will
   inherit.
3. **The entitlement is the outer gate.** No target, no check, whatever the flags say. On every write the server
   nulls the flags whose entitlement the tenant doesn't hold, silently, the same way it downgrades
   `deviceIntelligenceSettings.enabled`. That is why step 7 (GET the level back) is not optional here.
4. **`deviceIntelligenceEnabled` applies to WebSDK 2.0 levels only** (`websdkNext: true`). On a legacy WebSDK 1.0
   level the server nulls the flag on every write, like a flag without its entitlement, so it resolves to off.
5. **Identity enrichment needs the email or the phone check.** `advancedIdentityEnrichmentEnabled` runs only while
   `advancedEmailCheckEnabled` or `advancedPhoneCheckEnabled` runs for the same level, the rule the dashboard
   checkbox has. Switching both off switches identity enrichment off too, whatever its own flag says.

**Changing an existing override: start from the level's current object.** With `base` (step 6) both fields come
through untouched. To change a flag, put the whole `fraudPreventionSettings` object from the GET into the spec with
only the requested keys changed, plus `useCustomFraudPreventionSettings: true`. The spec's object replaces the stored
one, so a key you leave out is erased. Levels of a migrated tenant already have all five checks pinned, so an object
with only the flag the user asked about sends the other four back to the client-wide defaults (off, see rule 2).
To put the level back on the client-wide values, send `useCustomFraudPreventionSettings: false`: a value, because a
PATCH cannot remove a field. The stored object stays but is never read (rule 1).

**Verify against what runs, not against what you sent.** `${CLAUDE_SKILL_DIR}/scripts/get_level_fraud_prevention.sh`
calls `GET /resources/api/agent/globalSettings` (needs the `manageClientSettings` permission on the token). With a
level name (`get_level_fraud_prevention.sh <level name>`, sent as `?applicantLevelName=`) its `fraudPreventionSettings`
is what runs on that level. Without a name it holds the client-wide values, which a level inherits when it has no
`useCustomFraudPreventionSettings`. In both, `true` runs, `false` is switched off, and a check missing from the
object is not available there (no entitlement, or `deviceIntelligenceEnabled` on a WebSDK 1.0 level). An empty
object `{}` means the tenant holds none of the five entitlements, which step 0 already shows. It is the only honest
readback: `fraudPreventionSettings` on the level itself is just the raw override.

**Tenants still on the older model.** If the answer has no `fraudPreventionSettings` key at all, the tenant has not
been moved to client-wide fraud prevention yet. There the checks live on the older per-level fields
`applicantInsightSettings.{advancedEmailCheckEnabled, advancedPhoneCheckEnabled, advancedIpCheckEnabled,
advancedIdentityEnrichmentEnabled}` and `deviceIntelligenceSettings.enabled`, and the two new fields are stored but
never applied. Configure the older fields in that case and tell the user which model their tenant is on. This model
has no client-wide default: a check runs on a level only when its older field is `true` there, so a flag left out
means off. When the user asks for checks to follow the client defaults, say that on this model they will not run on
the level, and offer to switch them on. PATCH
replaces `applicantInsightSettings` and `deviceIntelligenceSettings` whole too, so copy each object from the GET and
change only the requested keys. Check this
before promising a per-level override, not after. On the new model write the new fields. The server still accepts
the older ones there: a change to an older field, with the same check left untouched in `fraudPreventionSettings`,
becomes a pin of that check on the level and sets `useCustomFraudPreventionSettings: true`. On create every older
field in the body counts as a change. So if the GET back shows a pin you did not send, look for an older field in
the body.

See [`examples/fraud-prevention-override.json`](examples/fraud-prevention-override.json) for a complete spec.

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

### Database / non-document verification (KYC)

**Scope: KYC (individual) only.** Company/KYB database checks are not covered via this path.

When the request implies checking applicant data against a **database / registry** rather than (or in addition to) a document — signals: "non-doc", "eKYC", "no document", "against a database/registry", "validate the ID / SSN / DNI number" — resolve and place sources via [`sumsub-check-databases`](../sumsub-check-databases/SKILL.md) **before** building the payload:

1. Run `sumsub-check-databases <country>`. A source is usable when `status == "ENABLED"`; `SANDBOX_ONLY` works in sandbox but will not run in production (say so before building a level the user intends to go live with), and `DISABLED` is not usable at all. If the source the user needs is unavailable, follow that skill's fallback + enablement guidance (don't silently drop it — point the user at [Databases → Available products](https://cockpit.sumsub.com/checkus/sdkIntegrations/databaseServices/available), self-serve for most sources).
2. Each source's `validationReady` / `stepsReady` decides the **placement** — the two signals are independent, check both:

| Signal | docSet | Notes |
|---|---|---|
| `validationReady: true` | keep the document docSet (e.g. `IDENTITY`, `types` stays) | Source cross-checks the uploaded document's data against the database. Attach at the level's **top-level** `checkSourceSettings` (a sibling of `requiredIdDocs`, not nested inside it or inside the docSet). |
| `stepsReady` contains a type **on its own** (e.g. `E_KYC`) | standalone docSet of that type, no `types` field | Database-only, no upload. `E_KYC` requires `E_KYC_TARGET`. Nest `checkSourceSettings` **inside this docSet**. |
| `stepsReady` contains a type **alongside** an already-required doc step (e.g. `IDENTITY`) | keep that docSet's `types` | Applicant chooses document upload **or** the database check in the same step. Also requires `E_KYC_TARGET`. Nest `checkSourceSettings` **inside that same docSet**, not at the top level. |

If `stepsReady` lists more than one step type for a source, that's a menu of valid homes, not a mandate to use all of them — pick the one that matches the user's intent.

3. Attach the chosen source(s) via `checkSourceSettings.countrySettings[]` — **either** at the level's top level (a `checkSourceSettings` key sibling to `requiredIdDocs`, for `validationReady` placements) **or** nested inside the relevant docSet (for `stepsReady` placements):

```json
"checkSourceSettings": {
  "countrySettings": [
    {
      "country": "ARG",
      "checkType": "E_KYC_CHECK",
      "groupType": "INPUT_COUNTRY",
      "executionConfigurations": [
        {"sourceId": "arg_gov_dni", "fallbackReasons": []}
      ]
    }
  ]
}
```

- `country`, `checkType`, and `sourceId` come straight from the check-databases response.
- `groupType`: use `INPUT_COUNTRY` (the applicant's country) — the default. `TARGET_COUNTRY` is only for the rare cross-border source (e.g. a visa check).
- `executionConfigurations` is **ordered** — list multiple `sourceId`s to fall back in sequence. `fallbackReasons` (e.g. `NAME_MISMATCH`, `DATA_NOT_FOUND`) triggers the fallback to the next source; `[]` = no fallback.

See the three placements worked end-to-end in [`examples/identity-selfie-with-database-validation.json`](examples/identity-selfie-with-database-validation.json) (top-level, `validationReady`), [`examples/identity-with-non-doc-selfie.json`](examples/identity-with-non-doc-selfie.json) (nested in `IDENTITY`), and [`examples/non-doc.json`](examples/non-doc.json) (standalone `E_KYC`).

Field meanings, enum values, and the unavailable-source handling live in [`sumsub-check-databases`](../sumsub-check-databases/SKILL.md) + its [schema reference](../sumsub-check-databases/references/checksources-schema.md).

### KYB (company) levels

A KYB level is a `company` level built from the three WebSDK 2.0 KYB steps: company information (`COMPANY_DATA`, the first step of a new level), corporate documents (`COMPANY_DOCUMENTS`) and associated parties (`COMPANY_BENEFICIARIES`), plus a KYB check mode. Full rules, enums and defaults: [references/kyb.md](references/kyb.md).

```json
{
  "name": "KYB Standard",
  "applicantType": "company",
  "kybType": "autoAndManual",
  "kybSettings": {"uboThreshold": 25, "shareholderThreshold": 25},
  "docSets": [
    {"type": "COMPANY_DATA"},
    {"type": "COMPANY_DOCUMENTS", "companyDocsGroupDefinitions": [{"label": "legalPresence"}]},
    {"type": "COMPANY_BENEFICIARIES", "companyBeneficiaryDefinitions": [
      {"category": "ubos", "individual": {"levelName": "Basic KYC"}},
      {"category": "directors", "individual": {"levelName": "Basic KYC"}}
    ]}
  ]
}
```

Before building a KYB level:

1. **Pick `kybType` from the entitlements** fetched in step 0 — it is required on create:
   - `autoAndManual` (Full KYB) needs `KYB_FULL` or `COMPANY`;
   - `auto` (Registry and AML Check) needs one of those or `KYB_AUTO_AML_AND_REGISTRY`;
   - `amlOnly` (AML Check) needs any of the above, `KYB_AUTO_AML_ONLY` or `KYB_APPLICANTS` (data collection only — next sentence).

   Company applicants can't be created on a level whose mode the tenant doesn't have, so check it here. A tenant with only `KYB_APPLICANTS` can collect company data but not check it: use `kybType: amlOnly` with `disableWatchlists: true`. A tenant with no KYB entitlement at all → stop, as in [Tenant entitlements](#tenant-entitlements).
2. **Resolve a verification level for every party that must be verified.** `levelName` must name an existing standalone level of the matching applicant type: an `individual` level for `individual` parties, a `company` level for `company` parties. Pick it from the level list (step 1). If none fits, create it first with this skill (for example `IDENTITY` + `SELFIE`), then reference its `name`. Omit `levelName` only when the user wants the party's data collected without verification. If the user didn't say which roles must be verified, ask — never invent a level name. Build with `--levels levels.out` (the list from step 1): the builder then refuses a `levelName` that doesn't exist or is of the wrong type. `post_level.sh` / `patch_level.sh` check it again against a fresh list.
3. **Tell the user** when `kybType` is `auto` or `amlOnly` and the level has `COMPANY_DOCUMENTS`: those documents are collected but not verified. Pass on every `note:` line the builder prints — for example, `companyOfficers` and `investors` are for internal use only (Sumsub does not verify them), and with `canSkip` on both `ubos` and `shareholders` the applicant can skip only one of them.

The builder enforces the rest: a new company level starts with `COMPANY_DATA` (an update keeps the level's current order); a company level may add only `EMAIL_VERIFICATION`, `PHONE_VERIFICATION`, `PAYMENT_METHODS` and `QUESTIONNAIRE*`; each role takes the party kinds and fields the dashboard allows ([role matrix](references/kyb.md#company_beneficiaries--associated-parties)). It rejects what this iteration doesn't support — the legacy `COMPANY` step, building `COMPANY_ADDRESSES`, the `accountUsers` role, company parties for `ubos` / `representatives`, primary-contact settings — so point the user to the Sumsub dashboard for those. It also refuses the name `company-zero`: that is Sumsub's reserved default company level — never create or modify it.

#### Updating a KYB level

A KYB update sends `requiredIdDocs` (and, with a new `kybType`, `autoCheckGeneratorSettings`), and PATCH replaces a nested object it gets as a whole. So the update is the current level with the change laid over it — never a body built from the spec alone, which would drop every step and setting the spec doesn't carry (primary contact, regulation questions, `COMPANY_ADDRESSES`, …):

1. **GET** the level and save the output: `${CLAUDE_SKILL_DIR}/scripts/get_level.sh <id> > get.out` — the last line must be `HTTP 200`.
2. **Write the spec**: `id`, `docSets`, and only the settings the user asked to change. List **every** step, in order. A step you don't change is `{"type": "<step>", "keep": true}` — copied from the current level as it is, including steps the builder can't build (`COMPANY_ADDRESSES`, unsupported document subtypes). A step you change is spelled out in full: copy its current content from the GET, then edit it. A step you leave out is deleted.
3. **Build**: `python3 ${CLAUDE_SKILL_DIR}/scripts/build_level.py --base get.out --levels levels.out < spec.json > payload.json`. The spec's `kybType` / `kybSettings` keys are laid over the current ones; every other field comes from the GET (the server-populated ones are dropped). The GET body as the spec's `base` works the same way. Read the `note:` lines — a removed step you didn't mean to remove means the spec is missing it. The builder refuses a copy of another account's level (read-only — change the source level) and a WebSDK 1.0 level (edited in the Sumsub dashboard) — see [kyb.md](references/kyb.md#updating-a-kyb-level---base).
4. **Show what changes** and get explicit confirmation: `diff <(sed '$d' get.out | python3 -m json.tool --sort-keys) <(python3 -m json.tool --sort-keys payload.json)`. Show every `note:` line with it.
5. **PATCH** `payload.json` unchanged, then GET the level back and compare (step 7 of the [Procedure](#procedure)). `patch_level.sh` reads the level first and refuses the PATCH (exit 4) when the level is WebSDK 1.0 or the payload isn't what `build_level.py --base` builds from it.

```json
{
  "id": "686f1c2a4b9d8e0012349101",
  "docSets": [
    {"type": "COMPANY_DATA", "keep": true},
    {"type": "COMPANY_ADDRESSES", "keep": true},
    {"type": "COMPANY_DOCUMENTS", "keep": true},
    {"type": "COMPANY_BENEFICIARIES", "companyBeneficiaryDefinitions": [
      {"category": "ubos", "individual": {"enabled": true, "levelName": "Standard KYC", "fields": [
        {"name": "firstName", "required": true, "prefill": true},
        {"name": "lastName", "required": true, "prefill": true},
        {"name": "email", "required": true, "prefill": false},
        {"name": "shareSize", "required": true, "prefill": true}
      ]}},
      {"category": "directors", "individual": {"levelName": "Standard KYC"}}
    ]}
  ]
}
```

The builder rejects a company spec with an `id` but no `--base`, an `id` that isn't the `--base` level, and a rename (the API keeps the name). The API may refuse to edit a level that many applicants used recently (409) — edit that level in the dashboard.

### Chaining with other Sumsub-* skills

This skill's `QUESTIONNAIRE` and `PROOF_OF_RESIDENCE` doc-sets accept ids produced by sibling skills, so a 3-step build-everything-from-scratch flow is natural:

| First run … | Pass the returned `id` as … |
|---|---|
| `sumsub-create-questionnaire` | `docSets[].questionnaireDefId` on a `QUESTIONNAIRE` doc-set |
| `sumsub-create-poa-preset` | `docSets[].poaPresetId` on a `PROOF_OF_RESIDENCE` doc-set |

See [`examples/with-presets.json`](examples/with-presets.json) for an end-to-end level that references both.

For **database / non-document** verification, run [`sumsub-check-databases`](../sumsub-check-databases/SKILL.md) to resolve sources and attach them via `checkSourceSettings` — see [Database / non-document verification](#database--non-document-verification-kyc) above.

## Outputs

On success, lead with the human-readable info:
- `name`, `applicantType`, ordered list of `docSets[].idDocSetType`.
- **Dashboard link**: `https://cockpit.sumsub.com/checkus/sdkIntegrations/levels/<applicantType>Level/<id>?clientId=<clientId>&sbx=true`. Render as a clickable markdown link. The `<applicantType>Level` segment is `individualLevel` for individuals or `companyLevel` for companies. All three fields (`id`, `applicantType`, `clientId`) come from the POST response body; `sbx=true` targets the Sandbox workspace.
- Finally, on its own line: `Level ID (for SDK access tokens / future PATCH): <id>`.

On failure: HTTP status + the `description`/`errorName` from Sumsub's error envelope.

## Worked examples

- [`examples/identity-selfie.json`](examples/identity-selfie.json) — the most common pattern.
- [`examples/identity-live-capture.json`](examples/identity-live-capture.json) — IDENTITY-only with Live capture + all docapture sub-options + NFC.
- [`examples/questionnaire-only.json`](examples/questionnaire-only.json) — pure data-collection level (like the SOF level in this repo).
- [`examples/full-kyc.json`](examples/full-kyc.json) — `APPLICANT_DATA + IDENTITY + SELFIE + PROOF_OF_RESIDENCE + QUESTIONNAIRE`.
- [`examples/kyb-company.json`](examples/kyb-company.json) — KYB level: company data, two document groups, UBOs and directors verified by a KYC level, shareholders collected without verification.
- [`examples/with-presets.json`](examples/with-presets.json) — references both a questionnaire (`questionnaireDefId`) and a POA preset (`poaPresetId`) returned by sibling skills.
- [`examples/payment-methods.json`](examples/payment-methods.json) — payment method action level with bank card, bank account, crypto wallet, and e-wallet.
- [`examples/fraud-prevention-override.json`](examples/fraud-prevention-override.json) — per-level Fraud Prevention override (one check off, one pinned on, the rest inherited).
- [`examples/identity-selfie-with-database-validation.json`](examples/identity-selfie-with-database-validation.json) — database validation (`validationReady`): document upload stays, source cross-checks it via top-level `checkSourceSettings`.
- [`examples/identity-with-non-doc-selfie.json`](examples/identity-with-non-doc-selfie.json) — non-doc in an existing step (`stepsReady`): `checkSourceSettings` nested inside `IDENTITY`, applicant can upload or use the database check.
- [`examples/non-doc.json`](examples/non-doc.json) — standalone non-doc (`stepsReady`): dedicated `E_KYC` docSet, no document upload.

## See also

- [references/level-schema.md](references/level-schema.md) — full `ApplicantLevel` schema, all enum values, gotchas.
- [references/kyb.md](references/kyb.md) — KYB (company) levels: steps, check modes, thresholds, associated parties, what is not supported yet.