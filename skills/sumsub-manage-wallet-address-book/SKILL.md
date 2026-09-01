---
name: sumsub-manage-wallet-address-book
description: Register the crypto wallet addresses an organisation controls, so Sumsub can resolve address ownership without a human. Bulk-imports addresses into the Wallet Address Book via `POST /resources/kyt/walletAddress/import`, and registers a single address against a specific applicant via `POST /resources/api/applicants/{applicantId}/payments`. TRIGGER when the user asks to "upload / import / register our wallet addresses", "add addresses to the Wallet Address Book", "register a user's crypto wallet as a payment method", says Travel Rule requests are "not matching automatically" or "always land in manual review", or asks how to stop confirming the same address by hand on every exchange. SKIP for looking up which VASP owns a *counterparty* address (that is attribution — use `sumsub-api-generic` against `/resources/api/wallet-attribution`), for confirming ownership on one specific transaction (use `sumsub-integrate-travel-rule`), and for deleting addresses (no public endpoint — use the dashboard).
allowed-tools: Read, Write, Bash
---

# Sumsub — Wallet Address Book

Tells Sumsub which crypto addresses belong to your organisation, and which of
your users each one belongs to. This is the data that turns Travel Rule
answering from a manual queue into an automatic one.

## Why this matters more than it looks

When another VASP starts a Travel Rule exchange that involves one of your
users, Sumsub asks you two questions: *is this wallet yours?* and *whose is
it?* Both can be answered from stored data instead of by a person — but only
if the address is already registered.

| What you register | What it pre-answers |
|---|---|
| Address in the **Wallet Address Book** | "Is this wallet ours?" |
| Address as an applicant **payment method** | Both questions |

Anything not registered falls to manual handling, and manual handling does not
survive volume — counterparties can set the confirmation window to seconds.
The mechanics of how a pre-answered request arrives, and which flags to read,
belong to [`sumsub-integrate-travel-rule`](../sumsub-integrate-travel-rule/SKILL.md);
this skill is only about getting the data in.

🚧 **The most common mistake is uploading only deposit addresses.** Exchanges
created *after* settlement ask about the address the funds were sent *from* —
i.e. an address your users withdraw from. If the book holds only addresses you
receive on, that whole class of request silently falls to manual review. Ask
the user explicitly whether their export covers both directions.

## Endpoints

| Verb | Path | Purpose |
|---|---|---|
| `POST` | `/resources/kyt/walletAddress/import` | Bulk-register addresses your organisation controls. Body is a **JSON array** of wallet entries. Max **10 000** per call. |
| `POST` | `/resources/api/applicants/{applicantId}/payments` | Register one address against a specific applicant, as a `cryptoWallet` payment method. |

There is **no public list, update or delete** endpoint for the Wallet Address
Book. To review or remove entries, send the user to the dashboard
(**Transactions and travel rule → Wallet address book**).

### Two preconditions that produce confusing errors

- **The organisation must be linked to a VASP.** The import resolves your VASP
  from the token's client id and fails with `Your organization is not yet
  linked to a VASP. Please contact your Customer Success Manager` (HTTP 404) if
  there is none. This is not a permissions problem and retrying will not help —
  relay the message and stop.
- **Travel Rule entitlement is required** on the tenant. Check with
  [`sumsub-check-permissions`](../sumsub-check-permissions/SKILL.md) before
  building a payload and report the gap rather than letting the call 403.
- The import endpoint additionally requires the **admin** role on the token
  subject. A scoped agent token may not have it — if you get a 403 while the
  entitlement check passed, this is why; the user has to run the import from a
  token with admin rights or from the dashboard.

## Auth — App Token + secret (sandbox only)

This skill talks to the public Sumsub API and signs each request per
[the authentication reference](https://docs.sumsub.com/reference/authentication).
The full how-it-works writeup lives in the [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md)
skill — read it if you hit `401 Invalid signature`.

> **⚠️ Sandbox tokens only.** Do **not** accept or use a production App Token
> here. Wallet addresses are business-identifying data, and a bad import in
> production changes how real Travel Rule requests are answered. If the user
> offers a production token, refuse and ask them to generate a sandbox pair at
> <https://cockpit.sumsub.com/checkus/home?xSNSEnv=sbx> (**Connect Sumsub to your
> AI agent** -> **Build & configure** -> **Generate token**). Token + secret are
> shown once — copy both before closing the dialog. The helper script enforces this — it rejects
> tokens that don't start with `sbx:` unless `SUMSUB_ALLOW_PROD=1` is set.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

## Procedure

1. **Establish which addresses the user is registering** and, critically, in
   which direction they are used. If they say "our wallets" without
   qualification, ask whether the list includes withdrawal addresses.
2. **Decide which endpoint fits.**
   - Many addresses, ownership at organisation level → **import**.
   - One address that belongs to a known applicant → **payment method**. Prefer
     this whenever the applicant is known; it pre-answers both questions
     instead of one.
3. **Check entitlements** with `sumsub-check-permissions` (looking for
   `TRAVEL_RULE`).
4. **Build the import body** with `${CLAUDE_SKILL_DIR}/scripts/build_wallet_import.py`
   (compact spec on stdin → JSON array on stdout). It validates the address /
   hash rules below and refuses batches over 10 000.
5. **Send it.**
   - `${CLAUDE_SKILL_DIR}/scripts/import_wallet_addresses.sh <payload.json>`
   - `${CLAUDE_SKILL_DIR}/scripts/add_payment_method.sh <applicantId> <payload.json>`
6. **Report the result honestly.** The import returns
   `{successCount, errorCount, errors[]}` and **is partially successful by
   design** — a non-zero `errorCount` does not fail the HTTP call. Always
   surface `errorCount` and the first few `errors[]` entries; never report
   "imported" on the strength of a 200.

## Compact spec — import

```yaml
# Defaults applied to every entry unless overridden per address
defaults:
  asset: BTC          # optional — currency code
  chain: BTC          # optional — network

