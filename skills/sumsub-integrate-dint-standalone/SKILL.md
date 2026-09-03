---
name: sumsub-integrate-dint-standalone
description: >-
  Add Sumsub Device Intelligence (the Fisherman JS module) to your own web
  pages where there is NO Sumsub verification widget — login, signup, password
  reset, 2FA, checkout, or any high-value action you want fraud-screened.
  TRIGGER when the user asks to "add device intelligence to login / signup",
  "fingerprint the device on a custom page", "use Fisherman standalone /
  self-hosted", "ongoing monitoring of platform events", "pre-KYC device
  check", "detect multi-accounting at signup", or "send a financial transaction
  with the captured device". Covers the whole loop — behavior access token,
  @sumsub/fisherman init + fingerprint, confirming the event (platform event /
  financial transaction / create-applicant), reading results, sandbox, go-live.
  SKIP when the page already embeds the Sumsub WebSDK — Device Intelligence
  rides along inside it, use `sumsub-integrate-dint-websdk`.
allowed-tools: Read, Write, Bash
---

# Sumsub — Device Intelligence standalone (no WebSDK)

Run **Device Intelligence (DI)** on your own pages that have no Sumsub
verification widget — logins, signups, password resets, 2FA, checkouts. You
embed the **Fisherman** JS module (npm `@sumsub/fisherman`) directly, capture
the device on a user action, and confirm the action to Sumsub so it can screen
for device fraud (bots, emulators, VPN/proxy, reused devices, multi-accounting).

This is Sumsub's **ongoing-monitoring / pre-KYC** path. If your page already
shows the Sumsub WebSDK, stop — DI is built into it, use
[`sumsub-integrate-dint-websdk`](../sumsub-integrate-dint-websdk/SKILL.md) instead.

## ⚠️ Sandbox tokens only

Do **not** accept or use a production App Token / secret during integration
work. Insist on a **sandbox** pair from
<https://cockpit.sumsub.com/checkus/home?sbx=true> — **Connect Sumsub to
your AI agent** -> **Build & configure** -> **Generate token**. Token + secret
are revealed once at creation; copy both before closing the dialog. The curl recipes here assume an
`sbx:` token; the preflight enforces it with an `sbx:` prefix check. Deeper auth
mechanics: [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md).

## Before you start — fit DI into the existing app

DI should look like it was always part of their codebase — their framework, their
components, their styling, their conventions. **Don't scaffold over someone's app**
or introduce a new design system. Read enough of the repo to match it, then ask only
what you can't infer:

- **Which action to screen?** The high-value submit to hook DI onto — login,
  signup, withdrawal, checkout, 2FA, password reset. (Show the ones you found in
  their routes/components as suggestions.)
- **Where's the backend?** The server file/route that can mint the behavior token
  and sign the Stage-3 confirm — HMAC **must** stay server-side. If they're
  frontend-only (SPA, no backend), flag that they need a server endpoint and offer
  to add a minimal one in their stack.
- **Existing Sumsub footprint?** Do they already call Sumsub / have App Token +
  secret wired, an `externalUserId` convention, a webhook receiver? Reuse it; don't
  duplicate.
- **How are secrets / env handled?** Match their existing pattern (`.env`, secrets
  manager, config service) for `SUMSUB_APP_TOKEN` / `SUMSUB_SECRET_KEY` — sandbox
  values only during integration.
- **TypeScript or JS?** Match the repo; don't add TS to a JS project or vice-versa.

Map the chosen action to its Stage-3 confirm event:

| Action | Stage-3 confirm event |
|---|---|
| Login / signup / password reset / 2FA | platform event |
| Money movement (transfer, withdrawal, deposit, payment) | platform event + financial txn |
| Pre-KYC signup where you also create the applicant | pre-KYC create-applicant |
| Guest / high-value checkout | financial txn |

