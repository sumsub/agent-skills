---
name: sumsub-create-poa-preset
description: Create or update a Sumsub Proof-of-Address (POA) preset. POST `/resources/api/agent/poaStepSettings` to create new, PATCH same path to update (id in body), GET `/resources/api/agent/poaStepSettings/{id}` to read one back. TRIGGER when the user asks to "create / add / build / configure / update / edit a POA preset" or "PoA step settings", configure which proof-of-address document types are accepted (utility bills, bank statements, tax bills, etc.), set validity periods per provider type, enable POI-as-POA (accept identity doc as proof of address), tune the cross-validator (name/address fuzzy match between POI and POA), or add per-country POA overrides. SKIP for attaching a preset to a level (set `poaStepSettingsId` on the level instead, via `sumsub-create-level`), or for non-POA presets (cross-check presets, permission presets, etc.).
allowed-tools: Read, Write, Bash
---

# Sumsub — Create POA Preset

Builds a POA preset JSON payload from a compact spec, POSTs it to the Sumsub API, and reports the resulting preset `id` so it can be attached to one or more levels via `level.requiredIdDocs.docSets[].poaStepSettingsId`.

> **Prerequisite — level must have a PROOF_OF_RESIDENCE step.** A POA preset has no effect unless it is attached to a `PROOF_OF_RESIDENCE` (or `PROOF_OF_RESIDENCE2`/`3`/`4`) docset in at least one level. If the user hasn't created (or described) a level that includes a POA step, surface this before building the preset — there is no point creating it in isolation.

## Endpoints

| Method | Path | When |
|---|---|---|
| `POST` | `/resources/api/agent/poaStepSettings` | Create a new preset. Body MUST NOT include `id` — server assigns it. |
| `PATCH` | `/resources/api/agent/poaStepSettings` | Update an existing preset. Body MUST include `id` (the field, not in the URL). |
| `GET` | `/resources/api/agent/poaStepSettings/{id}` | Read one preset back — used to verify what landed and to resolve `name` from a known `id`. |

All three require permission `manageClientSettings`. Body shape is the
[POA preset schema](references/poa-preset-schema.md) — client-settable
fields only (`clientId`, `createdAt`, `createdBy`, `modifiedAt`, audit
trail are server-managed and echoed back on the response).

After creation, attach by editing a level: `requiredIdDocs.docSets[].poaStepSettingsId = "<the new id>"` on any `PROOF_OF_RESIDENCE` doc-set.

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

## Tenant entitlements

POA preset creation has historically been gated behind the `POA` entitlement, but **in practice the API accepts the write for most tenants regardless** — the entitlement is often baseline, covered by other keys, or simply not surfaced in `allowedChecks`. Don't treat its absence as a blocker.

1. Invoke `sumsub-check-permissions` and inspect `allowedChecks` — informational, for diagnostics.
2. **If `POA` is present** — proceed.
3. **If `POA` is missing** — proceed anyway, with a one-line user-visible note that the documented entitlement isn't listed (so they know what to mention to support if the POST eventually fails). Do NOT pause for confirmation — Sumsub will reject the write itself if the tenant truly lacks the right, and the 4xx from that will be more informative than a pre-emptive halt.
4. **If the POST returns a 4xx that mentions an entitlement** — surface the error body verbatim and suggest contacting CSM / Sumsub support.

## Procedure

0. **Fetch tenant entitlements** — see section above.
1. **Translate the user's intent into the compact spec** (below). Most users describe presets in terms of "what we accept" (bank statements, utility bills) and "for how long" (validity in months) — map that into `providers` keys, `subTypes`, and `validMonths`.
2. **Validate**: name non-empty; `includedCountries` and `excludedCountries` aren't both set; every provider key is a `PoaCompanyContactType`; every `subTypes` entry is a `PoaSubType`; every country code is ISO-3166-1 alpha-3 uppercase; `crossValidator.fuzzyThreshold` in `[0, 1]`.
3. **Generate payload** via `${CLAUDE_SKILL_DIR}/scripts/build_poa_preset.py` (compact spec on stdin → full payload on stdout).
4. **Create vs. update**:
   - **New preset** — POST via `${CLAUDE_SKILL_DIR}/scripts/post_poa_preset.sh`. The payload must **not** carry `id`.
   - **Update existing** — first GET the current state via `${CLAUDE_SKILL_DIR}/scripts/get_poa_preset.sh` so the user sees the diff, then PATCH via `${CLAUDE_SKILL_DIR}/scripts/patch_poa_preset.sh`. The payload must include the preset's `id`.
5. **Build the dashboard link.** Read `id` and `clientId` from the response body and format:

   ```
   https://cockpit.sumsub.com/checkus/sdkIntegrations/globalSettings/userVerification/proofOfAddress/<id>?clientId=<clientId>&sbx=true
   ```

   The `sbx=true` query param targets the **Sandbox** workspace — it is the canonical sandbox link param shared across all skills.
6. **Report** — lead with the human-readable name; surface the id only at the end as the value to pass into the next API call:
   - **Name** and country scope (incl/excl) + per-country override countries.
   - A brief summary of what's accepted (provider types covered, default validity).
   - **Dashboard link** as a clickable markdown link.
   - Final line: `Preset ID for level wiring: <id>`.

## Compact spec format (JSON or YAML on stdin)

