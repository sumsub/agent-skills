# Unhosted wallet verification — flow reference

## Where it starts

During Travel Rule processing, Sumsub looks up the counterparty address. If no
VASP is attributed, the exchange is closed as `counterpartyVaspNotFound` and
the destination is treated as unhosted.

At that moment, **if the account has the "TR SDK on transaction" setting
enabled**, Sumsub also creates a verification applicant action against the
transaction, so the user can be asked to prove ownership. With the setting off,
no action appears and the transaction is simply left to the rules.

That setting is the main reason two accounts behave differently on the same
transfer. Check it before concluding that verification "doesn't work".

## Sequence

```
attribution finds no VASP
        │
        ├─ TR status → counterpartyVaspNotFound
        │
        ├─ setting on?  ── no ──▶ rules decide; no user interaction
        │        │
        │       yes
        │        ▼
        │  verification action created on the transaction
        │        │
        ▼        ▼
 you generate an SDK link ──▶ user proves ownership in the SDK
        │                              │
        │                    signature | form | micro-transaction
        │                              ▼
        │                       ownership check produced
        ▼                              │
 applicantKytTxnAwaitingUser ◀─────────┘ (while waiting)
        │
        ▼
 transaction re-scored → approved / on hold / rejected
```

## Settings that gate it

| Setting | Effect |
|---|---|
| TR SDK on transaction | Whether the verification action is created automatically when no VASP is found |
| Unhosted-wallet verification methods | Which proofs the user is offered: `websdkSignature`, `selfDeclaration`, `satoshiTest`, `manualReview` |
| Unverifiable wallet handling | What happens when the wallet cannot be verified: `holdForReview`, `selfDeclaration`, `reject` |
| Minimum amount for unhosted-wallet verification | Below this, verification is skipped. **Falls back to the Travel Rule threshold when unset.** |

All are account-level, set during onboarding or in the dashboard. None is
settable over the public API, so an agent's job is to read the consequences,
not to change them.

## The amount threshold trap

Both thresholds — Travel Rule and unhosted-wallet — are compared against
`info.amountInDefaultCurrency`. The comparison only runs when that field is
present. Omit it and neither threshold applies: verification is attempted for
every transfer regardless of size.

The value is computed once at ingest and stored, so a wrong conversion is
frozen on the record. Send `amountInDefaultCurrency` and `defaultCurrencyCode`
explicitly when you know them.

## Webhooks

| Event | Meaning here |
|---|---|
| `applicantKytTxnAwaitingUser` | Waiting on **your own user** to complete verification. Not a counterparty signal — this is the most-misread event in the whole Travel Rule surface. |
| `applicantKytOnHold` | Sent for manual compliance review on your side. |
| `applicantKytTxnApproved` / `applicantKytTxnRejected` | The re-scored verdict once verification resolves. |
| `applicantActionPending` / `applicantActionReviewed` | The action-level lifecycle, if you subscribe to it. |

## Reading the outcome

`GET /resources/api/applicantActions/{actionId}/checks/latest?type=WALLET_OWNERSHIP_CHECK`

Judge on the check's answer. Two things not to assume:

- **A green ownership check is not an approved transaction.** It says the user
  proved control of the address; your rule bundle still decides what an
  unhosted destination means for the transfer.
- **No check is not a failed check.** If the account offers only
  `manualReview`, nothing automated is ever produced.

## Manual verification

`POST /resources/api/applicantActions/{actionId}/unhostedWallet/manualVerify`

Only valid on a payment-method action; anything else is rejected with an
explicit message. The effect is durable — the address becomes trusted for
future ownership matching — so it belongs behind the same controls as any other
compliance override.

## What is not in the public API

- Setting the verification methods, the unverifiable-wallet handling, or either
  threshold — dashboard only.
- The nonce / signature / questionnaire endpoints the SDK itself uses. They are
  scoped to an SDK access token, not an App Token, and are not a backend
  integration surface.
