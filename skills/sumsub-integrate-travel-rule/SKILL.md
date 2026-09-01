---
name: sumsub-integrate-travel-rule
description: End-to-end recipe for integrating Sumsub Travel Rule — deciding which of the three exchange flows applies, identifying the counterparty VASP, submitting the transfer, reading the exchange status, finalising or cancelling it, answering requests other VASPs send you, handling the unhosted-wallet path when no VASP is attributed, and finding existing transactions (deduplication before after-settlement exchanges). TRIGGER when the user asks to "integrate / add / implement Travel Rule", "send Travel Rule data with a withdrawal", "collect Travel Rule data for a deposit that already arrived", "respond to / answer incoming Travel Rule requests", asks why their exchanges sit at `onHold` or `completed` and never reach `finished`, why counterparties never answer, how to test Travel Rule in Sandbox, about "unhosted / self-hosted / non-custodial wallet verification", "prove the user owns the wallet", "Satoshi test", what happens on `counterpartyVaspNotFound` or `applicantKytTxnAwaitingUser`, or to "find / search transactions", "check whether a transaction already exists for this hash". SKIP for building the transaction payload itself (use `sumsub-create-transaction`), for writing the scoring rules that act on the outcome (use `sumsub-create-kyt-rules`), for bulk-registering wallet addresses (use `sumsub-manage-wallet-address-book`), and for KYC/AML work unrelated to transfers between VASPs.
allowed-tools: Read, Write, Bash
---

# Sumsub — Travel Rule integration

Travel Rule is an exchange of participant data between two VASPs about one
transfer. Sumsub is the hub: you talk to Sumsub, Sumsub talks to the
counterparty over whichever protocol you both speak.

The integration is small. What makes it fail in production is that most
integrations build one half of it — they start exchanges but never finalise
them, or they answer the first question and not the second, and nothing in the
API complains. This recipe is organised around those omissions.

## ⚠️ Sandbox tokens only

Do **not** accept or use a production App Token here. Travel Rule acts on real
transfers and real counterparty VASPs, and a test exchange sent to a live
counterparty puts a real request in a real compliance queue. Insist on a
sandbox pair from <https://cockpit.sumsub.com/checkus/home?xSNSEnv=sbx> —
**Connect Sumsub to your AI agent** -> **Build & configure** -> **Generate
token**. Token + secret are revealed once; copy both before closing the dialog.

Deeper auth mechanics: [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md).

## The three flows

Everything starts with one question: **who creates the exchange, and has the
transfer already settled on-chain?**

```
                          who creates the exchange?
                  ┌────────────────────┬────────────────────┐
                  │        you         │   the counterparty │
   ┌──────────────┼────────────────────┼────────────────────┤
   │ not settled  │  ① before          │                    │
   │ yet          │    settlement      │   ③ you answer     │
   ├──────────────┼────────────────────┤     their request  │
   │ already      │  ② after           │                    │
   │ settled      │    settlement      │                    │
   └──────────────┴────────────────────┴────────────────────┘
```

| | ① before settlement | ② after settlement | ③ answering |
|---|---|---|---|
| Typical case | Your user is withdrawing | A deposit arrived with no data | Anything involving your user |
| `info.paymentTxnId` | empty | **required** | set by them |
| Blocking | yes — the withdrawal waits | no — funds already moved | their transfer waits on you |
| End state | `finished` after you link the hash | `finished`, automatically | `finished`, automatically |

📘 **Do not key your integration off `info.direction`.** It says which way the
money moves for the account you are looking at, and it is flipped between the
two sides of the same exchange. Who *created* the exchange is the distinction
that changes your code; direction is not.

⚠️ Flow ③ is not optional. Every VASP that starts exchanges also receives them,
and an unanswered request means your user's transfer is delayed or refused by
the counterparty's rules. Integrations that ship only ①/② are the single
biggest source of Travel Rule failures.

## Stage 0 — Preconditions

Check these before writing any code; each produces a confusing failure later.

1. **Travel Rule entitlement** on the tenant — verify with
   [`sumsub-check-permissions`](../sumsub-check-permissions/SKILL.md).
