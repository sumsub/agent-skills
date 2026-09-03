---
name: sumsub-create-transaction
description: Submit a transaction to Sumsub Transaction Monitoring (KYT) via the ApplicantResource API. TRIGGER when the user asks to "submit / create / send / record a transaction", "test a KYT rule with a transaction", post a fiat or crypto payment for monitoring, attach Travel Rule data to a transfer, log a user-platform event (signup / login / password-reset / 2FA-reset) for monitoring, or submit a transaction for an applicant that does not exist yet (the request creates them). SKIP for editing arbitrary fields on an existing transaction, for bulk import (`/kyt/misc/txns/import`), for fetching / approving / rejecting transactions, for KYT rule management, or for Travel Rule data-exchange flows that are not transaction creation.
allowed-tools: Read, Write, Bash
---

# Sumsub — Create Transaction (KYT)

Builds a `KytTxnData` JSON payload from a compact spec, POSTs it to the Sumsub KYT endpoint, and reports the resulting `txnId` / `score` / `reviewAnswer`.

## Endpoint

Two variants, picked automatically by the post script:

| Case | Method + Path |
|---|---|
| Applicant exists | `POST https://api.sumsub.com/resources/applicants/{applicantId}/kyt/txns/-/data` |
| Applicant does **not** exist (Sumsub creates one from `applicant.externalUserId`) | `POST https://api.sumsub.com/resources/applicants/-/kyt/txns/-/data?levelName=<levelName>` |

Body: [`KytTxnData`](references/transaction-schema.md). Returns the persisted `KytTxn` with monitoring scores attached.

