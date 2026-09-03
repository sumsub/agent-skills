---
name: sumsub-resolve-currency
description: Resolve and validate the currency fields Sumsub expects on a transaction — `info.currencyCode`, `info.currencyType`, `info.cryptoParams.cryptoChain` and the `amountInDefaultCurrency` / `defaultCurrencyCode` pair. Reads the catalogue from `GET /resources/kyt/currency?type=crypto|fiat` and resolves a (symbol, chain, contract) triple to exactly one asset, normalising chain aliases and refusing ambiguous input rather than guessing. TRIGGER when the user asks "which currency codes / chains does Sumsub support", "is USDT on TRON supported", "what do I put in cryptoChain", "why is my currency not recognised", "why is amountInDefaultCurrency wrong / missing", or is about to submit a transaction with a token whose symbol exists on several networks. SKIP for building the transaction itself (use `sumsub-create-transaction`), for currency-based scoring rules (use `sumsub-create-kyt-rules`), and for FX rates or historical conversion — Sumsub exposes no rates endpoint.
allowed-tools: Read, Write, Bash
---

# Sumsub — Resolve currency and chain

One endpoint answers both halves, and the two halves look nothing alike:

| `type=fiat` | `type=crypto` |
|---|---|
| Flat list of ISO 4217 codes, fetched live | Thousands of assets across a hundred-plus chains |
| No chain, no contract, no ambiguity | Over a thousand symbols exist on **more than one** chain |
| Resolving = "is it in the list" | Resolving = `(symbol, chain, [contract])` → exactly one asset |

Most of this skill is about the crypto side, because that is where transactions
silently go wrong. Fiat is a membership test.

## Endpoint

| Verb | Path | Purpose |
|---|---|---|
| `GET` | `/resources/kyt/currency?type=crypto` | The crypto catalogue. Static server-side; safe to cache for a session. |
| `GET` | `/resources/kyt/currency?type=fiat` | Fiat codes, assembled live from the rates provider. |

Omit `type` and you get the fiat list. There is **no public endpoint for the
chain list** — derive it from the crypto catalogue's distinct `cryptoChain`
values. There is **no rates endpoint**: Sumsub converts internally and does not
expose the rate it used.

Each crypto entry carries `currencyCode`, `cryptoChain`, `contractAddress`,
`chainId`, `name`, `coinmarketcapId`, `coingeckoId`.

## Auth — App Token + secret (sandbox only)

