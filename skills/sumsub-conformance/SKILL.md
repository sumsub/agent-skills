---
name: sumsub-conformance
description: Check whether a tenant's DEPLOYED Sumsub config actually satisfies a regulation/policy document — tracing each requirement to where it is collected, scored, and ENFORCED, and flagging "collected-but-not-enforced" gaps. TRIGGER when the user has a regulation/policy/requirements doc (PDF or text) and wants to verify the live config matches it, audit a client's setup against compliance rules, "does my config satisfy this regulation", "check conformance / gap analysis", or close the loop after configuring with the create-* skills. SKIP for building config (sumsub-create-*) or for generating a config plan from a regulation (sumsub-analyze-regulation). For pure hygiene linting with no regulation, run this skill's bundled lint_config.py sub-pass directly.
allowed-tools: Read, Write, Bash
---

# Sumsub — Conformance (regulation ↔ deployed config)

Traces every requirement of a regulation through the **live** config graph and answers, per
requirement: **collected? → scored? → enforced?** The headline finding it surfaces — that nothing
else does — is **COLLECTED-BUT-NOT-ENFORCED**: the config gathers and scores the data a regulation
needs, then doesn't act on it (e.g. an appropriateness questionnaire that's scored but never routed).

This is an **advisory gap assistant, not a compliance guarantee.** It verifies the config-representable
parts deterministically and honestly delimits the rest (semantic intent = judgment; SDK/platform
outcomes = out of scope). Get a human to sign off.

## When to use

- Existing client: "here's our regulation, here's our tenant — what's actually enforced?"
- New client who configured Sumsub with the create-* skills: close the **generate → verify** loop —
  did the assembled config end up enforcing the regulation it was built from?

## Endpoints (read-only)

All via `scripts/sumsub_curl.sh` (App-Token HMAC). `resolve_graph.sh` wraps these:

| Purpose | Method + Path |
|---|---|
| Levels (find target) | `GET /resources/applicants/-/levels` |
| Workflows (auto-find the one referencing the level) | `GET /resources/api/applicantWorkflows` + `GET /resources/api/applicantWorkflows/{id}` |
| Questionnaire **content + scores** | `GET /resources/api/questionnaires/{id}` |
| PoA / cross-check preset | `GET /resources/api/poaStepSettings/{id}` · `GET /resources/api/crossCheckPresets/{id}` |
| Entitlements (`allowedChecks` keys) | `GET /resources/api/agent/settings/bgCheckTargets` |

## Auth — App Token + secret (sandbox only)

This skill talks to the public Sumsub API and signs each request per
[the authentication reference](https://docs.sumsub.com/reference/authentication). The how-it-works
writeup lives in [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md).

> **⚠️ Sandbox tokens only.** Read-only, but still: do not accept a production App Token. If the user
> offers one, refuse and ask for a sandbox pair at
> <https://cockpit.sumsub.com/checkus/home?sbx=true> (**Connect Sumsub to your AI agent** ->
> **Build & configure** -> **Generate token**). The helper
> rejects tokens that don't start with `sbx:`.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` |
| `SUMSUB_SECRET_KEY` | paired secret |
| `SUMSUB_BASE` / `SUMSUB_ENV=dev` | optional; `dev` targets `dev-api.sumsub.com` (internal). |

## Procedure

> **Use the scripts — do not hand-roll the deterministic steps.** The whole point of this skill is
> that resolution and the verdict are deterministic, not re-derived by eyeball each run:
> - **Resolve the graph ONLY via `resolve_graph.sh`.** Do **not** call `/resources/...` endpoints
>   directly, list levels by hand, or strip the `HTTP <code>` trailer yourself — the script does all
>   of that and emits one clean graph.
> - **If the graph can't be resolved, STOP — never work around the failure.** A `401`/`403`, a `404`,
>   or `0 levels` / "level not found" from `resolve_graph.sh` means the run cannot proceed. Report the
>   failure plainly (likely a bad/non-sandbox token or wrong level name) and stop. Do **not** edit
>   `resolve_graph.sh` (or any script) to route around the error, add a by-id fallback, retry a
>   different endpoint, or otherwise improvise a graph — and **never** emit a report, bucket counts, or
>   a CONFORMANT verdict from a partial or substituted graph. No resolved graph → no findings.
> - **Derive the verdict ONLY from `trace.py` / `report.py`.** Do **not** read the workflow/questionnaire
>   JSON by eye and decide "enforced / not enforced" yourself — that re-introduces variance and
>   hallucination. The `COLLECTED-NOT-ENFORCED` finding must come from the engine.
> - **If a script already ran, trust its output — do not re-verify it with manual API calls.**
> - **To inspect the graph for the Map step, run `python3 scripts/graph_summary.py "$CONFIG"`.** Do
>   **not** hand-iterate the graph JSON: `questionnaires`/`poaPresets`/`crossCheckPresets` are **dicts
>   keyed by id** (iterating yields id strings → `'str' has no attribute 'get'`) and `entitlements`
>   is a **list**. `graph_summary.py` prints the section/item indices + scores you need, correctly.
> The agent's judgment belongs to two steps only: ingest (reading the regulation) and map (matching
> requirements to deployed config elements — questions, docSets, fields, countries, entitlements).
> Everything else is the scripts.

