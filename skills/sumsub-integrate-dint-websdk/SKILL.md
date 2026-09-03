---
name: sumsub-integrate-dint-websdk
description: >-
  Add Sumsub Device Intelligence (the Fisherman module) to a web project that
  already verifies users with the Sumsub WebSDK. TRIGGER when the user asks to
  "add device intelligence", "enable device capture / fingerprinting in the
  WebSDK", "turn on Fisherman", "detect device fraud / multi-accounting in the
  verification flow", or asks how device risk labels get onto an applicant
  verified through the WebSDK. Covers the whole loop — enabling Capture device data
  on the level, the automatic in-SDK Fisherman lifecycle, the advanced
  self-rendered wiring, reading device signals (Devices tab, Device Check,
  risk labels, webhooks), sandbox testing, go-live checklist. SKIP for device
  intelligence on pages with NO WebSDK widget (login / signup / checkout) — use
  `sumsub-integrate-dint-standalone`; SKIP for the base WebSDK embed itself — use
  `sumsub-integrate-websdk`.
allowed-tools: Read, Write
---

# Sumsub — Device Intelligence via the WebSDK

Add **Device Intelligence (DI)** to a project that already embeds the Sumsub
WebSDK. DI is the fraud-detection layer that captures low-level device/browser
signals (device fingerprint, bot/automation, VPN/proxy, emulator, incognito,
reused-device) and attaches them to the applicant as **device risk labels**
that feed risk scoring.

The JS module that does the capture is called **Fisherman** (npm
`@sumsub/fisherman`) — same thing, different name. Inside the WebSDK you almost
never touch it directly; the SDK ships and drives it for you.

## ⚠️ Sandbox tokens only

Do **not** accept or use a production App Token / secret during integration
work. Insist on a **sandbox** pair from
<https://cockpit.sumsub.com/checkus/home?sbx=true> — **Connect Sumsub to
your AI agent** -> **Build & configure** -> **Generate token**. Token + secret
are revealed once at creation; copy both before closing the dialog. Helper scripts in sibling skills
enforce this with an `sbx:` prefix check; the curl recipes here assume the same.
Deeper auth mechanics: [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md).

## The lifecycle in one picture

```
 ┌───────────────────────────────┐  ← one-time, in the dashboard
 │ 1. "Capture device data" on    │     (verification level settings)
 │    on the verification level   │
 └───────────────┬───────────────┘
                 │
 ┌───────────────▼───────────────┐  ← your existing sumsub-integrate-websdk
 │ 2. WebSDK launches as usual    │     code. NOTHING new on the frontend.
 │    (same access token)         │
 └───────────────┬───────────────┘
                 │ the SDK auto-inits Fisherman with that token,
                 │ fingerprints the device, attaches it to the applicant
 ┌───────────────▼───────────────┐  ┌─────────────────────────────────┐
 │ 3. Sumsub computes device      │─▶│ Device risk labels on the       │
 │    signals + risk labels       │  │ applicant; feed risk scoring    │
 └───────────────┬───────────────┘  └─────────────────────────────────┘
                 │
 ┌───────────────▼───────────────┐  ← server reads the applicant /
 │ 4. You read the verdict +      │     receives the webhook (same as
 │    device signals server-side  │     the base WebSDK flow)
 └────────────────────────────────┘
```

The headline: **for a standard WebSDK integration, DI is a dashboard toggle, not
new code.** Stages 3–4 below are the advanced (self-rendered) path and the
result-reading details.

## Stage 1 — Enable device capture on the level

DI rides along automatically in WebSDK 2.0 and the Mobile SDKs **only when
"Capture device data" is enabled in the verification level settings**. In the
dashboard: open the level → **Device intelligence** section → tick **Capture
device data**. If you don't see the setting, DI isn't provisioned for the workspace —
contact Sumsub to enable the product before continuing.

Optional **BYOK**: you can supply your own Fingerprint Pro credentials (public +
secret API key) under DevSpace → Integrations → Fingerprint so devices are
captured under your Fingerprint account. Without BYOK, Sumsub's own credentials
are used — both work; BYOK only matters if you already run Fingerprint Pro.

That's the entire required setup. Re-launch your existing WebSDK flow and devices
start getting captured.

## Stage 2 — The automatic in-SDK lifecycle (no code)

With "Capture device data" on, the WebSDK, using the **same access token** your
[`sumsub-integrate-websdk`](../sumsub-integrate-websdk/SKILL.md) token endpoint
already mints:

1. Initializes Fisherman against the SDK's API host once the SDK config loads.
2. Fingerprints the device on each step transition, binding it to the current
   `(applicantId, attemptId)`.
3. Re-initializes on a level transition (the `attemptId` changes), so a
   multi-level flow gets a fresh device binding per level.
4. Forwards the resulting device id to the backend on subsequent calls so the
   capture is tied to the applicant.

You do not write, configure, or call any of this. It is listed so you can
recognise it in logs / network traffic (`/di/info`, an `/bhv/...` events POST,
an `X-External-Device-Fingerprint` request header).

## Stage 3 — Advanced: self-rendered / headless wiring

Only relevant if you do **not** use the prebuilt `snsWebSdk` widget and drive
the verification API yourself. Then you own the Fisherman lifecycle. Mirror the
SDK's own behaviour — see [`examples/fisherman-self-render.ts`](examples/fisherman-self-render.ts):

