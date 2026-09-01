# Crypto currency catalogue — reference

## Shape

`GET /resources/kyt/currency?type=crypto` returns a flat array. Fields visible
over the public API:

| Field | Meaning |
|---|---|
| `currencyCode` | Ticker symbol. **Not unique.** |
| `cryptoChain` | Native currency ticker of the chain (`ETH`, `BTC`, `TRX`, `TON`). Empty means the entry *is* the native coin. |
| `contractAddress` | Token contract, where applicable. |
| `chainId` | Numeric chain id (CAIP-2 style), e.g. `1` Ethereum, `56` BNB. |
| `name` | Human-readable asset name. |
| `coinmarketcapId` | CoinMarketCap UCID. |
| `coingeckoId` | CoinGecko id. |

The stored records carry more — per-provider vocabularies (`chainalysisAsset`,
`ellipticAsset`, `trmLabsChain`, `merkleBlockchainId`, `crystalCurrency`,
`fireblocksAssetId`) and Travel Rule protocol vocabularies (`gtrTicker`,
`gtrNetwork`, `sygnaCurrencyId`, `codeCurrency`, `codeNetwork`) — but these are
not returned to API clients. Their coverage still matters, see below.

## Scale and collisions

The catalogue holds thousands of assets across a hundred-plus chains, and over
a thousand symbols appear on more than one chain. `USDC` and `USDT` lead with
more than a dozen entries each, `ETH` has several, then a long tail of
memecoins reusing tickers.

Exact counts move every week — the listing job below adds assets continuously —
so derive them from the catalogue you just fetched rather than quoting a
figure. The invariant is the one that matters: **any integration that keys
assets by symbol alone will eventually hit a collision.**

## How the server resolves a lookup

Chain strings are normalised first: trim → uppercase → alias table. An empty
chain becomes an internal "native" sentinel. Then, in order:

1. **`(code, chain, contract)`** — exact match.
2. **`(code, chain)`** — tried when step 1 misses. If this hits, the server
   logs `Currency matched without contract address — contractAddress likely
   invalid` **and returns the match anyway**. A wrong contract address is
   therefore swallowed silently from the caller's point of view.
3. **`code == chain` → retry as native.** Handles the common client mistake of
   sending `BTC`/`BTC` or `ETH`/`ETH` instead of `BTC`/empty.

At every step, **more than one hit returns nothing**: the server logs
`Multiple currencies found` and yields no currency rather than choosing. Design
for "unresolved", not for "wrong pick".

## Chain aliases

Applied after uppercasing, before lookup. Anything not listed is used verbatim.

| Alias | Canonical |
|---|---|
| `ETHEREUM` | `ETH` |
| `BITCOIN` | `BTC` |
| `MATIC`, `POLYGON`, `POL_POLYGON` | `POL` |
| `BSC`, `BEP20` | `BNB` |
| `TRON`, `TRC20` | `TRX` |
| `SOLANA` | `SOL` |
| `STELLAR` | `XLM` |
| `AVAXC`, `CAVAX`, `AVAX_C` | `AVAX` |
| `ARBI`, `ARBITRUM`, `ARBEVM` | `ARB` |
| `OPTIMISM` | `OP` |
| `APTOS` | `APT` |
| `MANTLE` | `MNT` |
| `PULSE` | `PLS` |
| `PLASMA` | `XPL` |
| `VECHAIN` | `VET` |
| `HYPEEVM`, `HYPEREVM` | `HYPE` |
| `SEIEVM` | `SEI` |
| `MONAD` | `MON` |
| `SONIC` | `S` |
| `ETH_BASE` | `BASE` |

Near-misses are not forgiven: `TRON20`, `ERC-20`, `ERC20`, `Polygon PoS` do not
resolve. Check this table before telling a user their asset is unsupported.

## Travel Rule protocol vocabularies

The counterparty's protocol has its own names for assets and networks, and the
mapping is stored per catalogue entry. Approximate coverage:

Only a minority of entries carry a mapping for any given protocol: Sygna
covers the most, then GTR, then CODE, all of them a small fraction of the
catalogue. An asset without a mapping for the protocol in use
cannot be expressed in the outgoing message; the exchange ends at
`notEnoughCounterpartyData` before delivery. This is an asset-support problem
wearing a data-validation error's clothes.

Coverage is refreshed by a weekly job that polls the providers' own listing
APIs for assets Sumsub does not yet support, so gaps close over time — but not
on demand, and not because a client asked.

## Fiat

`GET /resources/kyt/currency?type=fiat` (or no `type`) returns ISO 4217 codes
assembled live from the rates provider. Only `currencyCode` is meaningful;
`cryptoChain`, `contractAddress` and the ids are absent. Matching is
case-insensitive. There is no chain concept and no ambiguity.

## What is not available

- **No rates endpoint.** Sumsub converts to your default currency internally
  and does not expose the rate or the timestamp used.
- **No public chain list.** Derive distinct `cryptoChain` values from the
  crypto catalogue; the dedicated endpoint is dashboard-only.
- **No alias endpoint.** The table above is code-only.
