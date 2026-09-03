---
name: sumsub-integrate-id-connect
description: End-to-end recipe for integrating Sumsub ID Connect — the OIDC-based "Verify with Sumsub ID" flow that lets a user share previously-verified identity claims with your app. TRIGGER when the user asks to "integrate Sumsub ID Connect", "add Verify-with-Sumsub-ID button", "reuse Sumsub KYC via OIDC", "exchange the Sumsub authorization code", "mint a Sumsub ID share token", or asks how to wire up `@sumsub/id-connect`, the OIDC `code → access_token` exchange (`/api/snsId/oauth/token`), the share-token / partner-consent flow, or the share-link redirect. Covers preconditions checklist, automated preflight, frontend button (library button + raw redirect alternative), backend code-for-token exchange, share-token minting, partner-consent shareLink flow, and applicant materialisation through `/resources/api/reusableIdentity/reuse`. SKIP for the standalone WebSDK / KYC widget (use `sumsub-integrate-websdk`), or for plain Reusable-KYC-via-API where the donor and recipient are both your own tenants without a user-mediated OIDC step.
allowed-tools: Read, Write, Bash
---

# Sumsub — ID Connect integration

Embed the "Verify with Sumsub ID" OIDC flow end-to-end — preconditions →
preflight → button → backend exchange → consent → applicant in your workspace.

## ⚠️ Sandbox tokens only

Do **not** use a production App Token / secret while wiring this up. Insist on
a **sandbox** pair from
<https://cockpit.sumsub.com/checkus/home?sbx=true> — **Connect Sumsub to
your AI agent** -> **Build & configure** -> **Generate token**. Token + secret
are revealed once at creation; copy both before closing the dialog. The preflight enforces this
with an `sbx:` prefix check.

Deeper auth mechanics: [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md).

## ⛔ Order of operations — do NOT scaffold an app first

This is the single most important rule of this skill. **Write no frontend or
backend code, create no demo project, scaffold nothing** until BOTH gates below
are green. The client-side Sumsub setup (Stage 0a) is manual and cannot be done
by you — jumping to code before it exists produces an app that can't
authenticate, can't redirect, and can't reuse. Always follow this sequence:

1. **Confirm Stage 0a preconditions with the user — one by one.** Do not assume
   any item is done. For each, ask the user whether it exists; if it doesn't,
   **stop and hand them the exact manual step and where to do it** (the support
   email template, the Dev Space → OIDC Settings registration, the App Token
   minting page, the level creation hand-off). These are Sumsub-dashboard /
   support actions only — there is no public API for them, so you cannot do them
   for the user. Wait until every item is confirmed before moving on.
2. **Run Stage 0b preflight and require exit 0.** Only after the preconditions
   are confirmed, run [`scripts/preflight.sh`](scripts/preflight.sh). Resolve
   every FAIL (loop back to Stage 0a as needed). Do not proceed on any FAIL.
3. **Only now build.** With both gates green, proceed to Stage 1 and scaffold
   the frontend/backend.

If the user says "just build the demo" before the gates are green, briefly
explain why it won't work yet and walk them through the missing precondition
first. The code is the *last* step, not the first.

## What ID Connect is (and isn't)

Sumsub ID Connect lets a business request specific verified identity claims —
age, name, nationality, email, country of residence, humanness — from a
**Sumsub ID** account belonging to the end-user. Sumsub hosts the entire
user-facing flow: sign-in, account creation (if needed), email OTP, any
missing verification steps, and a per-recipient consent screen. Your app
receives the result as a signed OIDC token plus, optionally, an applicant
materialised in your workspace through Reusable KYC.

This is **not** the WebSDK. The WebSDK runs a full KYC capture inside your
page; ID Connect delegates the whole UX to Sumsub.

## The lifecycle in one picture

