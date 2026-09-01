# Testing Travel Rule in Sandbox

Sandbox provides a **test VASP** — an ordinary Sumsub-hosted counterparty that
exists only in Sandbox and answers over the Sumsub protocol. You submit
transactions against it exactly as you would against a real counterparty.

Prerequisites are the same as production, plus: the account must be in Sandbox
mode, and your VASP must have the Sumsub protocol enabled. Configure Sandbox
the way you intend to configure production — if thresholds, ownership
validation mode and rules differ, the results will not predict production.

## A recommended order

Work outward from the success case, so that when something breaks you know
which change caused it.

1. **`completed`** — the success path. Confirm you receive the webhook and read the status correctly.
2. **`awaitingCounterparty`** — the waiting state. Disable your "wallet does not belong to the counterparty VASP" rule first, or the transaction is acted on before you can observe it.
3. **`unconfirmedOwnership`** — a decline. Check your integration treats it as final and does not retry.
4. **`counterpartyVaspNotReachable`** — identified but unreachable. Check you treat it as final.
5. **`counterpartyVaspNotFound`** — unattributed. Check your unhosted-wallet rules apply.
6. **`awaitingCounterparty` → `expired`** — the timeout. Set a short confirmation timeout, submit, wait it out.
7. **`completed` → `finished`** — finalisation. Submit, then send the hash. **Do not skip this one** — it is the step most integrations omit in production, and the only place you are likely to rehearse it.
8. **`completed` → `cancelled`** — abandonment. Submit, then cancel instead of finalising.

## Trigger values

The counterparty data you submit selects the scenario. Exactly one value is
guaranteed by the platform itself:

| Outcome | Counterparty wallet |
|---|---|
| `unconfirmedOwnership` | `0X7B1E4CFE1659FB2FF41E70C89BC03A92895C76FE` |

Any exchange naming that address as the counterparty wallet is declined with
`unconfirmedOwnership`, always, on every non-production environment and on
production Sandbox.

Every other scenario depends on how the test VASP's own Sandbox account is set
up at the time — which addresses it has registered, which applicant they belong
to, what its ownership validation mode is. Those values change without notice,
so do not hard-code them from any document, including this one.

Instead, drive the remaining scenarios from behaviour:

- **`completed`** — use an address the test VASP already knows. The Sandbox
  transaction list shows previous successful exchanges; reuse a counterparty
  address from one.
- **`awaitingCounterparty`** — any address the test VASP does not recognise.
  Disable your "wallet does not belong to the counterparty VASP" rule first, or
  the transaction is acted on before you can observe it.
- **`expired`** — the same, then set a short confirmation timeout and wait.
- **`counterpartyVaspNotReachable`** — name a VASP that supports no protocol
  you share; find one in the directory rather than pasting an id.
- **`counterpartyVaspNotFound`** — submit with no counterparty VASP and the
  counterparty payment method type set to `unhostedWallet`.
- **`finished` / `cancelled`** — reach `completed` first, then finalise or
  cancel.

**Read the status you actually got** rather than asserting the one you
expected. If a scenario does not reproduce, that is information about the test
account, not about your integration.

## After settlement

Use the same counterparty values but supply `info.paymentTxnId` at creation.
Scenarios 7 and 8 do not apply — the exchange finalises itself.

## Testing how you answer

You need a request to arrive on your account. Create one from the dashboard:
**Transactions and travel rule → Transactions → Create sample transaction →
Travel rule (simulate inbound transfer)**. Fill the transfer in as if it were
your own incoming transaction; the counterparty VASP field is filtered to test
VASPs and is required, as are both wallet addresses and the applicant's name.

Sumsub then creates the mirror image on the test VASP's account, and that
account starts a genuine exchange with you. A few seconds later the request
lands, indistinguishable from a real one, and you answer it with the two
responses.

🚧 **This step cannot be driven from the API.** The simulate endpoint accepts
dashboard authentication only, so an agent holding an App Token cannot create
the inbound request itself — a human has to click it. Everything after that
(reading the transaction, both responses) is ordinary API work.

## What is not reproducible in Sandbox

- **The VASP notification email** that accompanies `counterpartyVaspNotReachable`
  is never sent in Sandbox — the status is reproducible, the email is not.
- **Non-Sumsub protocols.** The interactive answering flow exists on the Sumsub
  protocol. Exchanges arriving over other protocols behave differently and are
  not exercised by this procedure.

## What to validate, for every scenario

- The transaction reaches the status you expected.
- Your webhook handler receives the full sequence, in order, and is idempotent — one exchange emits several events.
- Your system distinguishes open statuses from final ones and closes its records on the final ones.
- A failed webhook delivery raises an alert on your side.
