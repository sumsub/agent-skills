---
name: sumsub-manage-applicant-tags
description: Add, replace, or remove tags on a Sumsub applicant profile via the public API — `POST /resources/applicants/{applicantId}/tags/add` (additive), `POST .../tags` (overwrite the full set), `DELETE .../tags` (remove), read-back via `GET .../one`. TRIGGER when the user asks to "tag / untag an applicant", "add / remove / clear applicant tags", "label an applicant profile", or "replace an applicant's tag set". SKIP for transaction tags, tag definitions with scoring weights, or applicant risk assessment (use `sumsub-create-kyt-rules`), for automated tagging inside verification workflows (use `sumsub-create-workflow`), and for subscribing to tag-change webhooks (use `sumsub-manage-webhooks`).
allowed-tools: Read, Write, Bash
---

# Sumsub — Manage Applicant Tags

Adds, replaces, and removes tags on an applicant profile, always followed by
a read-back. Tags are free-form labels used for filtering and classification
in the applicant list; they are also readable as `applicant.tags` in workflow
routing and TM rule expressions.

## Endpoints

| Verb | Path | Purpose |
|---|---|---|
| `POST` | `/resources/applicants/{applicantId}/tags/add` | **Add** tags on top of the existing set. Additive; repeat adds of an existing tag are deduped server-side. Body: bare JSON array of strings. |
| `POST` | `/resources/applicants/{applicantId}/tags` | **Overwrite** — replaces the entire tag set with the body. `[]` clears all tags. Destructive: requires the confirm step below. |
| `DELETE` | `/resources/applicants/{applicantId}/tags` | **Remove** only the tags listed in the body; the rest stay. |
| `GET` | `/resources/applicants/{applicantId}/one` | Read-back. Tags come back in the `tags` field of the applicant — there is no dedicated tags GET. |

All writes return `{"ok": 1}` on success. Tag names not seen before are
**auto-created** on both the add and the overwrite endpoint (sandbox-verified;
the docs' claim that overwrite requires pre-existing tags is outdated).

Tag *definitions* — renaming a tag, picking its color, or the "include tag in
applicant summary report" flag — are **Sumsub dashboard UI only** (Applicant
tags page); there is no public-API surface for them.

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
> enforces this — it rejects tokens that don't start with `sbx:`.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

## Procedure

1. **Pick the operation.** Default to the additive `add` — it is safe and
   deduped. Use `overwrite` **only** when the user explicitly wants to replace
   the whole set (or clear it); use `remove` to take specific tags off. Do not
   pre-GET before `add` or `remove` — the endpoints are targeted and
   idempotent, the read-back in step 3 is the verification.
2. **Overwrite only — confirm first.** GET the applicant, show the user the
   current tags that will be lost, and get explicit confirmation before
   POSTing the replacement set. Same gate applies to clearing all tags
   (overwrite with `[]`).
3. **Run the write via the orchestrator** (it appends the read-back
   automatically):

   ```bash
   bash scripts/manage_applicant_tags.sh list      <applicantId>
   bash scripts/manage_applicant_tags.sh add       <applicantId> "High Risk" "VIP"
   bash scripts/manage_applicant_tags.sh overwrite <applicantId> "Compliance Reviewed"   # after the confirm step!
   bash scripts/manage_applicant_tags.sh remove    <applicantId> "Legacy KYC"
   ```

4. **Compare the read-back** to what was requested. An empty set comes back
   with the `tags` field **absent** from `GET /one` — that is the normal
   "no tags" state, not an error. On a mismatch, report it — do not retry
   automatically. Surface 4xx errors verbatim.
5. **Report, names first.** Lead with the applicant's name and the resulting
   tag list, then the dashboard link
   (`https://cockpit.sumsub.com/checkus/applicant/<applicantId>` — render as
   a clickable markdown link), and put the applicant `id` on its own last
   line.

## Gotchas

- **30-tag cap per applicant.** Exceeding it (existing + new) fails the whole
  request with HTTP 400 `"Too many applicant tags"` — atomically, nothing is
  applied. Report the 30-tag limit and **stop there**: do not trim the list
  and retry, and never delete or overwrite existing tags to make room in the
  same run — freeing up slots is a destructive decision the user must make
  explicitly, in a fresh request.
- **Tag names are case-sensitive** — `"High Risk"` and `"high risk"` are two
  different tags. Match the user's existing casing when removing.
- **Overwrite replaces everything.** `POST .../tags` with any body wipes tags
  not listed in it. When the user says "add", never use the overwrite
  endpoint.
- **Empty = absent.** After clearing tags, `GET /one` has no `tags` field at
  all. Read-back logic must treat a missing field as an empty set.
- **Unknown applicant → HTTP 404** `"Applicant with id ... not found (anf)"`
  (not 400). Ask the user to re-check the id.
- **Tag changes fire the `applicantTagsChanged` webhook** — relevant if the
  tenant subscribes to it (see `sumsub-manage-webhooks`).

## See also

- [`sumsub-create-kyt-rules`](../sumsub-create-kyt-rules/SKILL.md) — transaction
  tags, tag definitions with scoring weights (`scoreWeight`), applicant risk
  assessment.
- [`sumsub-create-workflow`](../sumsub-create-workflow/SKILL.md) — automated
  tag add/remove as workflow action nodes; routing on `applicant.tags`.
- [`sumsub-manage-webhooks`](../sumsub-manage-webhooks/SKILL.md) — subscribe to
  `applicantTagsChanged`.
- Sumsub docs: [Applicant tags](https://docs.sumsub.com/docs/add-applicant-tags.md),
  [Add and overwrite applicant tags](https://docs.sumsub.com/reference/adding-overwriting-custom-applicant-tags.md),
  [Add applicant tags](https://docs.sumsub.com/reference/add-custom-applicant-tags.md),
  [Remove applicant tags](https://docs.sumsub.com/reference/remove-custom-applicant-tags.md).
