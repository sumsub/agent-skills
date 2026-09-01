# Transaction query syntax — reference

## Shape

```
GET /resources/kyt/txns/query/-;<field>=<value>;<field>=<value>?order=<field>&limit=<n>
```

Criteria are **matrix parameters on the path segment**, separated by `;`.
`order` and `limit` are ordinary query parameters after `?`. Both parts are
signed, so encode once and sign exactly what you send.

## Which fields you can filter on

The server enforces an allowlist and owns it; the set has been expanding, so
the table below is *known to work today*, not a boundary. Try the field you
need and read the refusal if it comes.

| Field | Notes |
|---|---|
| `clientId` | Your own client id. |
| `data.applicant.paymentMethod.accountId` | Your user's address. On an incoming Travel Rule request this is the address you are asked to confirm. |
| `data.counterparty.paymentMethod.accountId` | The other side's address. |
| `data.info.amount` | In the transfer's own currency, not your default one. |
| `data.info.cryptoParams.cryptoChain` | Canonical chain ticker. Aliases are not expanded here — send `TRX`, not `TRON`. |
| `data.info.currencyCode` | Ticker. Pair it with the chain: a symbol alone can name many assets. |
| `data.info.direction` | `in` or `out`. Mirrored between the two sides of an exchange. |
| `data.info.paymentTxnId` | The on-chain hash. The one exact identifier available. |
| `data.txnDate` | Format `yyyy-MM-dd HH:mm:ss`, URL-encoded. |
| `data.type` | `finance`, `travelRule`, `kyc`, `userPlatformEvent`, … |
| `data.sourceKey` | Source key, when you segment traffic by it. |

A refused field returns
`The following fields are not allowed in query criteria: <field>`. The message
names the offender — relay it. Do not substitute a near-miss field that happens
to be allowed: a query answering a different question is worse than an error.

The check runs against the *base* field name, so a suffixed field passes when
its base is allowed.

## Operators

| Suffix | Meaning | Example |
|---|---|---|
| `__gte` | ≥ | `data.info.amount__gte=100` |
| `__lte` | ≤ | `data.txnDate__lte=2026-05-21%2023%3A59%3A59` |
| `__ne` | ≠ | `data.info.direction__ne=in` |

Equality is the bare field: `data.type=travelRule`. The allowlist is checked
against the base field name, so a suffixed field passes when its base is
allowed.

## Limits

| Rule | Value |
|---|---|
| Max `limit` | 100 — above it, `"limit" must be less than or equal to 100` |
| Default `limit` | 100 when omitted |
| Empty criteria | Rejected: `"criteria" must not be empty` |

## Encoding

Everything in the path is URL-encoded. Dates are where this bites:
`2026-05-21 00:00:00` → `2026-05-21%2000%3A00%3A00`. Addresses are usually
safe but encode them anyway rather than reasoning per chain.

`order` takes a field name with an optional leading `-` for descending:
`-createdAt`, `-data.txnDate`.

## A sibling endpoint that is not this one

`GET /resources/kyt/txns/{segment}` — same restler DSL without the validator or
the limit cap — exists but is not part of the public contract, and the field
allowlist does not apply to it. Do not use it to work around the restrictions
here; `/query/-` is the supported surface.

## Response

`EntityResult<KytTxnApiDto>`: `{ "list": { "items": [ … ], "totalItems": n } }`.
An empty `items` means no match **under these criteria** — with an allowlist
this narrow, that is a weaker statement than "the transaction does not exist".
