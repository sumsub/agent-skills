---
name: sumsub-check-permissions
description: Fetch the current tenant's allowed entitlements (BackgroundCheckTarget list). Returns JSON `{"allowedChecks":{key:label}}` — a map whose keys are the enabled entitlement keys. Called by sumsub-create-level (and other create-* skills) before building a payload to gate entitlement-required features.
allowed-tools: Bash
user-invocable: false
---

# Check Permissions

Returns the tenant's allowed entitlements so callers can gate features before making any API writes.

## Usage

Run the script and parse the result:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/check_permissions.sh
```

Output: raw Sumsub response body followed by `HTTP <code>`.

Success (HTTP 200):
```json
{"allowedChecks": {"REUSABLE_KYC_SDK": "Reusable KYC via API/SDK: ...", "VIDEO_IDENT": "Video Identification: ..."}}
HTTP 200
```

Error (non-200):
```json
{"description":"Unauthorized","errorName":"...","correlationId":"..."}
HTTP 401
```

- `allowedChecks` — map of permission key → human-readable label for all entitlements enabled for this tenant.
- Permission keys present as keys of `allowedChecks` are the allowed entitlements.

## How callers should use this

If the HTTP status is not 200, **stop immediately** — show the error body to the user and do not proceed.

After a successful response, check whether the required `BackgroundCheckTarget` key is present in `allowedChecks`. If it is not, **stop immediately** — do not build or POST the payload. Tell the user which entitlement is missing and that they need to contact their CSM or Sumsub Support to get it enabled.

Entitlement → feature mapping (key examples):

| Feature | Required entitlement |
|---|---|
| `E_KYC` docset | `E_KYC_TARGET` |
| `PROOF_OF_RESIDENCE` docset | `POA` |
| `E_SIGN` docset | `E_SIGN_TARGET` |
| `deviceIntelligenceSettings.enabled: true` | `DEVICE_INTELLIGENCE` |
| `QUESTIONNAIRE` scoring | `QUESTIONNAIRE_SCORING` |
| `QUESTIONNAIRE` attachments | `QUESTIONNAIRE_ATTACHMENT` |
| NFC chip reading | `NFC` |
| Video ident sessions | `VIDEO_IDENT` |
| Reusable KYC via SDK | `REUSABLE_KYC_SDK` |
| Known face search | `KNOWN_FACE_SEARCH` |
| AML / watchlist step | `WATCHLISTS` |