Both endpoints are marked deprecated, but they remain the canonical "submit transaction" entry points in the [official docs](https://docs.sumsub.com/reference/submit-transaction-for-existing-applicant.md). No v2/v3 replacement exists.

## Auth — App Token + secret (sandbox only)

This skill talks to the public Sumsub API and signs each request per
[the authentication reference](https://docs.sumsub.com/reference/authentication).
The full how-it-works writeup lives in the [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md)
skill — read it if you hit `401 Invalid signature`.

> **⚠️ Sandbox tokens only.** Do **not** accept or use a production App Token
> here — transaction monitoring acts on real applicant data and can fire
> real KYT alerts. If the user offers a prod token, refuse and ask them to
> generate a sandbox pair at <https://cockpit.sumsub.com/checkus/home?sbx=true>
> (**Connect Sumsub to your AI agent** -> **Build & configure** ->
> **Generate token**). Token + secret are shown once — copy both before
> closing the dialog. The helper
> script enforces this — it rejects tokens that don't start with `sbx:`.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

### Signing the resolved path

This is the one routing wrinkle — the path **with query string** must be
signed. The post script handles it: it reads the sidecar route file the
builder emits, picks the URI (`/resources/applicants/{id}/…` or
`/resources/applicants/-/…?levelName=…`), URL-encodes the dynamic segments,
and signs the same bytes it sends. If you bypass the script, remember:

- Sign the path you put on the wire — encoded form, query string included.
- Body bytes signed must equal the bytes sent (no whitespace re-flow).

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

## Procedure

1. **Map the user's intent** to the compact spec below. The vast majority of transactions are `type: finance` (a payment) — for those, the user is really telling you *amount + currency + direction + applicant + counterparty*.
2. **Validate**: `txnId` non-empty, `applicant.externalUserId` non-empty, and per `type`:
   - `finance` / `travelRule` → `info.amount`, `info.currencyCode`, `info.direction` required (the OpenAPI marks all three required on `KytTxnInfo`).
   - `userPlatformEvent` → `userPlatformEvent.type` required.
   - Enums (`direction`, `currencyType`, `applicant.type`, `nameType`, etc.) checked upfront with full allowed-values list on failure.
3. **Generate** the full payload with `${CLAUDE_SKILL_DIR}/scripts/build_transaction.py` (compact spec on stdin → full `KytTxnData` payload on stdout).
4. **POST** via `${CLAUDE_SKILL_DIR}/scripts/post_transaction.sh` — auto-routes to existing-applicant vs non-existing-applicant URL based on whether `_applicantId` was set in the *spec* (NOT in the payload — see below).
5. **Build the dashboard link.** Read `id` (the **server-assigned identifier**, not the `txnId` you supplied) and `clientId` from the response body and format:

   ```
   https://cockpit.sumsub.com/checkus/kyt/txns/<id>?clientId=<clientId>&sbx=true
   ```

   The user-supplied `txnId` in the spec (e.g. `finance-2026-05-21-0001`) is **not** what goes in the URL — Sumsub assigns a separate identifier on persistence. The `sbx=true` query param targets the **Sandbox** workspace — it is the canonical sandbox link param shared across all skills.
6. **Report**: `txnId` (yours), the server `id`, applicant `externalUserId`, direction + amount + currency, counterparty (if any), the response's `score` / `reviewAnswer` / `riskLabels` if present, and the **dashboard link as a clickable markdown link**.

## Compact spec format (JSON or YAML on stdin)

```yaml
# Top-level
txnId: "finance-2026-05-21-0001"     # REQUIRED, unique alphanumeric in your system
txnDate: "2026-05-21 14:30:00+0000"  # optional; format: yyyy-MM-dd HH:mm:ss+XXXX
zoneId:  "UTC+01:00"                 # optional, time zone string
type:    finance                     # finance | travelRule | kyc | userPlatformEvent | iGamingSession (default: finance)

# Routing — pick ONE
_applicantId: "67abc..."             # post to existing applicant (path id, NOT a payload field)
# - OR -
_levelName: "Default"                # post to non-existing-applicant URL with ?levelName=...
                                     # (Sumsub creates the applicant from applicant.externalUserId)

# Finance / Travel Rule info (required for those types)
amount:       1500.50
currency:     USD                    # ISO-4217 fiat or crypto ticker (BTC, ETH, …)
currencyType: fiat                   # fiat | crypto  (default: fiat)
direction:    out                    # in | out
amountInDefaultCurrency: 1500.50     # optional, converted to client default
defaultCurrencyCode:     USD
paymentDetails: "Invoice #INV-2026-001"
mcc:    5411                         # optional, 4-digit Merchant Category Code

# Crypto-only block (used when currencyType=crypto)
crypto:
  chain:        ETH                  # ETH | BTC | TRX | … (mandatory for tokens; empty for native)
  contract:     "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
  paymentTxnId: "0x1234abcd..."      # on-chain hash
  fingerprint:  "0x1234abcd..."      # alternative blockchain identifier
  attemptId:    "attempt-01"         # optional, when retrying
  outputIndex:  0                    # for UTXO chains

# Applicant (REQUIRED) — the person/entity acting on your platform
applicant:
  externalUserId: "user-001"         # REQUIRED — your stable user id
  type: individual                   # individual | company (default: individual)
  fullName: "John Smith"             # required for company; recommended for non-existing-applicant flow
  dob: "1990-05-01"
  email: "john@example.com"
  phone: "+1234567890"
  placeOfBirth: "London"
  address:
    country: USA
    town: "New York"
    street: "5th Avenue"
    formatted: "5th Avenue, New York, USA"
  paymentMethod:
    type: bankCard                   # bankCard | bankAccount | crypto | cryptoWallet |
                                     # eWallet | unhostedWallet | card | other
    accountId: "4111********1111"    # IBAN, last4-hash, wallet address, etc.
    issuingCountry: USA
    "3dsUsed": true
    "2faUsed": false
    memo: "optional memo"
  idDoc:
    number: "A12345678"
    country: USA
    idDocType: PASSPORT
  device:
    fingerprint: "abc123"
    userAgent: "Mozilla/5.0 ..."
    ipInfo: { ip: "1.2.3.4" }

# Counterparty (typical for finance + travelRule; same shape as applicant + a few extras)
counterparty:
  externalUserId: "merchant-XYZ"
  type: company
  fullName: "Acme Inc."
  registrationNumber: "12345678"
  leiCode: "529900XXXX0000XXXX00"
  residenceCountry: QAT
  address: { country: QAT }
  institution:                       # → institutionInfo
    code: "ACME-CODE"
    name: "Acme Bank"
    internalId: "<VASP id from directory>"
  ceo:                               # only for company counterparties (Travel Rule)
    firstName: "Jane"
    lastName: "Roe"

# user-platform-event only (when type=userPlatformEvent)
userPlatformEvent:
  type: login                        # login | failedLogin | signup | passwordReset | twoFaReset | general
  twoFaUsed: true
  passwordHash: "..."

# Optional escape hatches
sourceKey: "<segregation key>"
props:                               # custom string-string map
  customField: "value"
  dailyOutLimit: "10000"
```

### Enums (validated upfront)

| Field | Allowed values |
|---|---|
| `type` (top-level) | `finance`, `travelRule`, `kyc`, `auditTrailEvent`, `userPlatformEvent`, `scheduledEvent`, `iGamingSession` |
| `direction` | `in`, `out` |
| `currencyType` | `crypto`, `fiat` |
| `applicant.type` / `counterparty.type` | `individual`, `company` |
| `applicant.nameType` | `aliasName`, `birthName`, `maidenName`, `legalName`, `shortName`, `tradingName`, `other` |
| `userPlatformEvent.type` | `login`, `failedLogin`, `signup`, `passwordReset`, `twoFaReset`, `general` |

`paymentMethod.type` is intentionally **not** enum-checked — the OpenAPI lists `KytTxnPaymentMethodType` (only `smartContract`, `bankCard`, `bankAccount`) but the docs and live data accept many more (`crypto`, `eWallet`, `unhostedWallet`, etc.). The builder forwards whatever the caller supplies.

## Outputs

On success, report all of:
- `txnId` (yours) **and** `id` (server-assigned, used in the dashboard link).
- Applicant `externalUserId`.
- `direction amount currency`, counterparty (if any).
- The response's `score` / `reviewAnswer` / `riskLabels` if returned.
- **Dashboard link**: `https://cockpit.sumsub.com/checkus/kyt/txns/<id>?clientId=<clientId>&sbx=true`. Render as a clickable markdown link. `<id>` is the **server-assigned identifier** (not the `txnId` you sent); both it and `clientId` are in the POST response body; `sbx=true` targets the Sandbox workspace.

On failure: HTTP status + Sumsub's `description`/`errorName`. Most likely 4xx cases:
- `409 Entity already exists` — `txnId` collision (use a fresh id or the bulk-import method to update).
- `400` — required field missing (typical: `info.amount`, `info.currencyCode`, `info.direction`, or `applicant.externalUserId`).
- `400` — `levelName` unknown (when using non-existing-applicant flow).

## Worked examples

- [`examples/fiat-out.json`](examples/fiat-out.json) — outbound EUR card payment to a foreign counterparty (the docs' canonical example).
- [`examples/crypto-in.json`](examples/crypto-in.json) — inbound ETH deposit with `cryptoParams.cryptoChain=ETH`, contract address, on-chain `paymentTxnId`.
- [`examples/travel-rule.json`](examples/travel-rule.json) — `type: travelRule` outbound crypto with `institution.internalId` (VASP id) on the counterparty.
- [`examples/login-event.json`](examples/login-event.json) — `type: userPlatformEvent` for a successful login with 2FA.
- [`examples/new-applicant.json`](examples/new-applicant.json) — non-existing-applicant flow: `_levelName` is set so the POST goes to `/-/kyt/txns/-/data` with `?levelName=...`.

## See also

- [references/transaction-schema.md](references/transaction-schema.md) — full `KytTxnData` schema, all sub-objects, all enums, the existing-vs-new-applicant routing, scoring response fields, common gotchas.
- [Sumsub docs — Submit transaction](https://docs.sumsub.com/reference/submit-transaction-for-existing-applicant.md)
- [Sumsub docs — Submit transaction for non-existing applicant](https://docs.sumsub.com/reference/submit-transaction-for-non-existing-applicant.md)
- [Sumsub docs — Submit transactions and review results](https://docs.sumsub.com/docs/submit-transactions-and-review-results.md)