```ts
// Shape only — the full impl (single-active-session class, attemptId re-init,
// try/catch fail-open, header forwarding) is in examples/fisherman-self-render.ts.
import { init, destroy, type Fisherman } from '@sumsub/fisherman'

let fisherman: Fisherman | undefined // module-level singleton

// init once with the SDK access token + region API host
fisherman = await init({ token, baseUrl, onError: () => { destroy() /* re-init after token refresh */ } })

// on each step transition — gate, then fingerprint bound to (applicantId, attemptId)
if (fisherman?.isDeviceIntelligenceEnabled) {
  const { visitorId } = await fisherman.fingerprint({
    linkedId: applicantId,
    deviceBindingId: `${applicantId}-${attemptId}`, // MUST change per level
  })
  // forward visitorId as the X-External-Device-Fingerprint header on the API calls that follow
}
```

Key rules the SDK follows and you must too:
- Two-layer gate. The SDK gates `init()` itself on the config-level flag
  `config.deviceIntelligenceSettings.enabled` — when DI is off for the level it
  never calls `init()`. Then it gates each `fingerprint()` on the runtime flag
  `fisherman.isDeviceIntelligenceEnabled` (from `/di/info`). Mirror both: skip
  init when the config flag is false, never fingerprint unless the runtime flag
  is true (it errors / wastes a call).
- On a level transition (`attemptId` changes) `destroy()` then `init()` again
  before the next `fingerprint()`, so devices bind to the right level.
- Forward the returned `visitorId` as the `X-External-Device-Fingerprint`
  header on the verification API calls that follow the capture. (This header is
  device/stats enrichment — the actual applicant binding is the per-attempt
  `deviceBindingId` (`applicantId-attemptId`) above, not the header.)

## Stage 4 — Read the device signals

DI does not change *how* you read the verdict — it enriches it. Keep the
server-as-source-of-truth rule from the base WebSDK skill (webhook +
authenticated applicant GET), and read the device data alongside it.

**In the dashboard:**
- Applicant profile → **Devices** tab — every device seen, with risk labels.
- Completed verification → **Device Check** block.
- **Transactions** → a device row → **View device details**.

**Via API / webhooks:** the device risk labels land **on the applicant**, not in
the webhook payload. The `applicantReviewed` webhook carries the verdict only
(`reviewResult`) — treat it as the trigger to read the applicant server-side
(same App-Token + HMAC auth as the base skill), here keyed by your `externalUserId`:

```bash
USER_ID="<your-externalUserId>"   # for a Sumsub applicant id instead: /resources/applicants/<applicantId>/one
PATH_Q="/resources/applicants/-;externalUserId=${USER_ID}/one"
TS=$(date -u +%s)
SIG=$(printf '%s%s%s' "$TS" "GET" "$PATH_Q" \
      | openssl dgst -sha256 -hmac "$SUMSUB_SECRET_KEY" -hex | awk '{print $NF}')
curl -sS --fail-with-body -H "X-App-Token: $SUMSUB_APP_TOKEN" -H "X-App-Access-Ts: $TS" \
     -H "X-App-Access-Sig: $SIG" -H "X-Agent-Source: sumsub-skills" \
     -H "X-Agent-Source-Ver: 1.4.1" \
     "https://api.sumsub.com${PATH_Q}"
```

Runnable version of that GET: [`examples/read-device-results.sh`](examples/read-device-results.sh).

The full device-signal / risk-label catalog and where each surfaces:
[`references/device-signals.md`](references/device-signals.md).

## Sandbox testing

- Sandbox has no real device signals — Fingerprint is simulated. Devices are
  still captured and risk labels still appear, but values are synthetic.
- For deterministic test outcomes the module accepts a `simulationConfig`
  (`FpSimulationConf`) on `init` to force specific signals; only relevant on the
  self-rendered path. The prebuilt WebSDK handles sandbox simulation itself.
- Run a full sandbox WebSDK verification (see the base skill's test docs) and
  confirm a device appears under the applicant's Devices tab.

## Going live checklist

- [ ] "Capture device data" is enabled on the **production** level (it's per-level,
  per-workspace — enabling it in sandbox does not carry over).
- [ ] Your server reads device risk labels from the applicant / webhook, not
  from the browser.
- [ ] If you gate access on device risk, you decided which labels are blocking
  vs informational (`references/device-signals.md`).
- [ ] BYOK Fingerprint keys (if used) are the production keys in the prod
  workspace, sandbox keys only in sandbox.
- [ ] Self-rendered path only: `isDeviceIntelligenceEnabled` gate, per-`attemptId`
  re-init, and `X-External-Device-Fingerprint` forwarding all verified against a
  real sandbox run.

## See also

- [`sumsub-integrate-websdk`](../sumsub-integrate-websdk/SKILL.md) — the base
  WebSDK embed this skill sits on top of (token endpoint, lifecycle, webhooks).
- [`sumsub-integrate-dint-standalone`](../sumsub-integrate-dint-standalone/SKILL.md) —
  Device Intelligence on pages with no WebSDK widget (login / signup / checkout).
- [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md) — HMAC signing shared by every
  Sumsub skill.
- [`references/device-signals.md`](references/device-signals.md) — device risk
  labels + where they surface.
- [`examples/fisherman-self-render.ts`](examples/fisherman-self-render.ts) — the
  advanced headless wiring.
- [`examples/read-device-results.sh`](examples/read-device-results.sh) — read the
  applicant (incl. device risk labels) server-side.
- [Device Intelligence docs](https://docs.sumsub.com/docs/device-intelligence)
  and [Get started](https://docs.sumsub.com/reference/get-started-with-device-intelligence)
  — authoritative source if this skill drifts.