```
 ┌──────────────────────────────┐
 │ Stage 0a Preconditions check │  manual setup on Sumsub side
 │ Stage 0b scripts/preflight.sh │  automated validation
 └──────────────┬───────────────┘
                │ clientId, levelName, allowlist
 ┌──────────────▼───────────────┐
 │ Stage 1: Frontend "Verify…"  │  authorize redirect with PKCE
 │   button                      │
 └──────────────┬───────────────┘
                │ onSuccess({ code, state })
 ┌──────────────▼───────────────┐
 │ Stage 2: code → access_token  │  POST id.sumsub.com/api/snsId/oauth/token
 │   (client_secret_basic)       │
 └──────────────┬───────────────┘
                │ access_token
 ┌──────────────▼───────────────┐
 │ Stage 3a: → share token       │  POST /resources/accessTokens/sumsubIdShareToken
 └──────────────┬───────────────┘
                │ sharingAllowed?
        ┌───────┴────────┐
        │ false           │
        ▼                ▼ true
 ┌──────────────────┐ ┌──────────────────────────────┐
 │ Stage 3b:        │ │ Stage 4: reuse/preview +     │
 │ shareLink        │ │   reuse/commit               │
 │ redirect + retry │ │ → applicant in your workspace │
 └────────┬─────────┘ └──────────────────────────────┘
          │
          └──────► back to Stage 3a (retry — now sharingAllowed: true)
```

## Endpoints

| METHOD | URL | Auth | Stage |
|---|---|---|---|
| (browser redirect) | `https://id.sumsub.com/api/snsId/oauth/authorize` | none | 1 |
| GET  | `https://id.sumsub.com/.well-known/openid-configuration` | none | 0b |
| GET  | `https://id.sumsub.com/.well-known/jwks.json` | none | (id_token validation) |
| POST | `https://id.sumsub.com/api/snsId/oauth/token` | `client_secret_basic` | 2 |
| POST | `https://api.sumsub.com/resources/accessTokens/sumsubIdShareToken` | App Token + HMAC | 3a |
| POST | `https://api.sumsub.com/resources/snsId/oauth/shareLink` | App Token + HMAC + Bearer | 3b |
| GET  | `https://api.sumsub.com/resources/api/reusableIdentity/reuse/preview` | App Token + HMAC | 4 |
| POST | `https://api.sumsub.com/resources/api/reusableIdentity/reuse` | App Token + HMAC | 4 |

The "Enable Sumsub ID Connect" toggle, OIDC client registration
(client_secret + redirect_uri allowlist), and sharing-partner registration
are **Sumsub dashboard UI only** — no public-API equivalent.

## Stage 0a — Preconditions checklist

Before any code or preflight, the following must already exist on the Sumsub
side. Each item maps to a check below or to a runtime failure if missed.

- [ ] **Sumsub support has enabled ID Connect for your workspace.** This is
      **not a self-serve toggle** — until support flips it, no OIDC client
      can be created and the preflight will report
      `connect_token: ID Connect not enabled for this workspace`. Email your
      CSM or `support@sumsub.com` first and wait for confirmation. Template:

      ```
      Subject: Enable Sumsub ID Connect for clientId <YOUR_CLIENT_ID> (sandbox)

      Hi Sumsub team,

      Please enable Sumsub ID Connect for our workspace.

        Environment:         sandbox
        clientId:            <YOUR_CLIENT_ID>          (Dashboard top-left)
        Intended scopes:     openid, share, name        (adjust as needed)
        Intended recipients: self                       (or list partner clientIds)
        Use case:            <one-line description of where the button will live>

      Once enabled we'll register the OIDC client + redirect URIs in
      Dev Space → OIDC Settings.

      Thanks
      ```

- [ ] **App Token + secret (sandbox).** Minted at
      <https://cockpit.sumsub.com/checkus/home?sbx=true> via **Connect
      Sumsub to your AI agent** -> **Build & configure** -> **Generate
      token**. Both values shown once at creation. → exported as
      `SUMSUB_APP_TOKEN` / `SUMSUB_SECRET_KEY`.
