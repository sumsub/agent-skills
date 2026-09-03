---
name: sumsub-manage-webhooks
description: Manage Sumsub `clientWebhooks` (event subscriptions for applicantReviewed / applicantPending / kytTxn / etc.) — reads via `/resources/api/clientWebhooks`, writes via `/resources/api/agent/clientWebhooks`. **Sandbox only** — production webhooks must be created by a human directly in the Sumsub dashboard. TRIGGER when the user asks to "list / retrieve / show webhooks", "create / add / register a webhook", or "update / edit / change a webhook target / event list / secret / signature algorithm" against their sandbox tenant. SKIP for production webhook setup (refer the user to the dashboard), for unrelated webhook surfaces (Stripe / videoIdent / Fireblocks / NFC / partner-specific receive paths under `/resources/webhooks/...`), for testing one-off delivery (use the `inspectionCallbacks/testWebhook` endpoint directly), and for KYT-only webhook routing (that's managed in the Sumsub dashboard's KYT section). The public API does not expose delete or per-webhook delivery stats — for those, refer the user to the Sumsub dashboard UI.
allowed-tools: Read, Write, Bash
---

# Sumsub — Manage Client Webhooks

Lists, retrieves, creates, and updates `ClientWebhook`
event subscriptions. Reads use `/resources/api/clientWebhooks`; writes use
`/resources/api/agent/clientWebhooks`.

## Endpoints

| Verb | Path | Purpose |
|---|---|---|
| `GET` | `/resources/api/clientWebhooks` | List webhooks on the tenant. Returns `EntityResult<ClientWebhook>` (`{list: {items: [...] }}`). **Capped at the oldest 50** server-side (`getOldest50`). |
| `GET` | `/resources/api/clientWebhooks/{id}` | Read one webhook by id. Use this to resolve a `name` from a known id, or to verify what landed after a write. |
| `POST` | `/resources/api/agent/clientWebhooks` | Create. Body must NOT include `id` — server assigns it. (The model layer still does an internal upsert, but the request DTO is `ClientWebhookCreateRequest` without `id`.) |
| `PATCH` | `/resources/api/agent/clientWebhooks` | Update an existing webhook (by `id` in body). DTO is `ClientWebhookUpdateRequest`. |

Permission required: `manageClientSettings`.

There is **no DELETE** and **no `/stats` endpoint** on the public API —
use the Sumsub dashboard UI when you need to delete a webhook or view
per-webhook delivery stats.

## Auth — App Token + secret (sandbox only)

This skill talks to the public Sumsub API and signs each request per
[the authentication reference](https://docs.sumsub.com/reference/authentication).
The full how-it-works writeup lives in the [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md)
skill — read it if you hit `401 Invalid signature`.

> **⚠️ Sandbox tokens only.** Do **not** accept or use a production App Token
> here. If the user offers one, refuse and ask them to generate a sandbox
> pair at <https://cockpit.sumsub.com/checkus/home?sbx=true> (**Connect
> Sumsub to your AI agent** -> **Build & configure** -> **Generate token**).
> Token + secret are shown once — copy both before closing the dialog. The helper script
> enforces this — it rejects tokens that don't start with `sbx:` unless
> `SUMSUB_ALLOW_PROD=1` is set.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

## Sandbox-only scope — production webhooks must be created by a human

Because this skill only accepts sandbox App Tokens, every webhook it creates
or updates lives in the sandbox workspace. Sandbox and production are
separate tenants on Sumsub's side — there is no "promote to prod" path, and
re-running this skill with a production token is **not** the right way to set
up a real webhook.

When the user is ready to wire up a production webhook:

- **Do not** offer to do it from this skill, even if the user asks.
- **Do not** ask for or accept a production App Token (the script will refuse
  it without `SUMSUB_ALLOW_PROD=1`, and you should not suggest that override).
- Tell the user that the production webhook — target URL, signing secret,
  event subscription, custom headers — should be configured by a human
  directly in the Sumsub dashboard (Integrations → Webhooks, with the
  workspace toggle on **Production**). Setting up a production webhook is a
  security-sensitive operation (the signing secret authenticates real PII
  deliveries) and the audit trail should attribute it to a person.