2. **Your organisation is linked to a VASP.** Without it, nothing starts and
   the error reads `Your organization is not yet linked to a VASP. Please
   contact your Customer Success Manager`. That is not a permissions problem
   and not retryable — relay it and stop. Linking is done by a Customer
   Success Manager, not over the API.
3. **A Travel Rule rule bundle is installed and active.** The bundle decides
   what each exchange outcome means for the transaction's review answer — the
   platform has no default opinion. See
   [`sumsub-create-kyt-rules`](../sumsub-create-kyt-rules/SKILL.md).
4. **Travel Rule settings** are configured: confirmation timeout, ownership
   validation mode, participant data settings.
5. **Webhooks** are subscribed and reaching you — see
   [`sumsub-manage-webhooks`](../sumsub-manage-webhooks/SKILL.md). The events
   that matter here: `applicantKytTxnCreated`, `applicantKytTxnApproved`,
   `applicantKytTxnRejected`, `applicantKytOnHold`,
   `applicantKytTxnAwaitingUser`, `applicantKytTxnDataChanged`.
6. **The Wallet Address Book has your addresses** — both the ones you receive
   on and the ones you send from. See
   [`sumsub-manage-wallet-address-book`](../sumsub-manage-wallet-address-book/SKILL.md).

## Stage 1 — Identify the counterparty VASP

This single step moves the success rate more than anything else in the
integration, and it is the one most often skipped.

### Option A — let the user pick (recommended)

Add a destination selector to the withdrawal screen and pass the chosen id as
`counterparty.institutionInfo.internalId`. Attribution is then skipped
entirely and the request goes straight to the counterparty.

```bash
# search the directory as the user types
GET /resources/vasps/-?q=binance&limit=20
```

- Search on `q` — people know brand names, not legal entities.
- If they pick a group rather than one of its regional entities, that is fine:
  Sumsub resolves the group down to the entities underneath it that can
  actually receive the request. Do not force a choice between subsidiaries.
- Hidden VASPs are excluded by default; test VASPs only exist in Sandbox, so
  no production filtering is needed.

Single VASP by id: `GET /resources/api/vasps/{id}/one`.

### Option B — send only the address

Sumsub attributes it against the wallet address databases, then asks the
Travel Rule protocols, then falls back to blockchain analytics providers. This
is the right fallback when the user cannot name their destination, but a
significant share of addresses cannot be attributed at all.

The two are not exclusive: offer the picker, allow proceeding without it.

## Stage 2 — Submit the transfer

Build and post the transaction with
[`sumsub-create-transaction`](../sumsub-create-transaction/SKILL.md) using
`type: travelRule`. Only two fields distinguish the flows:

| | before settlement | after settlement |
|---|---|---|
| `info.paymentTxnId` | omit | the on-chain hash |
| `counterparty.institutionInfo.internalId` | VASP id from Stage 1, when known | same |

📘 In flow ② check first that an exchange does not already exist for this
transfer — a duplicate puts two requests in the counterparty's queue. Query
`GET /resources/kyt/txns/query/-` walking the deduplication ladder — hash,
then address + asset, then amount + time window — and create the exchange only
when nothing comes back. Endpoint syntax, the ladder and helper scripts:
[`references/find-transactions.md`](references/find-transactions.md).

🚧 Sending a hash in flow ① turns it into an after-settlement exchange — the
counterparty is asked to authorise a transfer that already happened. Omitting
it in flow ② does the reverse. This one field decides the semantics.

## Currencies and chains

Two currency facts change Travel Rule behaviour, not just precision.

**A symbol is not an asset.** `USDT` and `USDC` each name more than a dozen
different assets in Sumsub's catalogue, and over a thousand symbols exist on
more than one chain. Send
`currencyCode` without `cryptoParams.cryptoChain` for one of those and the
lookup matches nothing at all, so the asset is unresolved and no conversion
happens.

**Thresholds are compared against `amountInDefaultCurrency`.** If that field is
absent, the Travel Rule threshold check is skipped entirely and the flow runs
regardless of amount — the same for the unhosted-wallet threshold. The value is
also frozen when the transaction is created, so a bad conversion needs a
backfill, not a re-read. Send `amountInDefaultCurrency` and
`defaultCurrencyCode` explicitly whenever you know them.