- [ ] **OIDC client registered** at Dashboard → Dev Space → OIDC Settings.
      Capture all three:
      - **`client_id`** (public — goes in the browser, used as `forClientId`
        for the share token in the common self-recipient case)
      - **`client_secret`** (shown ONCE at creation; if you lose it you must
        regenerate, which invalidates existing integrations). Required for the
        Stage 2 code→token exchange — keep it server-side only.
      - **`redirect_uri` allowlist** populated for BOTH callbacks (Sumsub
        matches byte-for-byte — trailing slash, casing, port, query all
        matter):
        - your authorize callback (e.g. `https://yourapp.com/auth/callback`)
        - your shareLink callback (e.g. `https://yourapp.com/share-complete`)
        Sumsub redirects the **browser** back to these URLs and requires
        public **HTTPS** — a bare `http://localhost:3000` won't work for local
        testing. To develop on your machine, expose your local server with a
        public HTTPS tunnel (ngrok) and allowlist *that* origin — see
        [Local development with ngrok](#local-development-with-ngrok) below.
- [ ] **At least one verification level** exists in this workspace. Capture
      `levelName`. If none, hand off to
      [`sumsub-create-level`](../sumsub-create-level/SKILL.md) first — Stage 4
      can't materialise an applicant without one.
- [ ] **At least one Sumsub ID account with verified data** for end-to-end
      testing. An email-only account (no completed KYC) makes Stage 4 fail
      with errorCode `10521 reusable-kyc-inactive-sumsub-id-account` — see
      the error table at the end of Stage 4.

## Stage 0b — Preflight

[`scripts/preflight.sh`](scripts/preflight.sh) machine-validates the
preconditions that can be probed without minting OIDC codes or creating
applicants. It does **not** mutate anything.

```bash
SUMSUB_APP_TOKEN=sbx:... SUMSUB_SECRET_KEY=... \
  bash scripts/preflight.sh
```

Checks (each independent — one failing doesn't abort the others):

| Check | What it proves |
|---|---|
| `connect_token`  | App-Token HMAC signing is accepted and ID Connect is enabled for the workspace — probes the endpoint with a known-bad code and expects `401 Invalid code` (a `404 invalid clientId` means ID Connect isn't enabled). This is a connectivity/entitlement probe, not the Stage 2 exchange route. |
| `oidc_discovery` | `https://id.sumsub.com/.well-known/openid-configuration` returns a valid OIDC discovery doc |
| `levels`         | At least one verification level exists in this workspace |

Exit code: `0` on all-PASS / PASS+WARN, `10` on any FAIL. Resolve all FAILs
before Stage 1.

## Local development with ngrok

ID Connect can't be tested against `http://localhost`. Sumsub redirects the
**browser** back to your `redirect_uri` after the authorize flow (Stage 1) and
after the shareLink consent flow (Stage 3b), and it requires the URL to be
public **HTTPS** and present in the OIDC client's `redirect_uri` allowlist
**byte-for-byte**. A bare `localhost` URL is neither public nor HTTPS, so the
redirect fails. For local development, put a public HTTPS tunnel in front of
your local server with [ngrok](https://ngrok.com/) and allowlist that origin.

1. **Start your backend locally** (the example listens on `PORT=3000`):

   ```bash
   PORT=3000 node examples/express-callback.js
   ```

2. **Open a tunnel to that port.** Prefer a **reserved (static) domain** so the
   URL survives restarts — a free random ngrok URL changes on every launch and
   forces you to re-edit the allowlist each time:

   ```bash
   ngrok http 3000 --domain=your-reserved-name.ngrok-free.app
   # or, ephemeral URL (changes each restart): ngrok http 3000
   ```

   ngrok prints a forwarding URL, e.g. `https://your-reserved-name.ngrok-free.app`.

3. **Allowlist BOTH callbacks at the ngrok origin** in Dashboard → Dev Space →
   OIDC Settings (sandbox workspace) — byte-for-byte, including trailing slash:

   ```
   https://your-reserved-name.ngrok-free.app/
   https://your-reserved-name.ngrok-free.app/share-complete
   ```

4. **Point the app at the public URL, not localhost.** The browser's
   `redirect_uri` and the server-side shareLink `redirectUri` must derive from
   the *same* public origin, so set `PUBLIC_BASE_URL` and restart:

   ```bash
   PUBLIC_BASE_URL=https://your-reserved-name.ngrok-free.app \
     PORT=3000 node examples/express-callback.js
   ```

   Then open the **ngrok URL** (not `localhost:3000`) in the browser so the
   `redirect_uri` it sends matches the allowlist.

> ⚠️ **Re-register on every URL change.** If you use an ephemeral ngrok URL,
> the allowlist entry (and `PUBLIC_BASE_URL`) must be updated each time ngrok
> restarts. A reserved domain avoids this churn.
>
> ngrok's free interstitial ("You are about to visit…") only affects API/XHR
> calls, not top-level browser navigation, so it doesn't block the OIDC
> redirects. A reserved domain or paid plan removes it entirely.

## Stage 1 — Frontend: the button

> ⛔ **Gate.** Do not start this stage until Stage 0a preconditions are all
> confirmed with the user AND Stage 0b preflight exits 0. If you haven't done
> both, go back — see "Order of operations" above. This is the first stage
> where you write code; everything before it is setup you must verify first.

### Architecture — what's yours vs Sumsub's

Sumsub provides: the OIDC service (`id.sumsub.com`), the HMAC API
(`api.sumsub.com`), and the optional `@sumsub/id-connect` JS library that
mounts the button.

**You write both halves** of the integration:

- **Frontend** (this stage) — page with the button. Generates PKCE, kicks
  off the OIDC redirect to `id.sumsub.com`, receives `?code=` in the
  callback, POSTs `{ code, codeVerifier }` to your own backend.
- **Backend** (Stages 2-4) — HTTP endpoint that your frontend POSTs to.
  Signs Sumsub API calls with your App Token + secret (which must NEVER
  reach the browser), orchestrates the chain `code → access_token →
  share token → reuse`, and returns the materialised applicant.

The two halves are coupled by one route name — `POST /api/sumsub/id-connect/exchange`
in the examples; rename to fit your routing. Reference pair (matched):
[`examples/oidc-button.html`](examples/oidc-button.html) (frontend) +
[`examples/express-callback.js`](examples/express-callback.js) (backend).
The backend is a thin orchestrator (~180 lines of Node/Express); port it to
your stack of choice — the wire format is identical regardless of language.

> ⚠️ **`onSuccess` is not a verification signal.** It only confirms the user
> finished the OIDC consent step and Sumsub issued an authorization code.
> The actual verification verdict comes from Stage 4 —
> `applicant.review.reviewStatus` in the `/reuse` response (immediate, if
> your recipient level runs no additional checks) or the `applicantReviewed`
> webhook (authoritative, for any level that runs post-reuse checks).
> **Never grant access or unlock features based on `onSuccess` firing.**

Three variants — use **Method 1 (`createButton`)** by default; the others
exist for design-system or no-bundler scenarios.

### Method 1 — pre-built button via `@sumsub/id-connect` (recommended)

```js
import { createButton } from '@sumsub/id-connect';

// PKCE helpers (S256 — full versions in examples/oidc-button.html).
const b64url = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf)))
  .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const sha256 = (s) => crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));

// Generate the PKCE pair yourself, store the verifier under YOUR key — Stage 2
// on the backend needs that verifier to exchange the code for an access token.
const verifier  = b64url(crypto.getRandomValues(new Uint8Array(32)));
const challenge = b64url(await sha256(verifier));
sessionStorage.setItem('myapp.pkce.verifier', verifier);

createButton({
  clientId:      '<your-client-id>',
  permissions:   ['openid', 'share', 'name'],
  container:     document.getElementById('button-container'),
  codeChallenge: challenge,                            // library uses YOUR challenge — skips its own PKCE gen
  loginHint:     'user@example.com',                   // optional, prefills the email field
  onSuccess: async ({ code, state }) => {
    const v = sessionStorage.getItem('myapp.pkce.verifier');
    await fetch('/api/sumsub/id-connect/exchange', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ code, codeVerifier: v, redirectUri: location.href }),
    });
  },
  onError: (err) => console.error('sumsub-id-connect error', err),
});
```

Why generate PKCE yourself: the Stage 2 token exchange needs the `verifier`.
If you let the library generate it, you depend on the library's internal
`sessionStorage` key (undocumented per minor version) to read it back in
`onSuccess`. Passing your own `codeChallenge` keeps the verifier under a key
you own. Same pattern works for Methods 2 and 3.

Runnable example: [`examples/oidc-button.html`](examples/oidc-button.html).

### Method 2 — your trigger + library modal

Same library, you own the trigger element; library opens the flow in an
overlay via `openModal({...})`. Use when your design system has its own
buttons.

Runnable example: [`examples/oidc-modal.html`](examples/oidc-modal.html).

### Method 3 — raw OIDC redirect (no library)

Direct navigation to the OIDC authorize endpoint, no Sumsub script on the
page. Reach for this when CSP forbids third-party scripts, you're in an
SSR-only environment, or you maintain a generic OIDC client across multiple
providers.

```
GET https://id.sumsub.com/api/snsId/oauth/authorize
  ?client_id=<your-client-id>
  &response_type=code
  &redirect_uri=<allowlisted URI>
  &scope=openid+share+name
  &state=<random CSRF nonce>
  &code_challenge=<base64url(SHA256(code_verifier))>
  &code_challenge_method=S256
  &login_hint=<optional email>
```

You generate the `code_verifier` (43–128 chars, URL-safe), derive
`code_challenge = base64url(SHA256(verifier))`, store the verifier
(`sessionStorage`), and forward it to your backend after the callback.
Sumsub only accepts `code_challenge_method=S256` (`plain` is rejected) and
the `redirect_uri` must match the allowlist **byte-for-byte**.

Runnable example: [`examples/oidc-redirect.html`](examples/oidc-redirect.html).

### Choosing scopes

Default `['openid', 'share', 'name']`. Add `email`, `profile`, or
`offline_access` (refresh token) only when downstream logic actually reads
them — extra scopes trigger extra checks in the user-facing flow. Full table:
[`references/scopes-and-claims.md`](references/scopes-and-claims.md).

## Stage 2 — Backend: code → access_token

Exchange the authorization code on the OIDC token endpoint. The code came from
the browser authorize flow, so its counterpart is the standard OIDC token
endpoint — authenticated with the OIDC `client_secret` (`client_secret_basic`),
**not** HMAC.

```
POST https://id.sumsub.com/api/snsId/oauth/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(<client_id>:<client_secret>)

grant_type=authorization_code
&code=<the code your frontend got>
&redirect_uri=<exact-match URI from Stage 1 — byte-for-byte>
&code_verifier=<PKCE verifier matched to the code_challenge from Stage 1>
```

Response (24-hour `access_token`):

```json
{
  "access_token":  "snd-id-con-a-...",
  "refresh_token": "snd-id-con-r-...",   // only with `offline_access`
  "token_type":    "Bearer",
  "expires_in":    86400,
  "id_token":      "eyJhbGc..."           // only with `openid` — RS256-signed
}
```

Refresh later via `grant_type: "refresh_token"`; you cannot request more
scopes on refresh than were granted at consent time.

> The `client_secret` stays server-side — never in the browser bundle. The
> exchange is `client_secret_basic` / `client_secret_post`; do **not** HMAC-sign
> it. (The App-Token + HMAC auth is still used in Stage 3a/4 for the share
> token and reuse calls.)

### Gotchas

- **`Invalid code` 401** has three common causes: PKCE mismatch (verifier
  doesn't hash to the challenge sent at authorize), code already used
  (single-use; refreshing the callback page double-fires), or code expired
  (short TTL — exchange immediately).
- **`redirect_uri` must match Stage 1 byte-for-byte** — trailing slash, casing,
  port and query all count, or the exchange fails.
- **`id_token` validation** — use a mature library (`jose`, `pyjwt`, `jjwt`)
  against the `jwks_uri` from `.well-known/openid-configuration`. Never trust
  unverified JWT contents.

## Stage 3 — Backend: access_token → share token + consent

Mint a share token scoped to a recipient (`forClientId`). **Always implement
the consent fallback (Stage 3b)** — `sharingAllowed: false` is returned
whenever the user hasn't yet authorised sharing with this specific
`forClientId`. In the common self-recipient case both consents are usually
granted in one click on the Stage 1 consent screen, but production code that
only handles `sharingAllowed: true` breaks the first time a user re-enters
the flow or a recipient configuration differs.

### Stage 3a — mint share token

```
POST https://api.sumsub.com/resources/accessTokens/sumsubIdShareToken
{
  "sumsubIdConnectToken": "<access_token from Stage 2>",
  "forClientId":          "<recipient clientId>",
  "ttlInSecs":            1800
}
```

`forClientId`:

- Self-recipient (common case): your own workspace `clientId`, visible in the
  Dashboard top-left.
- Third-party recipient: the partner's `clientId` (they must be pre-registered
  as a partner in the Dashboard).

Response:

```json
{
  "token":          "_act-snsId-...",
  "forClientId":    "<echoed>",
  "sharingAllowed": true    // or false → continue to Stage 3b
}
```

### Stage 3b — partner-consent shareLink

If `sharingAllowed: false`, mint a consent link and redirect the user:

```
POST https://api.sumsub.com/resources/snsId/oauth/shareLink
Authorization: Bearer <access_token from Stage 2>
X-App-Token + X-App-Access-Ts + X-App-Access-Sig

{
  "redirectUri": "<your shareLink callback URL — must be in the allowlist>",
  "forClientId": "<same recipient clientId>",
  "displayMode": "page",
  "state":       "<csrf-or-correlation-id>"
}
```

Response: `{ "link": "https://id.sumsub.com/share/<id>" }` — expires in 5
minutes.

Persist the `access_token` server-side keyed by `state` (in-memory Map is OK
for demos; use Redis / encrypted cookie / session table for prod). Redirect
the user to the `link`. After consent, Sumsub redirects back to `redirectUri`
as `?token=<JWT>` — a signed RS256 JWT whose **payload carries `state`**
(alongside `sharingAllowed: true` and `forClientId`).

> ⚠️ **`state` is inside the JWT payload, not a top-level `?state=` query
> param.** Decode the `token` JWT to read `state` back (verify its signature
> against the `jwks_uri` first), then look up the saved
> `access_token` by that `state`. Re-call Stage 3a — the share token now
> returns `sharingAllowed: true`. Decoded payload shape:
> `{ iss, sub, aud, iat, exp, sharingAllowed, state, forClientId }`.

Full reference implementation:
[`examples/express-callback.js`](examples/express-callback.js) (in-memory
`pendingShare` Map keyed by `state`, `/share-complete` handler).

## Stage 4 — Materialise the applicant

With a usable share token, create the applicant in your workspace. **Always
preview first.**

### Preview (no side effects)

```
GET https://api.sumsub.com/resources/api/reusableIdentity/reuse/preview
  ?shareToken=<token>
  &levelName=<your-level>
  &userId=<externalUserId>
```

Returns the same `ApplicantPublicDto` shape that `/reuse` would create — use
it to surface compatibility errors before committing.

### Commit (creates the applicant)

```
POST https://api.sumsub.com/resources/api/reusableIdentity/reuse
  ?shareToken=<token>
  &levelName=<your-level>
  &userId=<externalUserId>
```

`userId` is the **`externalUserId`** Sumsub stores on the applicant — stable
per real user, opaque to the user, tied to your auth system. Same rules as
WebSDK.

### Reuse error codes

All `400` responses include `errorCode` (integer) and `errorName` (kebab-case)
suitable for code branching. `401` is generic token validity — no `errorCode`,
just `description`.

| HTTP / errorCode | name | Cause | Action |
|---|---|---|---|
| 401 / — | `Token is invalid` | Share token expired (TTL exceeded), already consumed, or malformed | Re-mint via Stage 3a — call `/sumsubIdShareToken` again with the still-valid `access_token` |
| 400 / `10501` | `not-in-partners-list` | `forClientId` is not registered as a sharing partner of your workspace | Add the recipient as a partner in the Dashboard (Sumsub UI only — no public API) |
| 400 / `10502` | `invalid-partner-id` | The partner ID extracted from the share token is invalid | Re-check `forClientId`; re-mint share token against a real partner |
| 400 / `10503` | `invalid-share-token` | Share token is malformed or expired | Re-mint via Stage 3a |
| 400 / `10504` | `non-suitable-share-token` | Share token is not suitable for reuse at the given `levelName` (scope mismatch) | Re-mint share token with matching scope, retry against the same level |
| 400 / `10505` | `reusable-kyc-disabled` | Reusable KYC is disabled for this workspace | Contact Sumsub support to enable Reusable KYC for your workspace |
| 400 / `10506` | `reusable-kyc-not-reusable` | Generic fallback — donor doesn't meet reuse eligibility and no more specific reason matched | Inspect the donor in the Dashboard; pick a different donor or fall back to the WebSDK |
| 400 / `10507` | `reusable-kyc-not-approved-applicant` | Donor applicant is not in an approved state (pending / rejected / on-hold) | Wait for donor's KYC to be approved; use a donor with approved status |
| 400 / `10508` | `reusable-kyc-not-active-applicant` | Donor applicant is inactive (deactivated / blocked) | Use a different donor — reactivation is Sumsub-side |
| 400 / `10509` | `reusable-kyc-not-kyc-moderation-type` | Donor's source moderation type is not suitable for reuse | Donor needs standard KYC moderation; specialised flows aren't reusable |
| 400 / `10510` | `reusable-kyc-not-selfie-or-identity-doc` | Required selfie or identity document is missing on donor | Pick a level without that doc-set, or have donor re-verify |
| 400 / `10511` | `reusable-kyc-not-selfie-liveness` | Recipient level requires liveness; donor's selfie wasn't captured with liveness | Use a level without `videoRequired: passiveLiveness` on SELFIE, or have donor re-verify with liveness |
| 400 / `10512` | `reusable-kyc-not-req-doc-overlap` | Required document types don't overlap between donor and recipient levels | Pick a recipient level whose required docs are a subset of donor's |
| 400 / `10513` | `reusable-kyc-not-compatible-doc-type` | Recipient level requires document types the donor doesn't carry | Use a less strict level, or fall back to the WebSDK for full capture |
| 400 / `10514` | `reusable-kyc-not-actual-poi-date` | Donor's Proof of Identity is outdated and not valid for reuse | Donor must re-submit fresh POI, or relax recipient level's POI freshness window |
| 400 / `10515` | `reusable-kyc-not-actual-poa-date` | Donor's Proof of Address is outdated and not valid for reuse | Donor must re-submit fresh POA, or relax recipient level's POA freshness window |
| 400 / `10516` | `reusable-kyc-not-acceptable-age` | Donor doesn't meet the age criteria of the recipient level | No recovery — different user required |
| 400 / `10517` | `reusable-kyc-incompatible-capture-settings` | Capture settings (file upload vs live camera, etc.) mismatch between donor and recipient | Align recipient level's `captureParams` with what donor used, or have donor re-capture |
| 400 / `10518` | `reusable-kyc-email-mismatch` | Donor's email doesn't match the email already on the recipient applicant | Resolve duplicate-applicant collision — different `externalUserId`, or align emails |
| 400 / `10519` | `reusable-kyc-phone-mismatch` | Donor's phone doesn't match the phone already on the recipient applicant | Same as 10518 — resolve collision |
| 400 / `10521` | `reusable-kyc-inactive-sumsub-id-account` | Donor Sumsub ID account has no stored documents (email-only, KYC never completed) | Donor must complete full KYC on `id.sumsub.com` first; for testing, use a Sumsub-provided verified test account |

After the applicant is materialised, your `applicantReviewed` webhook is the
authoritative signal for verification outcome — wire it up the same way as
for the WebSDK. See
[`sumsub-integrate-websdk`](../sumsub-integrate-websdk/SKILL.md) for the
webhook material and
[`sumsub-manage-webhooks`](../sumsub-manage-webhooks/SKILL.md) for the
sandbox webhook subscription setup.

## Going-live checklist

When the user says "we're ready for prod":

- [ ] Sumsub support has enabled Sumsub ID Connect for the **production**
      `clientId` (separate from sandbox).
- [ ] Production `redirectUri`s (both authorize and shareLink callbacks) are
      in the Dashboard allowlist on the prod workspace.
- [ ] Backend token-exchange endpoint is auth-gated (only the authenticated
      user can exchange a code minted *for them*).
- [ ] `id_token` signature is verified against the prod JWKS.
- [ ] `externalUserId` is stable per real user (not email, not display name).
- [ ] `/reuse/preview` is called before `/reuse` so compatibility errors
      surface as UX, not 4xx noise.
- [ ] Stage 3b shareLink flow is implemented and tested — don't ship code
      that only handles `sharingAllowed: true`.
- [ ] In-memory state used for the shareLink callback is replaced with a
      real session store (Redis / encrypted cookie / DB).
- [ ] App Token + secret + OIDC `client_secret` are in the prod secret
      store, not committed and not in browser bundles.
- [ ] Refresh-token storage (if used) is server-side only, encrypted at
      rest, single-tenant.

## See also

- [`references/scopes-and-claims.md`](references/scopes-and-claims.md) — full
  scope table, token-endpoint response shape, error codes.
- [`scripts/preflight.sh`](scripts/preflight.sh) — preconditions validator.
- [`examples/oidc-button.html`](examples/oidc-button.html) — Method 1
  (`createButton`) — recommended.
- [`examples/oidc-modal.html`](examples/oidc-modal.html) — Method 2
  (`openModal`).
- [`examples/oidc-redirect.html`](examples/oidc-redirect.html) — Method 3
  (raw OIDC redirect with PKCE).
- [`examples/express-callback.js`](examples/express-callback.js) — full
  backend (Stages 2-4 incl. Stage 3b consent flow).
- [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md) — auth signing reference.
- [`sumsub-create-level`](../sumsub-create-level/SKILL.md) — when the workspace
  has no recipient level yet.
- [`sumsub-integrate-websdk`](../sumsub-integrate-websdk/SKILL.md) — sibling
  skill; reuse its webhook material once the applicant is materialised.
