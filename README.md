# @sumsub/agent-skills

Agent skills for the [Sumsub](https://sumsub.com) API — works with any coding agent that supports the [Agent Skills](https://agentskills.io) format (Claude Code, Codex, Cursor and others).

## Install

```bash
npx skills add sumsub/agent-skills --all -y
```

This fetches the repo and installs each skill into your agent's skills directory (for Claude Code, typically `~/.claude/skills/` for global install or `.claude/skills/` for project-local install).

### Manual install

Clone or download the repo, then copy any directory under [`skills/`](skills/) into your agent's skills directory (Claude Code shown):

```bash
git clone https://github.com/sumsub/agent-skills.git
cp -r skills/sumsub-create-questionnaire ~/.claude/skills/
```

## Available skills

| Skill | What it does |
|---|---|
| [`sumsub-analyze-regulation`](skills/sumsub-analyze-regulation/) | Analyze a regulation document (PDF or text) and produce a Sumsub configuration plan — mapping regulatory requirements to levels, questionnaires, PoA presets, TM rules, and workflows. Entry point before invoking the create-* skills. |
| [`sumsub-conformance`](skills/sumsub-conformance/) | Check whether the **deployed** Sumsub config actually satisfies a regulation/policy document — resolves the live config graph (level, questionnaires, presets, workflow, entitlements) and traces each requirement to where it is collected, scored, and enforced, flagging collected-but-not-enforced gaps. Advisory, sandbox only. |
| [`sumsub-api-auth`](skills/sumsub-api-auth/) | Authenticate to `api.sumsub.com` with an App Token + secret (HMAC-SHA256 signing). **Sandbox tokens only — never share production credentials with the agent.** |
| [`sumsub-create-questionnaire`](skills/sumsub-create-questionnaire/) | Create or update a Sumsub `QuestionnaireDefinition`. Compact spec → full localized payload → `POST /resources/api/agent/questionnaires` (create; 409 if id exists) or `PATCH` (update; 404 if id missing). Read via `GET /resources/api/agent/questionnaires/{id}`. |
| [`sumsub-create-poa-preset`](skills/sumsub-create-poa-preset/) | Create or update a Sumsub `PoaStepSettings` (Proof-of-Address preset). `POST /resources/api/agent/poaStepSettings` to create, `PATCH` to update by id, `GET /{id}` to read. Returned `id` attaches to a level's `PROOF_OF_RESIDENCE` doc-set. |
| [`sumsub-create-level`](skills/sumsub-create-level/) | Create or update a Sumsub `ApplicantLevel`. `POST /resources/applicants/-/levels` to create, `PATCH` to update by id, `GET /{id}` to read. Can wire in an existing `questionnaireDefId`. |
| [`sumsub-create-cross-check-preset`](skills/sumsub-create-cross-check-preset/) | Create or update a Sumsub cross-check preset (POI↔POA name/address comparison rules). Use **only** when the user explicitly asks to override defaults — Sumsub's default preset is tuned for best approval rate. |
| [`sumsub-supported-id-documents`](skills/sumsub-supported-id-documents/) | Read the built-in supported identity-document catalogue (`GET /resources/api/agent/supportedDocs/documentsByCountries`, locally filtered) and edit the client's per-country overrides via read-modify-write against `PUT /resources/api/agent/globalSettings/idDocSettings/countryMappings`. |
| [`sumsub-manage-webhooks`](skills/sumsub-manage-webhooks/) | Manage Sumsub `clientWebhooks` event subscriptions — list, GET /{id}, create, and update (PATCH). Sandbox only; production webhook setup stays in the dashboard. |
| [`sumsub-manage-applicant-tags`](skills/sumsub-manage-applicant-tags/) | Add, replace, or remove tags on an applicant profile — `POST /resources/applicants/{applicantId}/tags/add` (additive), `POST .../tags` (overwrite), `DELETE .../tags` (remove), read-back via `GET .../one`. |
| [`sumsub-create-workflow`](skills/sumsub-create-workflow/) | Build & POST a Sumsub `ApplicantWorkflow` via the public API. Compact node/edge spec with parsed `when:` expressions → full payload → `POST /resources/api/agent/applicantWorkflows`, then `PUT /{id}/revisionStatus` to publish. Defaults to `draft`. |
| [`sumsub-create-transaction`](skills/sumsub-create-transaction/) | Submit a `KytTxnData` to Sumsub Transaction Monitoring. Auto-routes between existing-applicant (`/{applicantId}/kyt/txns/-/data`) and non-existing-applicant (`/-/kyt/txns/-/data?levelName=…`) endpoints. |
| [`sumsub-create-kyt-rules`](skills/sumsub-create-kyt-rules/) | Create or modify KYT transaction monitoring scoring rules via `POST /resources/api/agent/tm/rules` — translates described conditions (amount thresholds, country lists, aggregations, scheduled applicant checks) into `KytTxnRule` payloads. Rules start in test mode (dry run) and are activated in the dashboard. |
| [`sumsub-integrate-websdk`](skills/sumsub-integrate-websdk/) | End-to-end Sumsub WebSDK integration recipe — level setup → server-signed access-token endpoint → `snsWebSdk` init (vanilla + React) → client lifecycle events → webhook signature verification (incl. ngrok-based local testing) → go-live checklist. |
| [`sumsub-integrate-dint-websdk`](skills/sumsub-integrate-dint-websdk/) | Add Device Intelligence (Fisherman) to an existing Sumsub WebSDK integration — enable Capture devices on the level, automatic in-SDK Fisherman lifecycle, advanced self-rendered wiring, reading device signals (Devices tab, Device Check, risk labels, webhooks), sandbox testing, go-live checklist. |
| [`sumsub-integrate-dint-standalone`](skills/sumsub-integrate-dint-standalone/) | Add Device Intelligence (Fisherman) to pages **without** the WebSDK widget — login, signup, checkout, 2FA. Behavior access token → `@sumsub/fisherman` init + fingerprint → confirm via platform event / financial transaction / create-applicant → read results. |
| [`sumsub-integrate-msdk`](skills/sumsub-integrate-msdk/) | Add Sumsub identity verification (KYC) to your native iOS or Android app. Detects the platform, then walks you from installing the Mobile SDK (iOS: Swift Package Manager or CocoaPods; Android: Gradle + the Sumsub Maven repo) through permissions to a ready-to-run integration file — token refresh, lifecycle callbacks, and the launch point (iOS: UIKit or SwiftUI; Android: Activity, Fragment, or Compose) included, with your approval at each step. Native iOS & Android only. |
| [`sumsub-theme-msdk`](skills/sumsub-theme-msdk/) | Scan a mobile app's design system (colors, fonts, corner radii, light/dark) → derive a full palette → generate a theme that makes the Mobile SDK match, wired at the launch site (iOS: `SumsubTheme: SNSTheme` subclass; Android: `sumsubTheme(context)` via the `SNSTheme` DSL). |
| [`sumsub-integrate-id-connect`](skills/sumsub-integrate-id-connect/) | End-to-end Sumsub ID Connect (OIDC "Verify with Sumsub ID") integration recipe — preconditions checklist → preflight → frontend button (`@sumsub/id-connect` or raw OIDC) → backend code → access_token exchange → share-token mint → partner-consent shareLink flow → applicant materialisation via `/resources/api/reusableIdentity/reuse`. |
| [`sumsub-api-generic`](skills/sumsub-api-generic/) | Fallback catch-all for anything Sumsub-API-related not covered above. Searches the bundled OpenAPI schema, inspects the operation, signs with App Token, and calls it. |
| [`sumsub-check-permissions`](skills/sumsub-check-permissions/) | Fetch the current tenant's allowed entitlements (`BackgroundCheckTarget` list) — returns `{"allowedChecks": {key: label}}` (keys are the enabled entitlements). Called by the create-* skills to gate entitlement-required features before building a payload. |
| [`sumsub-check-skills-version`](skills/sumsub-check-skills-version/) | Check whether the installed skills are up to date — fetches the canonical version from `https://api.sumsub.com/llms.txt`, compares it to the locally installed version, and recommends `npx skills add sumsub/agent-skills --all` when behind. |
| [`sumsub-integrate-travel-rule`](skills/sumsub-integrate-travel-rule/) | End-to-end Sumsub Travel Rule integration recipe — pick the flow (before settlement / after settlement / answering), identify the counterparty VASP, submit the transfer, read the exchange status, finalise or cancel, and answer incoming requests with the two ordered responses. Also covers the unhosted-wallet path when no VASP is attributed (`POST /resources/tr/sdk/init`, ownership checks, manual verification) and transaction search via `GET /resources/kyt/txns/query/-` with the dedupe ladder. Includes the Sandbox testing procedure. |
| [`sumsub-manage-wallet-address-book`](skills/sumsub-manage-wallet-address-book/) | Register the crypto wallet addresses an organisation controls so Travel Rule ownership resolves without a human — bulk import via `POST /resources/kyt/walletAddress/import` (max 10 000 per call), or bind one address to an applicant via `POST /resources/api/applicants/{applicantId}/payments`. |
| [`sumsub-resolve-currency`](skills/sumsub-resolve-currency/) | Resolve and validate the currency fields on a transaction — `currencyCode`, `currencyType`, `cryptoParams.cryptoChain` and the `amountInDefaultCurrency` pair. Reads `GET /resources/kyt/currency?type=crypto|fiat`, resolves `(symbol, chain, contract)` to exactly one asset, normalises chain aliases, and refuses ambiguous input instead of guessing. |

## Layout

```
.
├── package.json                ← npm metadata + claude.skills pointer
├── skills.json                 ← skill manifest (name, path, description)
└── skills/
    └── <skill-name>/
        ├── SKILL.md            ← frontmatter + procedure (required)
        ├── scripts/            ← deterministic shell/python helpers
        ├── references/         ← long docs loaded on-demand
        └── examples/           ← input fixtures
```

Each skill is self-contained — `SKILL.md` is the entry point.

## Setup

> **Requirements:** `bash`, `curl`, `openssl`, and `python3` (stdlib only) on `PATH`.

All skills authenticate to `https://api.sumsub.com` with an App Token + secret key.

**Step 1.** Generate an agent scoped sandbox token pair: Sumsub dashboard → switch to **Connect Sumsub to your AI agent** → **Build & configure** → **Generate token**. The token and secret are shown once — copy both before closing.

**Step 2.** Provide the credentials as environment variables to your agent. In Claude Code, create `.claude/settings.local.json` in your project root (gitignored, loaded automatically):

```json
{
  "env": {
    "SUMSUB_APP_TOKEN": "sbx:...",
    "SUMSUB_SECRET_KEY": "..."
  }
}
```

⚠️ **Sandbox tokens only.** Never give the agent a production App Token — it grants full access to live applicant PII. Helper scripts refuse any token that doesn't start with `sbx:`.

See [`sumsub-api-auth`](skills/sumsub-api-auth/) for the signing mechanics and troubleshooting `401` errors.

## License

MIT