Signing per [the authentication reference](https://docs.sumsub.com/reference/authentication);
mechanics in [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md).

> **⚠️ Sandbox tokens only.** The helper script refuses tokens that don't start
> with `sbx:` unless `SUMSUB_ALLOW_PROD=1`. This endpoint is read-only, but the
> same rule applies across these skills — get a sandbox pair at
> <https://cockpit.sumsub.com/checkus/home?sbx=true> (**Connect Sumsub to your AI agent** -> **Build & configure** -> **Generate token**).

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` |
| `SUMSUB_SECRET_KEY` | The paired secret. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

## The rule that matters

**A symbol is not an asset.** `USDT` and `USDC` each name more than a dozen
different assets in the catalogue; `ETH` several. The identity of a crypto
asset is the pair `(currencyCode, cryptoChain)`, plus `contractAddress` when
even that is not unique.

📘 **An empty `cryptoChain` is a value, not a gap.** It means *the native coin
of its own chain* — `BTC` with no chain is bitcoin; `BTC` with `cryptoChain:
BTC` is the same thing (the server normalises that common mistake); `BTC` on
some wrapped chain is a different asset entirely.

🚧 **Ambiguity does not resolve to a default — it resolves to nothing.** When a
lookup matches more than one row the server logs `Multiple currencies found`
and returns no currency at all. So the symptom of a missing chain is not "wrong
rate" but "currency not recognised", with everything downstream that depends on
it silently degraded.

## Procedure

1. **Decide the type.** If the code is three uppercase letters and appears in
   the fiat list, treat it as fiat unless the user says otherwise. Beware of
   overlaps in intent — a user saying "USD" almost never means a token called
   USD.
2. **Fetch the catalogue** with `${CLAUDE_SKILL_DIR}/scripts/get_currencies.sh crypto`
   (or `fiat`). Cache it for the session; the crypto list is large and static.
3. **Resolve** with `${CLAUDE_SKILL_DIR}/scripts/resolve_currency.py` — pass the
   catalogue and the query. It uppercases and trims, expands chain aliases,
   treats `code == chain` as the native coin, and on ambiguity **fails with the
   candidate list** instead of picking one.
4. **Report the exact fields to send**, never just "supported":

   ```json
   "info": {
     "currencyCode": "USDT",
     "currencyType": "crypto",
     "cryptoParams": { "cryptoChain": "TRX" }
   }
   ```

5. **Address the conversion** — see below. This is the part callers forget.

## `amountInDefaultCurrency` — read this before skipping it

`info.amountInDefaultCurrency` + `info.defaultCurrencyCode` express the
transfer in your reporting currency. They look optional. They are not, in three
ways.

🚧 **Travel Rule thresholds are compared against `amountInDefaultCurrency`.**
If it is absent, the threshold comparison is **skipped entirely** and the
Travel Rule flow runs regardless of how small the transfer is. Omitting the
field does not lose precision — it changes behaviour. The same applies to the
unhosted-wallet verification threshold.

🚧 **The value is frozen at ingest.** Sumsub computes it once, when the
transaction is created, and stores it. A rate that was wrong at that moment
stays wrong on the record; correcting it later means a backfill, not a
re-read.

📘 **If the asset does not resolve, there is nothing to convert.** An
unrecognised `(symbol, chain)` pair means no conversion happens — which is the
second reason a missing `cryptoChain` is expensive.

**Recommendation:** if you know the value your own systems used, send
`amountInDefaultCurrency` and `defaultCurrencyCode` explicitly. Your books and
Sumsub's record then agree by construction, and you are not depending on a
third-party rate at an instant you do not control.

## Chain aliases

Chain names are uppercased, trimmed, then mapped through a fixed alias table
before lookup. `ETHEREUM`, `BSC`, `TRC20`, `MATIC`, `POLYGON`, `BEP20`,
`TRON`, `SOLANA`, `AVAX_C` and about two dozen more resolve to their canonical
chain. Anything outside the table is used verbatim, so a near-miss like
`TRON20` or `ERC-20` simply does not match.

The table is not exposed by any endpoint — the full list is in
[`references/crypto-catalogue.md`](references/crypto-catalogue.md). When a
user's chain string fails to resolve, check it against the aliases before
concluding the asset is unsupported.

## Travel Rule specifics

Beyond the threshold behaviour above, the asset you pick can decide whether an
exchange is possible at all. Each catalogue entry carries the counterparty
protocols' own vocabularies, and coverage is thin.

Only a minority of catalogue entries carry a mapping for any given protocol —
Sygna covers the most, then GTR, then CODE, and all three are a small fraction
of the whole. Coverage grows as the weekly listing job picks up new assets, so
check rather than assume.

An asset with no mapping for the protocol your counterparty speaks cannot be
expressed in their message. The exchange fails validation before anything is
sent — surfacing as `notEnoughCounterpartyData`, which reads like a data
problem rather than an asset-support problem. If a Travel Rule exchange fails
that way on an exotic token, check the vocabulary coverage before debugging the
payload. See [`sumsub-integrate-travel-rule`](../sumsub-integrate-travel-rule/SKILL.md).

## Outputs

- **Resolved** — the matched entry, and the exact `currencyCode` / `currencyType` / `cryptoChain` to send. Mention `contractAddress` when the symbol is a known collision, so the caller can pin it.
- **Ambiguous** — the candidate rows with their chains and contracts, and the question the user must answer. Never pick one.
- **Not found** — say whether the *symbol* is unknown or only the *chain* is, and check the alias table before declaring it unsupported.

## Worked examples

- [`examples/resolve-usdt-tron.json`](examples/resolve-usdt-tron.json) — the common case: a collided symbol pinned by chain.
- [`examples/resolve-ambiguous.json`](examples/resolve-ambiguous.json) — the same symbol with no chain; must fail, not guess.
- [`examples/resolve-native.json`](examples/resolve-native.json) — a native coin, showing the empty-chain semantics.
- [`examples/resolve-fiat.json`](examples/resolve-fiat.json) — the membership test.

## See also

- [`references/crypto-catalogue.md`](references/crypto-catalogue.md) — catalogue fields, the alias table, the server's resolution ladder, collision statistics.
- [`sumsub-create-transaction`](../sumsub-create-transaction/SKILL.md) — where the resolved fields go.
- [`sumsub-integrate-travel-rule`](../sumsub-integrate-travel-rule/SKILL.md) — thresholds and protocol vocabularies.
