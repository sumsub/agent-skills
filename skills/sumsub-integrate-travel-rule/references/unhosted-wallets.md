
# Unhosted wallets — verification when no VASP is attributed

When Travel Rule attribution finds no VASP behind an address, the exchange ends
at `counterpartyVaspNotFound` and the destination is treated as an **unhosted
wallet** — one the user themselves controls. There is no counterparty to
exchange data with, so the question changes from *who is the other VASP?* to
*does this wallet really belong to your user?*

This is not a rare branch. On a typical account it is the largest single
outcome by volume, so an integration that handles only the VASP-to-VASP path
handles a minority of its traffic.

## Where your code actually sits

Read this before planning work — most of the flow is not yours to build.

| Step | Who does it |
|---|---|
| Deciding which proof methods are offered | Configured on the account, not called over the API |
| Creating the verification action | Sumsub, automatically, when no VASP is attributed |
| Collecting the proof from the user | The SDK — signature, form, or micro-transaction |
| Judging the proof | Sumsub |
| **Handing the user a link to the SDK** | **You** |
| **Reading the outcome and gating the transfer** | **You** |
| **Overriding with a manual verdict** | **You**, optionally |

So the integration is: generate a link, wait for a webhook, read a result. If
you find yourself writing signature-verification code, stop — that is the
SDK's job.

## The four proof methods

Configured per account (during onboarding or in the dashboard), not selectable
per request:

| Method | What the user does |
|---|---|
| `websdkSignature` | Signs a nonce with the wallet's private key, in the SDK |
| `selfDeclaration` | Fills in a declaration form asserting ownership |
| `satoshiTest` | Sends a micro-transaction from the wallet |
| `manualReview` | Nothing — the transaction is held for a human on your side |

And a separate setting decides what happens when the wallet **cannot** be
verified: hold for review, fall back to a self-declaration form, or reject.

📘 Which methods are active changes what the user sees, and you cannot override
it per transaction. If the user wants a different mix, that is a settings
change — direct them to Travel Rule settings, do not try to force it through
the API.

## Its own amount threshold

Unhosted-wallet verification has a **separate minimum amount** from the Travel
Rule threshold. When it is unset, it falls back to the Travel Rule threshold
for backward compatibility — so the two are easy to confuse.

🚧 Both are compared against `info.amountInDefaultCurrency`. If you do not send
that field, **neither threshold is evaluated** and verification is attempted
regardless of amount. See [`sumsub-resolve-currency`](../../sumsub-resolve-currency/SKILL.md).

## Endpoints

| Verb | Path | Purpose |
|---|---|---|
| `POST` | `/resources/tr/sdk/init` | Generate a WebSDK link + token so the user can prove ownership. |
| `GET` | `/resources/applicantActions/-;applicantId={applicantId}` | List the applicant's actions, to find the verification one. |
| `GET` | `/resources/applicantActions/{actionId}/one` | Read one action and its status. |
| `GET` | `/resources/api/applicantActions/{actionId}/checks/latest?type=WALLET_OWNERSHIP_CHECK` | The ownership check result. |
| `POST` | `/resources/api/applicantActions/{actionId}/unhostedWallet/manualVerify` | Mark the wallet verified by hand. |
| `PATCH` | `/resources/kyt/txns/{id}/applicantWalletAddress` | Correct the address on the transaction. |

## Auth — App Token + secret (sandbox only)

