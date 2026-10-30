# Finding transactions — the search endpoint and the dedupe check

Two reads, both public:

| Verb | Path | Purpose |
|---|---|---|
| `POST` | `/resources/api/tr/txns/search` | Find an existing Travel Rule transaction for a settled transfer. JSON body. |
| `GET` | `/resources/kyt/txns/{id}/one` | One transaction by its Sumsub id. |

Permission: **View TM transactions** on the App Token, and Travel Rule enabled
for the client — otherwise `403`.

## Request body

| Field | Required | Notes |
|---|---|---|
| `paymentTxnId` | yes | On-chain hash of the transfer. |
| `applicantWalletAddress` | yes | Your customer's wallet — the deposit (beneficiary) address for `in`. |
| `amount` | yes | Positive number, in the transfer's own asset. |
| `currencyCode` | yes | Ticker, e.g. `USDT`. Case-insensitive. |
| `txnDate` | yes | Settlement time, `yyyy-MM-dd HH:mm:ss+0000`. |
| `direction` | yes | `in` (deposits) or `out` (withdrawals). |
| `counterpartyWalletAddress` | no | The other side's address, when known. Often unavailable on UTXO chains. |
| `cryptoChain` | no | Network, e.g. `TRX`. Send it — a ticker alone can name many assets. |

```json
{
  "paymentTxnId": "<hash>",
  "applicantWalletAddress": "0xourdepositaddress",
  "counterpartyWalletAddress": "0xaddressthefundscamefrom",
  "amount": 1250,
  "currencyCode": "USDT",
  "cryptoChain": "ETH",
  "txnDate": "2026-05-21 09:12:00+0000",
  "direction": "in"
}
```

A missing required field or a non-positive `amount` returns `400`. Do not
invent a value to get past it — ask the user for the missing field.

## Response

```json
{ "list": { "items": [ { "id": "…", "externalTxnId": "…", "reviewStatus": "…",
  "travelRuleStatus": "…", "paymentTxnId": "…", "amount": 1250, "currencyCode": "USDT",
  "cryptoChain": "ETH", "txnDate": "2026-05-21 09:12:00+0000" } ], "totalItems": 1 } }
```

`totalItems` is `0` or `1` — the endpoint returns the best match, not a list
to page through.

## Auth — App Token + secret (sandbox only)

Signing per [the authentication reference](https://docs.sumsub.com/reference/authentication);
mechanics in [`sumsub-api-auth`](../../sumsub-api-auth/SKILL.md).

> **⚠️ Sandbox tokens only.** This is read-only, but transaction records are
> real customer data. The helper script rejects tokens without an `sbx:`
> prefix. Sandbox pair: <https://cockpit.sumsub.com/checkus/home?sbx=true>.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` |
| `SUMSUB_SECRET_KEY` | The paired secret. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

## Procedure

1. **Write the body** — shape in
   [`../examples/dedupe-search.json`](../examples/dedupe-search.json).
2. **Send it** with `${CLAUDE_SKILL_DIR}/scripts/find_transactions.sh <body.json>`
   (or `-` for stdin), or fetch one by id with
   `${CLAUDE_SKILL_DIR}/scripts/get_transaction.sh <txnId>`.
3. **Report honestly.** An empty result means no match for *this* transfer, not
   proof that nothing exists under other details.

## The deduplication check

The one search every Travel Rule integration needs. Before creating an exchange
for a transfer that already settled, make sure one does not exist — a duplicate
puts two requests in the counterparty's queue.

The server walks the ladder for you: exact match on `paymentTxnId` first, then
wallet addresses + asset/network, preferring a row whose amount and `txnDate`
(±24h) also match. Send every field you have — the fallback is only as good as
the addresses, chain, amount and date you give it.

Only create a new exchange when nothing comes back. See
[the main skill](../SKILL.md).

## See also

- [`sumsub-create-transaction`](../../sumsub-create-transaction/SKILL.md) — the write side.
- Sumsub docs: [Search for an existing Travel Rule transaction](https://docs.sumsub.com/reference/search-for-existing-travel-rule-transaction), [Get transaction information](https://docs.sumsub.com/reference/get-transaction).
