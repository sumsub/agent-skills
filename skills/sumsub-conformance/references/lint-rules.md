# Linter rule catalog

`lint_config.py` runs these against a resolved config graph (`resolve_graph.sh` output) — tenant
entitlements (`allowedChecks` keys) are read straight from that graph. Every rule traces back to a
hard-won constraint in the repo `CLAUDE.md` or the level / PoA schema references.

Severities: **error** (config is broken or will silently no-op) · **warn** (likely wrong, or
risk to approval rate) · **info** (advisory) · **unknown** (entitlement-dependent, but
entitlements could not be fetched — re-run with `sumsub-check-permissions`).

> **This table and the data below are generated from [`rules.json`](rules.json).** Do not edit
> them by hand — run `python3 scripts/gen_lint_docs.py`. `test_lint.py` fails if they drift.

<!-- GEN:rules -->
| Rule | Severity | Detection | Fix |
|---|---|---|---|
| `docset-entitlement-mismatch` | error / unknown | A docSet whose idDocSetType needs an entitlement absent from the tenant's allowedChecks | Enable the entitlement (CSM) or drop the step. Unknown when entitlements could not be fetched. |
| `device-intelligence-no-entitlement` | error / unknown | deviceIntelligenceSettings.enabled:true without DEVICE_INTELLIGENCE (a bare DEVICE_CHECK step is covered by docset-entitlement-mismatch) | Enable DEVICE_INTELLIGENCE, then GET the level back to confirm it stuck — otherwise the API silently stores enabled:false. |
| `aml-provider-invalid` | error | watchListCheckSettings.amlCaseType not in the valid provider set | Use a valid provider or omit amlCaseType to inherit the tenant default. |
| `aml-custom-watchlist-gated` | warn | useCustomWatchListCheckSettings:true or any amlCaseType set | Confirm the tenant is provisioned, or set useCustomWatchListCheckSettings:false and omit amlCaseType. |
| `poa-preset-missing` | error | PROOF_OF_RESIDENCE* step with no poaStepSettingsId | Create a PoA preset and wire its id into poaStepSettingsId — the server rejects the level otherwise. |
| `poa-preset-unresolved` | error | poaStepSettingsId points at an id that did not resolve | Point poaStepSettingsId at an existing PoA preset in this tenant. |
| `questionnaire-missing` | error | QUESTIONNAIRE* step with no questionnaireDefId | Create a questionnaire and wire its id into questionnaireDefId. |
| `questionnaire-unresolved` | error | questionnaireDefId GET 404s | Point questionnaireDefId at an existing questionnaire in this tenant. |
| `selfie-no-liveness` | warn | SELFIE* step with no videoRequired | Set videoRequired (default passiveLiveness; photoRequired to skip liveness deliberately). |
| `selfie-deprecated-liveness` | warn | SELFIE videoRequired in the discouraged set | Use passiveLiveness (default), or photoRequired to intentionally skip liveness. |
| `duplicate-docset-type` | error | Any idDocSetType appears more than once | Keep one, or use the numbered variant (e.g. IDENTITY2) — a distinct type string. |
| `poa-allowed-types-bad-keys` | error | PoA allowedTypesSettings keys outside the provider-category set | Keys must be provider categories, not document sub-types. |
| `legacy-websdk` | warn | websdkNext is not true | Set websdkNext:true. |
| `workflow-high-risk-no-pep-aml` | info | Workflow routes on country/risk but has no PEP/AML/watchlist branch (substring heuristic) | Confirm high-risk applicants get enhanced screening (PEP/AML) somewhere in the flow. |
<!-- /GEN:rules -->

## Reference data

<!-- GEN:lookups -->
- **Valid AML providers** (`amlCaseType`): `caSearch`, `wcCase`, `djAssociation`, `quantifindSearch`, `amlwSearch`, `caMeshSearch`.
- **Valid PoA `allowedTypesSettings` keys**: `governmentOrganization`, `utilityProvider`, `bank`, `mobileOperator`, `other`.
- **Discouraged SELFIE `videoRequired`**: `liveness`, `optional`, `disabled` (default is `passiveLiveness`).
- **docSet → entitlement** (any one satisfies the step):
    - `PROOF_OF_RESIDENCE` → `POA`
    - `PROOF_OF_RESIDENCE2` → `POA`
    - `QUESTIONNAIRE` → `QUESTIONNAIRE`
    - `QUESTIONNAIRE2` → `QUESTIONNAIRE`
    - `QUESTIONNAIRE3` → `QUESTIONNAIRE`
    - `QUESTIONNAIRE4` → `QUESTIONNAIRE`
    - `E_KYC` → `E_KYC_TARGET`
    - `E_SIGN` → `E_SIGN_TARGET`
    - `DEVICE_CHECK` → `DEVICE_INTELLIGENCE`
    - `PAYMENT_METHODS` → `PAYMENT_SOURCE` | `PAYMENT_METHOD` | `PAYMENT_METHOD_CRYPTO` | `KYT_UNHOSTED_WALLET_VERIFICATION`
    - `COMPANY` → `COMPANY` | `KYB_FULL` | `KYB_AUTO_AML_AND_REGISTRY` | `KYB_AUTO_AML_ONLY`
    - `COMPANY_DATA` → `COMPANY` | `KYB_FULL` | `KYB_AUTO_AML_AND_REGISTRY` | `KYB_AUTO_AML_ONLY` | `KYB_APPLICANTS`
    - `TR_RECIPIENT_INFORMATION` → `TRAVEL_RULE`
    - `INVESTABILITY` → `PROOF_OF_FUNDS`
    - `SOLANA_ATTESTATION` → `PAYMENT_METHOD_CRYPTO`
    - `LINEA_ATTESTATION` → `PAYMENT_METHOD_CRYPTO`
    - `CHAINLINK_ATTESTATION` → `PAYMENT_METHOD_CRYPTO`
<!-- /GEN:lookups -->

### Notes (hand-written)

- **Duplicate docSets**: no type is exempt — any exact-type repeat is rejected. Additional captures
  use a distinct numbered type (`IDENTITY2`, `QUESTIONNAIRE2`…), which is a different string and
  never collides.
- **`captureParams` is deliberately NOT linted.** It is `@Transient` and the server derives it on
  every read, so it is present on every read-back — flagging it would false-positive on healthy levels.
- **Entitlements input** may be fed as the raw `check_permissions.sh` output; `lint_config.py` reads
  the `allowedChecks` keys and tolerates the trailing `HTTP <code>` line.
- The docSet → entitlement map mirrors the entitlement table in `create-new-skill`.

## Adding a rule

**Data-only change** (new AML provider, entitlement, discouraged value, docSet→entitlement):
edit the relevant list in [`rules.json`](rules.json) → `lookups`, then
`python3 scripts/gen_lint_docs.py`. No code change needed.

**A whole new rule:**
1. Add its entry (severity, detection, fix) to [`rules.json`](rules.json) → `rules`.
2. Add the detection logic in `lint_config.py` (`lint()` appends `finding("<id>", entity, msg)`;
   severity/fix come from the registry — pass them explicitly only for dynamic cases). An
   unregistered rule id raises at runtime, so step 1 is enforced.
3. Run `python3 scripts/gen_lint_docs.py` to refresh this file.
4. Extend `examples/audit-input-dirty.json` so the rule fires and add its id to the `expected`
   set in `scripts/test_lint.py`. Run `python3 scripts/test_lint.py` — must stay green.