- The right workflow is: use this skill to prototype against sandbox, capture
  the final spec the user wants (event list, headers, signature algorithm),
  then hand that spec off as plain documentation so a human can recreate it
  in production.

## Subcommands

`manage_webhooks.sh` is the orchestrator:

```bash
manage_webhooks.sh list                       # GET all webhooks (table summary; capped at 50)
manage_webhooks.sh list --json                # raw JSON of all webhooks
manage_webhooks.sh get <webhookId>            # one webhook (filtered from the list)
manage_webhooks.sh create <spec.json>         # POST without id  (compact spec → ClientWebhook)
manage_webhooks.sh update <spec.json>         # POST with id     (spec MUST contain id)
```

`create` and `update` both call `build_webhook_payload.py` to expand the compact spec.

## Before submitting: target must be publicly reachable

Sumsub delivers webhooks from its own infrastructure, so the `target` URL has to resolve and accept connections from the public internet. Common gotcha: users paste `http://localhost:3000/webhook` (or `127.0.0.1`, `0.0.0.0`, `::1`) while developing locally. Sumsub accepts the URL at creation time but every delivery will fail — and `targets` like these are rejected by the skill's payload builder up front.

If the user supplies a localhost-ish URL, **don't submit it**. Instead, walk them through exposing the local server through a public tunnel before creating the webhook:

1. Suggest [ngrok](https://ngrok.com/download) (the most common choice). On macOS: `brew install ngrok/ngrok/ngrok`. Other platforms: download from the link. First-time users need a free ngrok account to grab an auth token, then `ngrok config add-authtoken <TOKEN>` once.
2. Ask which port their local webhook receiver listens on (typically 3000 / 8080 / 4000).
3. Have them run `ngrok http <port>` in a separate terminal and keep it open.
4. ngrok prints a `Forwarding https://<random>.ngrok-free.app -> http://localhost:<port>` line. The `https://...ngrok-free.app` part is the public URL.
5. Append the receiver's webhook path (e.g. `/webhook`, `/sumsub`) and use the full URL as `target`. Then re-run the `create` subcommand.

Heads-up to mention: on the free ngrok plan the public URL changes every time `ngrok` restarts — the webhook will need to be re-`update`d (POST with the existing `id` and the new `target`) each session. A reserved domain (paid) or `--domain=<your-subdomain>` keeps it stable. Alternatives if the user prefers: Cloudflare Tunnel (`cloudflared tunnel`), Tailscale Funnel, localtunnel — same idea, same procedure.

## Compact spec for `create` / `update`

```yaml
# Identity (omit on create; required on update)
id: 698bfc...                  # id from a previous list / create response

# Display + addressing
name: "Production webhook"     # required (no min length but the dashboard expects something)
description: "Sends KYC events to our backend"
target: "https://example.com/sumsub/webhook"   # required — destination URL (or slack / email / telegram address depending on targetType)
targetType: http               # http | email | slack | telegram   (default: http)

# Subscription
types:                         # required — event-type strings (see "Event types" below)
  - applicantReviewed
  - applicantPending
  - applicantOnHold
  - applicantCreated
applicantType: individual      # individual | company   (omit to subscribe to both)
sourceKeys: []                 # optional — restrict to specific source keys

# Auth + delivery
secretKey: "..."               # HMAC secret used to sign payloads
signatureAlgorithm: HMAC_SHA256_HEX  # HMAC_SHA1_HEX | HMAC_SHA256_HEX | HMAC_SHA512_HEX  (default: SHA256)
headers:                       # optional extra HTTP headers added to each delivery
  - { key: "X-Source", value: "sumsub" }
  - { key: "Authorization", value: "Bearer ${MY_TOKEN}" }   # caller substitutes before sending

# Lifecycle flags
notResendFailedWebhooks: false # default false; true = no automatic retries on delivery failure
```

The builder validates enums (`targetType`, `signatureAlgorithm`, `applicantType`), rejects empty `types`, and wraps `headers` so that the `key`/`value` shape matches `ClientWebhookHeader`. Unknown keys pass through (escape hatch).

### Event types (`types[]`)

The OpenAPI keeps `types` as a free-form `string[]`. The names below cover
the commonly-emitted Sumsub events. Unknown event types are silently
accepted server-side and the webhook simply never fires — so typos are not
caught by the API.

| Group | Event type | When it fires |
|---|---|---|
| Applicant lifecycle | `applicantCreated` | New applicant created |
| | `applicantPrechecked` | Pre-screen complete |
| | `applicantPending` | Submitted for review |
| | `applicantReviewed` | Final review answer (GREEN / RED) reached |
| | `applicantOnHold` | Review held / paused |
| | `applicantActivated` | Applicant activated |
| | `applicantDeactivated` | Applicant deactivated |
| | `applicantReset` | Verification reset (retry) |
| | `applicantLevelChanged` | Level reassigned |
| | `applicantTagsChanged` | Tags added/removed |
| | `applicantPersonalInfoChanged` | Personal info edited |
| | `applicantDeleted` | Applicant deleted |
| | `applicantPersonalDataDeleted` | GDPR personal-data erasure executed |
| Action workflow | `applicantActionPending` / `applicantActionReviewed` / `applicantActionOnHold` | Action-flow events |
| Workflow | `applicantWorkflowCompleted` | Workflow run finished (**not** `applicantWorkflowRunCompleted`) |
| Video ident | `videoIdentStatusChanged` | Live status update |
| | `videoIdentCompositionCompleted` | Recording assembly finished |
| KYT (applicant-scoped) | `applicantKytTxnApproved` / `applicantKytTxnRejected` / `applicantKytTxnReviewed` / `applicantKytTxnDeleted` / `applicantKytTxnDataChanged` / `applicantKytTxnAwaitingUser` / `applicantKytOnHold` | Per-applicant transaction-monitoring events |
| KYT (case-scoped) | `kytCaseCreated` / `kytCaseStatusChanged` / `kytCaseReviewed` | KYT case-management events (note: it's `kytCaseStatusChanged`, **not** `kytCaseUpdated`) |
| AML case | `amlCaseApproved` / `amlCaseRejected` / `amlCaseOnHold` | AML-case disposition events |
| Travel Rule | `travelRuleAction` | Travel-rule lifecycle events |
| KYB | `kybCompanyActivity` | KYB ongoing-monitoring events |

The skill forwards whatever the caller writes — no client-side validation, since Sumsub may add events faster than this list updates.

## Outputs

- **`list`** — table with `id`, `name`, `target`, `disabled`, `types[]`, `applicantType`, `signatureAlgorithm`, `createdAt`.
- **`get`** — the full single webhook JSON (with `secretKey` redacted in the output as a defensive measure).
- **`create` / `update`** — the persisted `ClientWebhook` (with server-assigned `id` on create) and a one-line summary.

## Worked examples

- [`examples/basic-http.json`](examples/basic-http.json) — minimal webhook: HTTPS endpoint, four applicant-lifecycle events, SHA-256 signing.
- [`examples/with-headers-and-restrictions.json`](examples/with-headers-and-restrictions.json) — broad event set scoped to a specific `sourceKey`, with custom HTTP headers.
- [`examples/legacy-sha1.json`](examples/legacy-sha1.json) — SHA1-signed webhook, for receivers that already verify SHA1.
- [`examples/update-existing.json`](examples/update-existing.json) — same as basic but with `id` set, demonstrating the update path.

## See also

- [`references/webhook-schema.md`](references/webhook-schema.md) — full `ClientWebhook` schema, all enums, gotchas (secret not write-only, signing semantics).
- Sumsub docs: [Webhook system](https://docs.sumsub.com/docs/webhooks.md), [Webhook event types](https://docs.sumsub.com/docs/webhook-event-types.md), [Verify webhook signatures](https://docs.sumsub.com/docs/verify-webhook-payload-signatures.md).