> **Artifacts — MANDATORY location & naming.** Every run MUST write its artifacts into the **same
> directory as the source regulation file**, named from its **stem** (filename without extension).
> Never save in the cwd or under improvised names. Derive the exact paths once, up front:
> ```
> eval "$(python3 scripts/artifact_paths.py "<path/to/RegFile.pdf>")"
> #  $REQUIREMENTS = <dir>/<stem>_regulations.json   (the requirements you build in steps 1+3)
> #  $CONFIG       = <dir>/<stem>_config.json         (resolve_graph output, step 2)
> #  $REPORT       = <dir>/<stem>_report.md           (the rendered report, step 6)
> ```
> e.g. `Level4regulations.pdf` → `Level4regulations_regulations.json`, `Level4regulations_config.json`,
> `Level4regulations_report.md`. Use `$REQUIREMENTS` / `$CONFIG` / `$REPORT` verbatim in the steps below.

1. **Ingest the regulation** (judgment). **Just Read the document with the Read tool — it reads PDFs natively (renders pages + extracts text), so nothing needs to be installed.** For a PDF over ~10 pages, Read it in page ranges (the Read tool's `pages` parameter, ≤20 pages per call). Reading visually is equal or better than a text extractor — it preserves tables, headings and layout that flat-text extraction loses. *Optional, only if already installed and never a blocker:* `pypdf`/`pdftotext` can pull a long, text-heavy PDF in one shot, and `scripts/render_regulation.py` (PyMuPDF) pre-renders a scanned/image-only PDF to PNGs for explicit DPI control — see [`references/conformance-method.md`](references/conformance-method.md) step 1. If a library is absent, just Read the PDF directly.
   Then extract requirements and write them to **`$REQUIREMENTS`** (the `<stem>_regulations.json` beside
   the source — see the Artifacts rule above), per
   [`references/requirements-schema.md`](references/requirements-schema.md): each = `{id, source,
   text, type, enforceable, …}`. **Always capture `source`** — the citation into the original document
   (section number / heading / page, e.g. `"§5.9.2"`, `"Section 2 — Scoring Result"`, `"p.21"`); the
   report leads with it so findings trace back to the regulation, not to an artificial id. Mark
   outcomes that live in SDK/platform/CRM as `enforceable: sdk|platform`.
   **Show the extracted requirements to the user and confirm before tracing** — this is the
   highest-risk step.
2. **Resolve the deployed graph** (deterministic). `bash scripts/resolve_graph.sh <levelNameOrId> > "$CONFIG"`
   (level + questionnaires-with-scores + presets + auto-found workflow + entitlements). **This one
   command replaces any manual level-listing / curl / HTTP-trailer stripping — don't do those by hand.**
3. **Map** (judgment). **First inspect the graph: `python3 scripts/graph_summary.py "$CONFIG"`** — it
   prints questionnaires with `[section]/[item]` indices + option scores, docSets, APPLICANT_DATA fields,
   geo, entitlements, and the workflow (don't hand-iterate the JSON). Then for each requirement pick the
   right `type` and fill its `match` — **not everything is a questionnaire question.** The
   per-type `match` shapes are in [`references/requirements-schema.md`](references/requirements-schema.md):
   - questionnaire question/score → `match: {questionnaire, section, item}` (+ `expectScores`);
   - document collected → `match: {docSet: "IDENTITY", types: [...]}`;
   - **applicant-data field present** → `type: data-field`, `match: {field: "dob"}` / `{fields: [...]}`;
   - country allowlist / prohibited jurisdictions → `type: country-eligibility`, `match: {mustHaveAllowlist: true}` / `{mustExclude: [...]}`;
   - selfie liveness → `type: liveness`, `match: {}`;
   - capability provisioned → `type: entitlement`, `match: {entitlement: "WATCHLISTS"}`;
   - screening/routing outcome → set a **discriminating** `enforcementSignal` (NOT a generic token).
   Be conservative: if unsure a thing exists, leave `match: null` (→ MISSING) rather than guess.
4. **Trace** (deterministic). `python3 scripts/trace.py --requirements "$REQUIREMENTS" --graph "$CONFIG"`
   → findings bucketed **MISSING / SCORING-MISMATCH / COLLECTED-NOT-ENFORCED / NOT-CONFIG-REPRESENTABLE /
   CONFORMANT**, each with evidence + a `basis` (deterministic vs judgment). **The bucket verdict comes
   from here — do not decide "enforced / not enforced" by reading the workflow JSON yourself.**
5. **(Optional) hygiene sub-pass.** Pipe the same graph through the bundled linter to catch silent
   misconfigurations (entitlement gaps, dangling preset/questionnaire refs, deprecated SDK, invalid AML
   provider) alongside conformance — entitlements are read straight from the graph:
   `bash scripts/resolve_graph.sh <level> | python3 scripts/lint_config.py`. Rule catalog in
   [`references/lint-rules.md`](references/lint-rules.md) (generated from `references/rules.json`).
6. **Report — render with the canonical formatter to `$REPORT`, do NOT hand-format.** The format is
   fixed so every run looks identical:
   `python3 scripts/trace.py --requirements "$REQUIREMENTS" --graph "$CONFIG" | python3 scripts/report.py --date <today> > "$REPORT"`
   → Markdown with a headline status, a fixed bucket-count table, findings grouped in fixed order (each
   with evidence + `basis`), and a fixed caveats footer. Present `$REPORT` verbatim. Do not re-summarise
   it in prose — that's what made past runs differ. (The `trace.py` JSON is the other canonical format
   for tooling — save it beside the others if a machine consumer needs it.)

## What it does NOT do (say it)

- Not a compliance guarantee or a replacement for a compliance officer.
- Does not verify **semantic** correctness beyond presence + scores + routing-enforcement
  (e.g. whether a question's wording is legally adequate is judgment).
- Cannot verify SDK/platform/CRM outcomes (disclosure pop-ups, demo accounts, read-only mode,
  the 25%/10% restriction, CRM timestamps) — these are bucketed `NOT-CONFIG-REPRESENTABLE`.

## Guardrails

- Keep **deterministic facts separate from judgment** (the `basis` field). Never present a mapping
  guess as a verified finding.
- The trace walks **requirements → deployment only** — it never flags a deployed question as
  "extraneous" (avoids the false-positive class). Report extra questions, if at all, as an explicit
  advisory note.
- `enforcementSignal` must be **discriminating** — a generic token (`country`) matches catch-all
  edges and yields false CONFORMANT. See [`references/requirements-schema.md`](references/requirements-schema.md).
- **Fail honestly — never work around a resolution failure.** If `resolve_graph.sh` returns an auth
  error / 404 / `0 levels`, stop and report it. Do not edit the scripts to bypass it or fabricate a
  report from a partial graph (see the Procedure callout).

## See also

- [references/requirements-schema.md](references/requirements-schema.md) — the requirement model + buckets.
- [references/conformance-method.md](references/conformance-method.md) — the five steps, guardrails, scope.
- [references/lint-rules.md](references/lint-rules.md) — the bundled hygiene-lint rule catalog (sub-pass).
- [`sumsub-analyze-regulation`](../sumsub-analyze-regulation/SKILL.md) — the opposite direction (regulation → build plan).

## Worked examples (`examples/`)

- `sample-requirements.json` + `sample-graph.json` — synthetic, exercise every bucket (drive `test_trace.py`).
- `fiu-india-vasp-mapped.json` + `vasp-graph.json` — a broad AML guideline mapped against a hypothetical
  VASP level; **self-contained, trace them together offline**:
  `python3 scripts/trace.py --requirements examples/fiu-india-vasp-mapped.json --graph examples/vasp-graph.json | python3 scripts/report.py`.
- `cfd-requirements.json` — real CFD/MiFID requirements (run against a live `cfd-onboarding-eu` graph).
- `fiu-india-requirements.json` — the ingest-stage output for that broad guideline (before mapping).
- `audit-input{,-dirty}.json` — hygiene-linter fixtures (drive `test_lint.py`).
