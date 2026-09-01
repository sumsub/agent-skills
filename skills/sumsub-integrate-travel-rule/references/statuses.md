# Travel Rule statuses

`travelRuleInfo.status` describes the state of the **data exchange** — not the
review answer your rules produced, and not the blockchain transfer. Three
statuses are open; the other ten are final and will not move again.

## Open

| Status | Meaning | What moves it |
|---|---|---|
| `awaitingCounterparty` | Delivered; waiting on their answer | Their response, or the timeout |
| `onHold` | Waiting on the answering side — the address to be confirmed, participant data, or a compliance review | The answer, a compliance decision, or the timeout |
| `completed` | The data exchange succeeded; the transfer is not linked yet | Linking the blockchain transaction, or cancelling |

## Final

| Status | Meaning |
|---|---|
| `finished` | The blockchain transaction was linked. The fully successful end state. |
| `cancelled` | Abandoned — either the sender cancelled after `completed`, or the sender's own rules rejected the transfer outright before the request went out. |
| `expired` | No answer within the requesting party's confirmation timeout. |
| `unconfirmedOwnership` | The wallet was declared not to belong to the expected VASP or organisation. |
| `counterpartyMismatchedData` | The counterparty reported that participant data did not reconcile. |
| `counterpartyVaspGeneralDecline` | Declined without a more specific reason. |
| `counterpartyVaspNotFound` | No VASP attributable to the address; treated as an unhosted wallet. |
| `counterpartyVaspNotReachable` | Identified, but no protocol you both support. Sumsub still emails them (production only) and records the attempt under **Events → Emails**. |
| `notEnoughCounterpartyData` | Insufficient data to build a valid message. On an exchange you started this is Sumsub validating **your** payload, not a counterparty decline. |
| `notApplicable` | Deliberately skipped by your configuration — below your minimum amount threshold, or the counterparty is excluded as not-a-VASP. |

A deprecated `counterpartyUnconfirmedOwnership` still appears on transactions
created before 2025. Treat it as `unconfirmedOwnership`.

## Where an exchange starts

**If you started it,** normally `awaitingCounterparty`. Four outcomes are
assigned immediately instead, without ever waiting on anyone, and all four are
final: `counterpartyVaspNotFound`, `counterpartyVaspNotReachable`,
`notEnoughCounterpartyData`, `notApplicable`.

**If you are answering,** the request arrives at `onHold` and stays there until
you answer. Note that on this side `onHold` means ownership is *not* yet
confirmed — the opposite of what it means on the initiating side.

## Transitions

- `awaitingCounterparty` → `onHold` when your own compliance review holds the transfer
- `awaitingCounterparty` | `onHold` → `completed` when both sides have what they need
- `awaitingCounterparty` | `onHold` → `expired` on timeout — **the only two statuses that can expire**
- `awaitingCounterparty` | `onHold` → `unconfirmedOwnership` | `counterpartyMismatchedData` | `counterpartyVaspGeneralDecline` on a decline
- `awaitingCounterparty` → `cancelled` when your own rules reject the transfer before the request goes out
- `completed` → `finished` when the blockchain transaction is linked
- `completed` → `cancelled` when the sender abandons the transfer

## Reaching `finished`

| Your situation | What reaches `finished` |
|---|---|
| You started the exchange **before** settlement | **You do it** — `PATCH /resources/kyt/txns/{id}/data/info` with the hash in `paymentTxnId` |
| You started the exchange **after** settlement | Automatic — the hash was supplied at creation |
| You **answered** someone else's request | Automatic — the hash reaches you from the initiator |

Only the first row needs code. In the other two, do not poll and do not call
the update method to force it.

## Status vs review answer

The Travel Rule status says what happened in the exchange. The review answer —
delivered as `applicantKytTxnApproved` / `applicantKytOnHold` /
`applicantKytTxnRejected` — says whether your organisation should proceed.
They are independent, and the mapping between them is entirely decided by the
rule bundle you installed. The platform has no default: if you need a specific
outcome for counterparties that never respond, install a rule for it.

📘 `applicantKytTxnAwaitingUser` means the transaction is waiting on **your own
user**, typically to complete wallet ownership verification. It does not mean
you are waiting on the counterparty.

## Expiry

When the confirmation timeout elapses, Sumsub sets the exchange to `expired` on
both sides and re-scores the transaction against each party's own rules. What
the counterparty does next is their configuration, not ours — many install a
rule that rejects transfers whose counterparty did not respond.

## Transactions with no status at all

A Travel Rule transaction can occasionally carry no status. This is not a stage
of the lifecycle and not a state to handle — the exchange did not get far
enough to be assigned one. Do not retry; report the transaction ids to Sumsub
support, since the cause is usually account configuration.