addresses:
  - walletAddress: "bc1qmdld6jk0r3tvh39yqmet790t5vl3up2rcfzh0d"
  - walletAddress: "0x7DF6AF1C17AC9F86F8B3FBBC25253B8B5DF2F3A1"
    asset: ETH
    chain: ETH
  # privacy-preserving variant — see below
  - walletAddressHash: "9f2c...64"
```

| Field | Required | Notes |
|---|---|---|
| `walletAddress` | one of the two | The plain address. |
| `walletAddressHash` | one of the two | Use when you do not want to send the address itself. |
| `asset` | no | Currency code, e.g. `BTC`, `ETH`, `USDT`. |
| `chain` | no | Network, e.g. `BTC`, `ETH`, `TRX`. |

📘 **Either `walletAddress` or `walletAddressHash` must be present.** If you
send **both**, the server recomputes the hash from the address and rejects the
entry when they disagree — so only send both if you are deliberately verifying
your own hashing. When in doubt, send just `walletAddress`.

📘 The `source` field on the entry is ignored — the server stamps imported
addresses as `api` regardless. That matters: only addresses whose source is
`api`, `dashboard`, a previously confirmed exchange, or a registered payment
method are trusted for automatic ownership confirmation. Addresses Sumsub
merely inferred (from attribution or from your transaction data) are not.

## Compact spec — payment method

```yaml
externalId: "wallet-btc-user-001"   # optional, your own identifier
data:
  type: cryptoWallet                 # cryptoWallet | bankCard | bankAccount | eWallet | other
  accountIdentifier: "bc1qmdld6jk0r3tvh39yqmet790t5vl3up2rcfzh0d"
  fullName: "John Smith"             # the holder, as you know them
  currencyCode: "BTC"
  cryptoChain: "BTC"
  memo: ""                           # for chains that use one (XRP, XLM, …)
```

`data.type` is required and must be one of the enum values above; for Travel
Rule purposes it is always `cryptoWallet`. `accountIdentifierHash` may be sent
instead of `accountIdentifier` on the same terms as the import.

The `applicantId` goes in the **path**, not the body — it is Sumsub's internal
applicant id, not your `externalUserId`. If the user only has an
`externalUserId`, resolve it first via
`GET /resources/applicants/-;externalUserId={externalUserId}/one`.

## Outputs

- **import** — `successCount`, `errorCount`, and `errors[]` where each entry
  carries the failing address (or hash) and a reason. Report the counts and
  the distinct reasons, not a raw dump of 10 000 rows.
- **payment method** — the persisted payment-method instance, including its
  server-assigned id.

## Worked examples

- [`examples/deposit-addresses.json`](examples/deposit-addresses.json) — a small multi-chain import.
- [`examples/withdrawal-addresses.json`](examples/withdrawal-addresses.json) — the direction integrations forget; same shape, different addresses.
- [`examples/hashed-only.json`](examples/hashed-only.json) — registering by hash without disclosing the addresses.
- [`examples/payment-method-crypto.json`](examples/payment-method-crypto.json) — one address bound to one applicant.

## See also

- [`references/wallet-address-schema.md`](references/wallet-address-schema.md) — field-by-field schema, source-type precedence, error shapes.
- [`sumsub-integrate-travel-rule`](../sumsub-integrate-travel-rule/SKILL.md) — the flow this data feeds.
- Sumsub docs: [Wallet Address Book](https://docs.sumsub.com/docs/wallet-address-book), [Travel Rule settings](https://docs.sumsub.com/docs/travel-rule-settings#confirmation-ownership-mode).