Start with **Stage 0 (preflight)** to confirm the workspace has the DI entitlement
before writing any code. Then implement Stages 1–4 against *their* files: a token
route in their backend style, `fisherman.fingerprint()` on their existing submit
handler (fail-open), the server-side confirm with the event mapped from the chosen
action. Touch the minimum needed; follow surrounding code style.

## The loop in one picture

```
 ┌─────────────────────────────┐  ┌──────────────────────────────────────┐
 │ 1. Browser hits your page    │─▶│ Your backend: POST .../accessTokens/  │
 │    (login / signup form)     │  │ behavior {sessionId} → {token}        │
 └─────────────┬───────────────┘  └──────────────────────────────────────┘
               │ behavior access token
 ┌─────────────▼───────────────┐
 │ 2. Browser: @sumsub/fisherman│  ← init(token) → fingerprint() on submit
 │    captures the device       │     returns { visitorId }
 └─────────────┬───────────────┘
               │ user submits (login succeeds / account created)
 ┌─────────────▼───────────────┐  ┌──────────────────────────────────────┐
 │ 3. Your backend confirms the │─▶│ Sumsub runs DI analysis on the event  │
 │    event w/ captured device  │  │ (platform event / txn / applicant)    │
 └─────────────┬───────────────┘  └──────────────────────────────────────┘
               │ verdict + device signals
 ┌─────────────▼───────────────┐  ← Dashboard → Transactions (User
 │ 4. You read results / act    │     platform event); or webhook
 └──────────────────────────────┘
```

The headline: capturing the device is inert until you **confirm the event
server-side** (Stage 3). Capturing alone produces no verdict — the confirm call
is what makes Sumsub run the analysis.

## Vocabulary (get these right — they're load-bearing)

| Term | What it is | Who sets it |
|---|---|---|
| `sessionId` | **The correlation key.** Ties every fingerprint + event in one DI session together, and is the session the behavior token is minted with — so the Stage-3 confirm correlates the captured device to the event server-side, with no device fields in the body. | **Your backend** — generate one per logical session, opaque & unique. |
| `deviceBindingId` | Optional alternative linking id. Sumsub is migrating device linking from `sessionId` to `deviceBindingId`; on the default flow it is **not** required. If you use it: pass it to `fingerprint()`, mint the token with it, and send it at `applicant.device.deviceBindingId` in the confirm body. | **Your frontend** — a fresh `crypto.randomUUID()` per action. |
| `linkedId` | Optional — links the fingerprint to an entity (your user id / applicant id). | Frontend (optional). |
| `visitorId` | The device identifier `fingerprint()` returns; surfaces in results. On the standalone confirm flow you do **not** forward it — the token's session ties the capture to the event. | Returned by Fisherman. |

## Stage 0 — Preflight

[`scripts/preflight.sh`](scripts/preflight.sh) machine-validates the workspace
before you write any frontend code:

```bash
SUMSUB_APP_TOKEN=sbx:... SUMSUB_SECRET_KEY=... \
  bash scripts/preflight.sh
```

| Check | What it proves |
|---|---|
| `behavior_token` | HMAC signing is accepted **and Device Intelligence is enabled** for this workspace — mints a real short-TTL behavior token (discarded, expires on its own; nothing else is mutated) |
| `levels` | Verification levels exist. **WARN-only** — just the pre-KYC confirm path (create-applicant) needs one; platform events work without it |

Exit code: `0` on all-PASS / PASS+WARN, `10` on any FAIL. A `403` on
`behavior_token` usually means the **DI entitlement is off** for the
workspace — it's not self-serve; ask your CSM or `support@sumsub.com` to
enable Device Intelligence, mentioning your `clientId` (Dashboard top-left)
and environment (sandbox/production). Resolve all FAILs before Stage 1.

## Stage 1 — Backend: mint a behavior access token

Separate endpoint from the WebSDK token — note the `/behavior` suffix and the
JSON body:

```
POST https://api.sumsub.com/resources/accessTokens/behavior
Content-Type: application/json
{ "sessionId": "<your-session-id>", "ttlInSecs": 1800 }
```