📘 The counterparty's protocol has its own asset vocabulary, and only a
minority of catalogue entries carry a mapping for any given protocol. An exotic
token with no mapping cannot be expressed in the
outgoing message and the exchange ends at `notEnoughCounterpartyData` before
delivery. Check vocabulary coverage before debugging the payload.

Resolving symbols, chains and aliases:
[`sumsub-resolve-currency`](../sumsub-resolve-currency/SKILL.md).

## Stage 3 — Read the outcome

Sumsub assigns a Travel Rule status, then your rules assign a review answer.
**They are different things** and readers conflate them constantly: a
transaction can be approved by your rules while its exchange sits at
`expired`. Gate your withdrawal on the review answer, and record the exchange
status for audit.

Read the transaction with
`${CLAUDE_SKILL_DIR}/scripts/get_transaction.sh <txnId>` (a signed curl — use
the scripts rather than hand-rolling HTTP so signing and encoding stay right).
Immediately after submission the exchange either waits or is already final:

| Outcome | Meaning |
|---|---|
| `awaitingCounterparty` | Delivered; waiting on their answer |
| `counterpartyVaspNotFound` | Nobody to ask — treated as an unhosted wallet. Usually the largest single outcome by volume; see [`references/unhosted-wallets.md`](references/unhosted-wallets.md) |
| `counterpartyVaspNotReachable` | Identified, but no shared protocol |
| `notEnoughCounterpartyData` | **Your payload** failed protocol validation — not their decline |
| `notApplicable` | Your configuration skipped it |

Full status list, transitions and which ones are final:
[`references/statuses.md`](references/statuses.md).

## Stage 4 — Finalise, or cancel

Only flow ① needs code here. Flows ② and ③ reach `finished` on their own.

```bash
# after you broadcast
${CLAUDE_SKILL_DIR}/scripts/finalize_txn.sh <txnId> <on-chain hash>
# → PATCH /resources/kyt/txns/{id}/data/info   { "paymentTxnId": "<on-chain hash>" }

# if the user abandoned the withdrawal instead
${CLAUDE_SKILL_DIR}/scripts/cancel_txn.sh <txnId>
# → POST /resources/api/tr/{id}/cancel
```

🚧 **This is the most-skipped call in the whole integration.** Without it the
exchange stops at `completed`, the counterparty can never reconcile the data
they hold against anything on-chain, and neither side has a complete record
for audit. Send the hash as soon as you broadcast.

Cancelling matters too: an abandoned exchange left open occupies the
counterparty's queue until it expires and records you as unresponsive.

## Stage 5 — Answer incoming requests

A request arrives as `applicantKytTxnCreated` on a transaction where **your
user is `data.applicant`** and the wallet to confirm is
`data.applicant.paymentMethod.accountId`. Fetch it with
`${CLAUDE_SKILL_DIR}/scripts/get_transaction.sh <txnId>`.

Answering is **two responses, in order.** The transaction tells you which it
still needs:

| Flag | `true` | `false` |
|---|---|---|
| `needMasking` | send response one | already answered — skip |
| `travelRuleInfo.needApplicantOwnershipConfirmation` | send response two | already answered — skip |

```bash
# response one — is this wallet ours?
${CLAUDE_SKILL_DIR}/scripts/confirm_ownership.sh <txnId> confirmed   # or unconfirmed
# → POST /resources/kyt/txns/{id}/ownership/confirmed

# response two — whose is it?
${CLAUDE_SKILL_DIR}/scripts/attach_applicant.sh <txnId> <applicantId>
# → POST /resources/kyt/txns/{id}/travelRuleOwnership  { "applicantId": "..." }
# an { "applicantParticipant": { ... } } body instead: attach_applicant.sh <txnId> - < body.json
```

🚧 **Order is load-bearing, and getting it wrong fails silently.** Response two
on its own returns 200 — but while `needMasking` is `true` the exchange is
pinned at `onHold` no matter what data you send, the counterparty never
receives an answer, and the request expires. Confirming the address is also
what unmasks the counterparty's data, so until response one lands there is
nothing to reconcile against.

📘 No waiting between them. Both calls return the updated transaction, so there
is nothing to re-read and no webhook to wait for.