```yaml
name: "Standard POA (6 months)"
desc: "Default Proof of Address rules with 6-month validity"

# Country scope — choose AT MOST ONE
# includedCountries: [GBR, DEU, FRA]    # allow-list
excludedCountries: [PRK, IRN]            # block-list

# Global defaults
settings:
  acceptMultiplePages: true
  acceptDocScreenshot: true
  requireCountryMatch: false             # require POI country == POA country
  useIssueDateForExpiry: false           # use only issueDate (ignore expiry) for "fresh enough" check
  validMonths: 6                         # shortcut: applied to every provider that omits its own validMonths
  addressTypes: [dwelling, poBox]        # allowed PoA address types
  acceptableLanguages: [en, de, fr]

  # Document providers and the doc sub-types each may produce
  # Keys (PoaCompanyContactType): bank | utilityProvider | governmentOrganization | mobileOperator | other
  providers:
    bank:
      validMonths: 6
      acceptUnconventional: true         # accept non-mainstream banks (with allowedOrgNames below)
      subTypes: [bankStatement, bankLetter, other]
      allowedOrgs:                       # only used when acceptUnconventional=true
        names:    ["Some Local Co-op Bank"]
        websites: ["coopbank.example"]
      forbiddenDocumentNames: []
      forbiddenOrgNames:    []
      forbiddenOrgWebsites: []
    utilityProvider:
      subTypes: [telecom, utilityBill, other]
    governmentOrganization:
      subTypes: [statement, voterRegistration, taxBill, other]
    mobileOperator: {}                   # accept defaults
    other:
      subTypes: [lease, other, universityLetter]

  # Accept identity document as proof of address
  poiAsPoa:
    enabled: true                        # acceptPoiAsPoa
    sameDoc:  true                       # acceptSamePoiAsPoa (same doc for POI + POA)
    validMonths: 3
    allowedTypes: [PASSPORT, ID_CARD, RESIDENCE_PERMIT, DRIVERS]

  # Name/address comparison between POI and POA
  crossValidator:
    nameMode:    weakContainment         # strict | weakContainment | def | ai | fuzzy | containment | fuzzyContainment
    addressMode: fuzzy                   # strict | fuzzy
    fuzzyThreshold: 0.75
    ignoreMiddleName: false
    ignoreFixedInfo: false

# Per-country overrides — same shape as `settings`. Only the keys you set are overridden;
# others fall through to the global `settings`.
byCountry:
  BRA:
    validMonths: 3                       # tighter validity for Brazil
    providers:
      bank:
        validMonths: 3
```

### Provider-type values (`providers.<key>`)

`bank`, `utilityProvider`, `governmentOrganization`, `mobileOperator`, `other`.

### Sub-types (`providers.<key>.subTypes[]`)

`statement`, `voterRegistration`, `taxBill`, `telecom`, `utilityBill`, `bankStatement`, `bankLetter`, `lease`, `universityLetter`, `employmentLetter`, `other`.

### Address types (`addressTypes[]`)

`dwelling`, `poBox`, `poBoxSpecialCountries`.

### POI-as-POA `allowedTypes[]`

Standard `IdDocType` values: `PASSPORT`, `ID_CARD`, `RESIDENCE_PERMIT`, `DRIVERS` (others rare).

### Name comparison modes (`crossValidator.nameMode`)

`strict`, `weakContainment`, `def`, `ai`, `fuzzy`, `containment`, `fuzzyContainment`.

### Address comparison modes (`crossValidator.addressMode`)

`strict`, `fuzzy`.

## Outputs

On success, lead with the human-readable info:
- `name`, country scope, list of per-country override countries.
- A brief summary (provider types covered, default validity).
- **Dashboard link**: `https://cockpit.sumsub.com/checkus/sdkIntegrations/globalSettings/userVerification/proofOfAddress/<id>?clientId=<clientId>&sbx=true`. Render as a clickable markdown link. Both `id` and `clientId` come from the POST response body; `sbx=true` targets the Sandbox workspace.
- Finally, on its own line: `Preset ID (for level wiring / future PATCH): <id>`.

On failure: HTTP status + Sumsub's `description`/`errorName`. The builder rejects invalid enums / impossible combinations upfront with precise messages.

### Names, not ids, in user-facing messages

This applies to **every** message about the preset — pre-POST summary, mid-flow status updates, hand-off lines — not only the final report:

- Refer to the preset by `name` ("POA — 60 days"), not by its `id`, in prose.
- The `id` belongs only on the final dedicated line (`Preset ID for level wiring: <id>`) — that line is the one place a raw id is correct, because the user needs to copy it into a level's `poaPresetId`.
- When the caller is the level skill chaining this preset into a `PROOF_OF_RESIDENCE` step, the level skill should ALSO refer to this preset by name in its pre-POST summary — see [`sumsub-create-level`](../sumsub-create-level/SKILL.md#names-not-ids-in-user-facing-messages).

### Hand-off to `sumsub-create-level`

The returned `id` is what you pass to a level's `PROOF_OF_RESIDENCE` doc-set. The level skill exposes it as a friendly `poaPresetId` shortcut (or the canonical `poaStepSettingsId`):

```json
{
  "type": "PROOF_OF_RESIDENCE",
  "docTypes": ["UTILITY_BILL", "BANK_STATEMENT"],
  "poaPresetId": "<id from this skill>"
}
```

See [`sumsub-create-level/examples/with-presets.json`](../sumsub-create-level/examples/with-presets.json).

## Worked examples

- [`examples/minimal.json`](examples/minimal.json) — bare-minimum preset: 6-month bank/utility/gov defaults, POI-as-POA off.
- [`examples/eu-bank-friendly.json`](examples/eu-bank-friendly.json) — EU-only preset, generous bank-statement validity, POI-as-POA allowed for 3 months.
- [`examples/per-country-tight.json`](examples/per-country-tight.json) — global defaults plus a tighter Brazil override.

## See also

- [references/poa-preset-schema.md](references/poa-preset-schema.md) — full `PoaStepSettings` schema, every enum, and gotchas.
