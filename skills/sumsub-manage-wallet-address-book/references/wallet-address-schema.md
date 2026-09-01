# Wallet Address Book — schema reference

## `POST /resources/kyt/walletAddress/import`

Body: a **JSON array** of wallet entries. Not an object, not NDJSON.

```json
[
  { "walletAddress": "bc1q...", "asset": "BTC", "chain": "BTC" },
  { "walletAddressHash": "9f2c...", "asset": "ETH", "chain": "ETH" }
]
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `walletAddress` | string | one of the two | Plain address. |
| `walletAddressHash` | string | one of the two | Pre-hashed address. Sending both is only valid when they agree. |
| `asset` | string | no | Currency code. |
| `chain` | string | no | Network. |
| `source` | string | no | **Ignored on import** — the server stamps `api`. |
| `createdAt` | date | no | Server-assigned; ignored on input. |
| `vaspIdOwner` | ObjectId | — | Response only, and restricted — not returned to ordinary API subjects. |
| `dataOwnerClientId` | string | — | Response only, restricted. |

### Limits and preconditions

- **10 000 entries per call.** Over that: HTTP 400 `Too many wallets, 10000 is limit`. Chunk client-side.
- The tenant needs the **Travel Rule** entitlement.
- The organisation must be **linked to a VASP**, otherwise HTTP 404 `Your organization is not yet linked to a VASP. Please contact your Customer Success Manager`.
- The endpoint requires the **admin** role on the token subject.

### Response

```json
{ "successCount": 812, "errorCount": 3, "errors": [
  { "message": "Either 'walletAddress' or 'walletAddressHash' must not be empty",
    "walletAddressHash": null, "walletAddress": null }
]}
```

The call returns **200 even when entries failed** — it is a partial-success
API. `errorCount > 0` with a 200 is normal and must be surfaced.

Known per-entry errors:

| Message | Cause |
|---|---|
| `Either 'walletAddress' or 'walletAddressHash' must not be empty` | Both omitted. |
| `Invalid hash function for 'walletAddressHash' field` | Both sent, and the hash does not match the address under Sumsub's hashing. |

## Source-type precedence

Every stored address carries a source, and automatic ownership confirmation
only trusts the higher-priority ones. Lower number = higher priority.

| Source | Priority | How it gets there | Trusted for auto-confirm |
|---|---|---|---|
| `api` | 1 | This import endpoint | ✅ |
| `dashboard` | 1 | Manual entry in the dashboard | ✅ |
| `snsConfirmation` | 2 | You confirmed ownership on an earlier exchange | ✅ |
| `applicantPaymentsApi` | 3 | Registered as an applicant payment method | ✅ |
| `vaspLookup` | 4 | Derived from VASP attribution / GTR | ❌ |
| `applicantData` | 5 | Inferred from a client transaction | ❌ |

The cut-off is `applicantPaymentsApi`: anything ranked below it is treated as a
hint, not a declaration. This is deliberate — it stops a busy account from
silently auto-confirming addresses nobody vouched for.

## `POST /resources/api/applicants/{applicantId}/payments`

```json
{
  "externalId": "wallet-btc-user-001",
  "data": {
    "type": "cryptoWallet",
    "accountIdentifier": "bc1q...",
    "fullName": "John Smith",
    "currencyCode": "BTC",
    "cryptoChain": "BTC"
  }
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `externalId` | string | no | Your identifier for the payment method. |
| `data.type` | enum | ✓ | `cryptoWallet`, `bankCard`, `bankAccount`, `eWallet`, `other`. |
| `data.subType` | string | no | Free-form. |
| `data.accountIdentifier` | string | one of the two | The address / account number. |
| `data.accountIdentifierHash` | string | one of the two | Hashed form. |
| `data.fullName` | string | no | Holder name. |
| `data.memo` | string | no | Destination tag / memo for chains that need one. |
| `data.currencyCode` | string | no | e.g. `BTC`. |
| `data.cryptoChain` | string | no | e.g. `BTC`, `ETH`, `TRX`. |
| `data.validUntil` | date | no | Expiry, where applicable. |
| `institutionInfo` | object | no | Issuing institution, for bank instruments. |

Permission required: `managePersonalData`. The path takes Sumsub's internal
applicant id — resolve an `externalUserId` first with
`GET /resources/applicants/-;externalUserId={externalUserId}/one`.

There is no public update or delete for payment methods; the corresponding
handlers exist server-side but are commented out of the API resource.