If you see your transactions sitting at `onHold`, you are sending response one
and not response two.

### How long you have

**Seconds, not minutes.** The counterparty picks the confirmation timeout in
their own settings, and the shortest value on offer is currently **10
seconds** — the whole round trip, including webhook delivery and both calls,
not your thinking time. It is not shown on the transaction and varies by
counterparty, so design for the shortest rather than the typical.

Some protocols do not wait at all: the counterparty's system asks and expects
the answer inside the same request, so whatever Sumsub can determine from your
stored configuration at that instant *is* the answer. There is no window and
no opportunity to answer by hand.

🚧 That is why automation is not an optimisation here. A manual process cannot
cover the traffic, and you cannot tell in advance which kind of request is
arriving.

### Automating both responses

Automation does not replace the two responses — it pre-answers them, so
requests arrive with the flags already `false`.

| Register this | Pre-answers |
|---|---|
| Address in the Wallet Address Book | response one |
| Address as an applicant payment method | both |

Neither works unless the ownership validation mode allows reuse — one setting,
chosen in the dashboard. See
[Confirmation ownership mode](https://docs.sumsub.com/docs/travel-rule-settings#confirmation-ownership-mode)
and [`sumsub-manage-wallet-address-book`](../sumsub-manage-wallet-address-book/SKILL.md).

## Stage 6 — Test it in Sandbox

Sandbox provides a test VASP that answers like a real counterparty. Work
outward from the success case so that when something breaks you know which
change caused it, and rehearse the finalisation step specifically — it is the
one integrations omit in production.

Procedure, trigger values and what is *not* reproducible in Sandbox:
[`references/sandbox-testing.md`](references/sandbox-testing.md).

## Go-live checklist

- [ ] Organisation linked to a VASP; Travel Rule entitlement active
- [ ] Rule bundle installed **and activated**, with a deliberate decision for each exchange outcome
- [ ] Confirmation timeout set to the value you actually want
- [ ] Webhook endpoint receiving, and idempotent — one exchange emits several events
- [ ] Withdrawals: VASP picker wired, or a conscious decision to rely on attribution
- [ ] Withdrawals: the hash is sent after every broadcast, and cancellations are sent on abandonment
- [ ] Incoming: **both** responses implemented, in order, with the skip flags respected
- [ ] Incoming: answered automatically wherever possible; manual is the exception
- [ ] Wallet Address Book loaded with deposit **and** withdrawal addresses
- [ ] Your system distinguishes open statuses from final ones and closes records on the final ones
- [ ] A failed webhook delivery raises an alert on your side

## See also

- [`references/statuses.md`](references/statuses.md) — every status, what moves it, which are final.
- [`references/sandbox-testing.md`](references/sandbox-testing.md) — Sandbox procedure and trigger values.
- [`examples/withdrawal-before-settlement.json`](examples/withdrawal-before-settlement.json), [`examples/deposit-after-settlement.json`](examples/deposit-after-settlement.json) — transaction specs for `sumsub-create-transaction`.
- [`examples/answer-incoming-request.js`](examples/answer-incoming-request.js) — webhook handler implementing Stage 5 with the flags and ordering.
- [`references/unhosted-wallets.md`](references/unhosted-wallets.md) — the unhosted-wallet path: `POST /resources/tr/sdk/init`, reading the ownership check, manual verification; sequence details in [`references/unhosted-wallet-flow.md`](references/unhosted-wallet-flow.md).
- [`references/find-transactions.md`](references/find-transactions.md) — searching transactions and the dedupe ladder; operator and encoding details in [`references/query-syntax.md`](references/query-syntax.md).
- [`sumsub-resolve-currency`](../sumsub-resolve-currency/SKILL.md) — which `currencyCode` / `cryptoChain` to send, and why `amountInDefaultCurrency` matters here.
- Sumsub docs: [Travel Rule data exchange flows](https://docs.sumsub.com/docs/travel-rule-data-exchange-flows), [Travel Rule settings](https://docs.sumsub.com/docs/travel-rule-settings), [Wallet Address Book](https://docs.sumsub.com/docs/wallet-address-book), [Unhosted wallet verification](https://docs.sumsub.com/docs/unhosted-wallet-verification).