- Auth: App Token + HMAC. **The body is part of the signature** — sign
  `ts + "POST" + path + body` (the empty-body shortcut from the WebSDK skill
  does not apply here). See [`examples/behavior-token.sh`](examples/behavior-token.sh).
- Response: `{ "token": "_act-jwt-..." }` — the JWT is the `token` field, **not**
  `accessToken`. (Behavior tokens carry no `userId`, unlike the WebSDK access-token endpoint.)
- TTL defaults to 1800s. Mint on demand per session; don't cache globally.

Wire it as an auth-gated route on your backend (e.g. `POST /api/di/token`) that
generates/looks up the `sessionId`, signs, calls Sumsub, and returns the response
`token` to the browser.

## Stage 2 — Frontend: capture the device with Fisherman

```bash
npm i @sumsub/fisherman --save
```

```ts
// Shape only — the full impl (fail-open try/catch, React StrictMode teardown) is in
// examples/fisherman-vanilla.html and examples/fisherman-react.tsx.
import { init, destroy } from '@sumsub/fisherman'

// init once when the page / form mounts — getBehaviorToken() calls your Stage-1 route
const fisherman = await init({
  token: await getBehaviorToken(),
  baseUrl: 'https://api.sumsub.com',          // region-specific API host
  accessTokenUpdateHandler: getBehaviorToken, // refresh near expiry
  onError: () => destroy(),                   // never let DI block your form
})

// on the user action (e.g. login submit) — gate, fresh deviceBindingId, then confirm server-side
if (fisherman?.isDeviceIntelligenceEnabled) {
  const deviceBindingId = crypto.randomUUID()
  await fisherman.fingerprint({ deviceBindingId /*, linkedId: userId */ })
  // Fisherman posts the capture under the token's session — your Stage-3 confirm
  // call needs only the same accessToken to tie this device to the event.
}
destroy() // re-init for the next action
```

Rules:
- Gate `fingerprint()` on `isDeviceIntelligenceEnabled` — skip silently if DI is
  off for the workspace.
- A **fresh `deviceBindingId` per action**. Correlation of the capture to the
  confirm call is the token's `sessionId`, not this id — only the `deviceBindingId`
  migration path needs it echoed in the confirm body (Stage 3).
- DI must **never block your real flow** — wrap in try/catch, fail open.
- `destroy()` after the action; re-`init()` for the next one. Refresh tokens via
  `accessTokenUpdateHandler` (or call `updateAccessToken(newToken)` manually).

Runnable starting points: [`examples/fisherman-vanilla.html`](examples/fisherman-vanilla.html),
[`examples/fisherman-react.tsx`](examples/fisherman-react.tsx).

## Stage 3 — Backend: confirm the event with the captured device

Tell Sumsub the action happened; the captured device rides along via the token's
session. Pick the call that matches the action — all use your **standard App
Token + HMAC signing** (sign `ts + "POST" + path + body`, exactly like every other
Sumsub API call), and additionally carry the **behavior access token** as the
`?accessToken=` query param so Sumsub ties the captured device to the event. The
`accessToken` does **not** replace signing — it rides alongside it:

