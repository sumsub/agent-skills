
# Finding transactions — the query endpoint and the dedupe ladder

Two reads, both public:

| Verb | Path | Purpose |
|---|---|---|
| `GET` | `/resources/kyt/txns/query/-;<criteria>?order=…&limit=…` | Search. Criteria go in **matrix parameters on the path**, not the query string. |
| `GET` | `/resources/kyt/txns/{id}/one` | One transaction by its Sumsub id. |

Permission: `seeKytTxns`.

## Syntax

Criteria are semicolon-separated `key=value` pairs appended to the path
segment. `order` and `limit` are ordinary query parameters after `?`.

```
GET /resources/kyt/txns/query/-;data.type=travelRule;data.info.paymentTxnId=<hash>?order=-createdAt&limit=1
```

Range comparisons use suffixes on the field name:

| Suffix | Meaning |
|---|---|
| `__gte` | ≥ |
| `__lte` | ≤ |
| `__ne` | ≠ |

```
GET /resources/kyt/txns/query/-;data.info.direction=in;data.info.amount__gte=100;data.info.amount__lte=500;data.info.currencyCode=USDT;data.info.cryptoParams.cryptoChain=ETH;data.txnDate__gte=2026-05-21%2000%3A00%3A00;data.txnDate__lte=2026-05-21%2023%3A59%3A59;data.type=travelRule?order=-data.txnDate&limit=100
```

📘 **Everything in the path must be URL-encoded**, and dates bite hardest:
`2026-05-21 00:00:00` becomes `2026-05-21%2000%3A00%3A00`.

📘 `order` takes a field name with an optional leading `-` for descending.
`-createdAt` and `-data.txnDate` are the useful ones.

## Which fields you can filter on

The server enforces an allowlist and is the authority on it. The list has been
growing, so treat the set below as *known to work* rather than as the boundary —
try the field you need, and read the error if it is refused.

Commonly used and known good:

```
data.type                                    data.info.currencyCode
data.info.direction                          data.info.cryptoParams.cryptoChain
data.info.paymentTxnId                       data.info.amount
data.txnDate                                 data.sourceKey
data.applicant.paymentMethod.accountId       clientId
data.counterparty.paymentMethod.accountId
```

A refused field comes back as
`The following fields are not allowed in query criteria: <field>` — the message
names the offender, so relay it rather than guessing a substitute. The
allowlist is checked against the *base* field name, so `data.info.amount__gte`
is accepted because `data.info.amount` is.

🚧 Do not silently swap a refused field for a near-miss that happens to be
allowed. A query that answers a different question than the user asked is worse
than an error.

Two limits that are not about fields: `limit` must be **≤ 100**, and the
criteria set must not be empty — an unfiltered "give me everything" is
rejected.

## Auth — App Token + secret (sandbox only)

Signing per [the authentication reference](https://docs.sumsub.com/reference/authentication);
mechanics in [`sumsub-api-auth`](../../sumsub-api-auth/SKILL.md).

> **⚠️ Sandbox tokens only.** This is read-only, but transaction records are
> real customer data. The helper script rejects tokens without an `sbx:`
> prefix. Sandbox pair: <https://cockpit.sumsub.com/checkus/home?xSNSEnv=sbx>.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` |
| `SUMSUB_SECRET_KEY` | The paired secret. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

**Sign the path you send.** The criteria are part of the path, so they are part
of the signed bytes — encoded exactly as transmitted. The helper script builds
and signs the same string; if you hand-roll the request, do not re-encode
between signing and sending.

## Procedure

1. **Build the path** with `${CLAUDE_SKILL_DIR}/scripts/build_query.py` — it
   encodes values, applies the operator suffixes, enforces the non-empty and
   limit rules, and warns about fields it does not recognise without blocking
   them.
2. **Send it** with `${CLAUDE_SKILL_DIR}/scripts/find_transactions.sh "<path>"`,
   or fetch one by id with
   `${CLAUDE_SKILL_DIR}/scripts/get_transaction.sh <txnId>`.
3. **Report honestly.** An empty result means no match under *these* criteria.
   If a field was refused, say which one rather than reporting "nothing found".

## The deduplication check

The one search every Travel Rule integration needs. Before creating an exchange
for a transfer that already settled, make sure one does not exist — a duplicate
puts two requests in the counterparty's queue.

Work down the ladder and stop at the first unambiguous single match:

1. **The blockchain hash** — `data.info.paymentTxnId`. Exact and unique. Use it whenever you have it.
2. **Counterparty address + asset** — when the hash is not indexed yet. Enough for most deposits, but a counterparty that sends you many transfers from one address returns several rows.
3. **Add amount and a time window** — `data.info.amount__gte/__lte` plus `data.txnDate__gte/__lte` around settlement.

Only create a new exchange when nothing comes back. See
[the main skill](../SKILL.md).

## Worked examples

- [`../examples/dedupe-by-hash.json`](../examples/dedupe-by-hash.json) — step 1 of the ladder.
- [`../examples/dedupe-by-address-window.json`](../examples/dedupe-by-address-window.json) — steps 2–3 combined.
- [`../examples/travel-rule-recent.json`](../examples/travel-rule-recent.json) — recent Travel Rule transactions in one direction.

## See also

- [`query-syntax.md`](query-syntax.md) — operators, encoding rules, response shape, error messages.
- [`sumsub-create-transaction`](../../sumsub-create-transaction/SKILL.md) — the write side.
- Sumsub docs: [Find specific Travel Rule transactions](https://docs.sumsub.com/reference/how-to-find-specific-travel-rule-transactions-via-api), [Get transaction information](https://docs.sumsub.com/reference/get-transaction).