Signing per [the authentication reference](https://docs.sumsub.com/reference/authentication);
mechanics in [`sumsub-api-auth`](../../sumsub-api-auth/SKILL.md).

> **⚠️ Sandbox tokens only.** `manualVerify` asserts that a real user owns a
> real wallet and feeds the Wallet Address Book, which changes how later
> transfers are judged. Refuse production tokens; get a sandbox pair at
> <https://cockpit.sumsub.com/checkus/home?xSNSEnv=sbx>. The helper scripts
> reject tokens without an `sbx:` prefix.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` |
| `SUMSUB_SECRET_KEY` | The paired secret. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

## Procedure

1. **Confirm this is the unhosted path.** The transaction's Travel Rule status
   is `counterpartyVaspNotFound`, and the review is waiting rather than
   finished. If a VASP *was* found, you are in the wrong skill.
2. **Find or create the verification action.** When the account has the
   TR-SDK-on-transaction setting enabled, Sumsub creates the action itself as
   soon as attribution fails — list the applicant's actions with
   `${CLAUDE_SKILL_DIR}/scripts/get_applicant_actions.sh <applicantId>` before
   creating anything. Otherwise generate a session with
   `${CLAUDE_SKILL_DIR}/scripts/tr_sdk_init.sh <spec.json>`.
3. **Hand the link to the user.** The response carries a WebSDK `link` and a
   `token` with a TTL. Deliver it however you already reach users; do not embed
   the App Token anywhere near it.
4. **Wait for the outcome.** `applicantKytTxnAwaitingUser` means the
   transaction is waiting on **your own user** — not on a counterparty. That is
   the signal the verification is outstanding. When it resolves, the
   transaction is re-scored and you get the usual approved / on-hold /
   rejected event.
5. **Read the verdict** with
   `${CLAUDE_SKILL_DIR}/scripts/get_latest_check.sh <actionId>` and gate the
   transfer on it — not on the browser telling you the user finished.
6. **Only if your policy allows it,** override with
   `${CLAUDE_SKILL_DIR}/scripts/manual_verify.sh <actionId>`.

## `POST /resources/tr/sdk/init` — the spec

```yaml
userId: "user-001"        # REQUIRED — your externalUserId; the applicant must already exist
levelName: "..."          # optional — defaults to the Travel Rule SDK level
ttlInSecs: 1800           # optional — link lifetime
txnInfo:                  # REQUIRED — the transfer being verified
  txnId: "wd-2026-05-21-1" # your own reference, NOT the on-chain hash
  amount: 0.075
  currencyCode: "BTC"
  cryptoChain: "BTC"
  direction: "out"
  counterpartyWalletAddress: "bc1q..."
  applicantWalletAddress: "bc1q..."
  memo: ""
```

Returns `{ link, token, ttlInSecs }`.

🚧 Two constraints that produce confusing errors:

- **The user must already exist as a Sumsub applicant** — the call resolves
  `userId` as an `externalUserId` and fails if there is none.
- **`txnId` is your reference, not the blockchain hash.** There is no field for
  the on-chain hash here at all, which means an SDK session always describes a
  transfer that has not settled yet. A duplicate `txnId` is rejected.

## Manual verification — treat as an exception

`manualVerify` marks the wallet verified on your say-so. It only applies to a
payment-method action; called on anything else it fails.

🚧 The effect outlives the transaction: a manually verified address is trusted
for future matching. Use it for genuine operational cases — a user who cannot
sign, a wallet already verified through another channel — with an audit trail
on your side. It is not a way to clear a queue.

## Reading the result

`GET /resources/api/applicantActions/{actionId}/checks/latest?type=WALLET_OWNERSHIP_CHECK`
returns the check container. Judge on the check's own answer, and remember that
a green ownership check is not the same thing as an approved transaction — your
rules still decide what an unhosted destination means for the transfer.

📘 Absence of a check is not failure. If the account offers only
`manualReview`, no automated check is ever produced and the transaction simply
waits for a human.

## See also

- [the main skill](../SKILL.md) — the flow that leads here, and what `counterpartyVaspNotFound` means.
- [`sumsub-manage-wallet-address-book`](../../sumsub-manage-wallet-address-book/SKILL.md) — a verified address feeds ownership matching later.
- [`sumsub-resolve-currency`](../../sumsub-resolve-currency/SKILL.md) — why the thresholds may not be evaluated at all.
- [`unhosted-wallet-flow.md`](unhosted-wallet-flow.md) — the full sequence, settings that gate it, and the webhooks involved.
- Sumsub docs: [Unhosted wallet verification](https://docs.sumsub.com/docs/unhosted-wallet-verification), [Travel Rule settings](https://docs.sumsub.com/docs/travel-rule-settings).