| Action | Endpoint | Doc |
|---|---|---|
| Login / signup / password reset / 2FA | `POST /resources/applicants/-/kyt/txns/-/data?accessToken=…` | [platform event](https://docs.sumsub.com/reference/send-applicant-platform-event-with-captured-device) |
| Financial transaction | `POST /resources/applicants/-/kyt/txns/-/data?accessToken=…` | [financial txn](https://docs.sumsub.com/reference/send-financial-transaction-with-captured-device) |
| Pre-KYC signup (create the applicant) | create applicant with `levelName` + `accessToken` + `externalUserId` | [pre-KYC check](https://docs.sumsub.com/reference/use-device-intelligence-for-pre-kyc-check) |

**How the device links:** the confirm call is App-Token + HMAC signed **and**
carries the **same behavior access token** as `?accessToken=`. Sumsub correlates
the captured fingerprint to the event **server-side using the session the token
was minted with** (it reconstructs the key from your `externalUserId`; the token
scopes the session). You do **not** put `visitorId` or a device block in the
body — just identify the user + the event:

```json
{
  "txnId": "<unique-id-you-generate>",
  "type": "userPlatformEvent",
  "applicant": { "externalUserId": "<your-user-id>", "type": "individual" },
  "userPlatformEventInfo": { "type": "login" }
}
```

Runnable: [`examples/submit-platform-event.sh`](examples/submit-platform-event.sh).
Financial-transaction and pre-KYC bodies + full field lists:
[`references/standalone-flow.md`](references/standalone-flow.md).

> `deviceBindingId`-based linking (Sumsub is migrating to it) is the exception:
> mint the token with a `deviceBindingId`, pass the same one to `fingerprint()`,
> and send it at `applicant.device.deviceBindingId`. The default flow keys on
> `sessionId` and needs none of that.

For **pre-KYC**, also add `creationTrackingData.ip` to the applicant if
you want Advanced IP verification, then request the applicant check to trigger
the DI analysis.

## Stage 4 — Read the results

- **Dashboard:** Transactions and Travel Rule → **Transactions**, filter by
  type **User platform event** → open the row → device details + risk labels.
- **Webhooks:** subscribe to the transaction/event reviewed webhooks to gate
  programmatically (same signature-verification rules as the WebSDK skill —
  verify on raw bytes).
- Device risk labels + scoring are the same catalog as the WebSDK path:
  [`references/standalone-flow.md`](references/standalone-flow.md). Full signal
  definitions are in the `sumsub-integrate-dint-websdk` skill's
  `references/device-signals.md` (install that skill for the file).

Decide which device labels are blocking (refuse / step-up) vs informational
(log) — that policy is yours.

## Sandbox testing

- Sandbox has no real device signals; Fingerprint is simulated. Use the
  `simulationConfig` (`FpSimulationConf`) option on `init` to force specific
  signals for deterministic test outcomes.
- Run the full loop in sandbox (token → fingerprint → confirm) and confirm a
  **User platform event** transaction appears in the dashboard.

## Going live checklist

- [ ] Backend mints the **behavior** token (`/accessTokens/behavior`), signing
  the **body**, with a unique per-session `sessionId`.
- [ ] Token endpoint is auth-gated (only your authenticated context can mint).
- [ ] Frontend fails open — a Fisherman error never blocks login/signup.
- [ ] Unique `sessionId` per session in the behavior token — it's what correlates
  the captured device to the confirm call (no device fields needed in the body).
- [ ] You confirm the event server-side (platform event / txn / applicant) so
  Sumsub actually runs the analysis — capturing alone produces no verdict.
- [ ] Results read from the dashboard / webhook, not from the browser.
- [ ] Production App Token + secret in the prod store; sandbox values stay in dev.

## See also

- [`sumsub-integrate-dint-websdk`](../sumsub-integrate-dint-websdk/SKILL.md) — DI when
  the page already embeds the Sumsub WebSDK widget.
- [`sumsub-integrate-websdk`](../sumsub-integrate-websdk/SKILL.md) — the base
  KYC WebSDK embed (token signing, webhook patterns reused here).
- [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md) — HMAC signing shared by every
  Sumsub skill.
- [`scripts/preflight.sh`](scripts/preflight.sh) — workspace validator (run
  before Stage 1).
- [`references/standalone-flow.md`](references/standalone-flow.md) — concepts,
  event types, result reading, pre-KYC and financial-txn variants.
- [Get started with Device Intelligence](https://docs.sumsub.com/reference/get-started-with-device-intelligence),
  [Generate access token](https://docs.sumsub.com/reference/generate-access-token-device-intelligence),
  [`@sumsub/fisherman`](https://www.npmjs.com/package/@sumsub/fisherman) — authoritative source if this skill drifts.
