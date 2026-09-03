---
name: sumsub-create-cross-check-preset
description: Create or update a Sumsub cross-check preset (name/address comparison rules between POI and POA documents) via `POST/PATCH /resources/api/agent/crossCheckPresets` and `GET /resources/api/agent/crossCheckPresets/{id}`. TRIGGER **ONLY** when the user EXPLICITLY asks to override how cross-checks compare names or addresses — e.g. "switch name match to strict", "allow fuzzy address match", "ignore middle-name mismatch", "create a custom cross-check preset". SKIP by default — Sumsub ships sensible defaults tuned for the best conversion and approval rate, so most clients should NOT create a custom preset. SKIP for level creation (the default cross-check preset auto-applies to every level), for general KYC config, or any request that doesn't specifically name "cross-check rules", "name comparison", or "address comparison".
allowed-tools: Read, Write, Bash
---

# Sumsub — Create / Update Cross-Check Preset

> **⚠️ Read this before running this skill.**
>
> Sumsub's default cross-check preset is tuned for the best balance of
> conversion and approval rate. **Most clients should not override it.** If
> the user hasn't named a specific comparison they want to change, stop and
> say:
>
> > "Cross-check rules are already configured for the best approval rate.
> > We strongly recommend keeping the defaults. Tell me a specific tweak
> > you need (e.g. 'allow fuzzy address match', 'ignore middle name') and
> > we'll create a minimal override."
>
> Only proceed if the user has a concrete, named tweak.

## What is a cross-check preset

A cross-check preset controls how Sumsub compares the name and address that
appear on the **proof-of-identity (POI)** document with the same fields on
the **proof-of-address (POA)** document. The preset decides whether small
differences ("Jonathan" vs "Jon", "Apt 4" vs "Apartment 4") are accepted or
flagged as mismatches.

> **Don't confuse with PoA preset's `crossValidator`.** The
> `sumsub-create-poa-preset` skill has an internal block called
> `crossValidator` (`CrossValidatorSettings` on `PoaDocumentSettings`) with
> `nameMode` / `addressMode` / `fuzzyThreshold` — that's a **per-PoA-preset
> override** for the same comparison. A workspace-level CrossCheckPreset
> (this skill) supplies the default when no PoA-preset override applies.
> When a PoA preset's `crossValidator` is set, it wins for documents
> handled by that preset.

There are two preset modes:

- **`basic`** — what this skill creates. Picks `nameComparisonMode` and
  `addressComparisonMode` from a small enum, plus optional ignore-flags.
  Best for almost everyone.
- **`advanced`** — per-rule manual configuration. **Not supported via the
  public API** (`POST` returns `403 Forbidden — Advanced cross-check presets
  cannot be managed via API`). Has to be done in the dashboard.

## Endpoints

| Method | Path | When |
|---|---|---|
| `POST` | `/resources/api/agent/crossCheckPresets` | Create a new preset. Body must NOT include `id`. |
| `PATCH` | `/resources/api/agent/crossCheckPresets` | Update an existing preset. Body MUST include `id`. |
| `GET` | `/resources/api/agent/crossCheckPresets/{id}` | Read one preset back (verify what landed; resolve `title` from a known `id`). |

All require permission `manageClientSettings`. Body shape is the
[cross-check preset schema](references/cross-check-preset-schema.md) —
client-settable fields only.

## Auth — App Token + secret (sandbox only)

This skill talks to the public Sumsub API and signs each request per
[the authentication reference](https://docs.sumsub.com/reference/authentication).
The full how-it-works writeup lives in the [`sumsub-api-auth`](../sumsub-api-auth/SKILL.md)
skill — read it if you hit `401 Invalid signature`.

> **⚠️ Sandbox tokens only.** Do **not** accept or use a production App
> Token here — cross-check rules affect every verification on the
> workspace. If the user offers a prod token, refuse and ask them to
> generate a sandbox pair at
> <https://cockpit.sumsub.com/checkus/home?sbx=true> (**Connect Sumsub to
> your AI agent** -> **Build & configure** -> **Generate token**). Token +
> secret are shown once — copy both before closing the dialog. The helper scripts
> enforce this — they reject tokens that don't start with `sbx:`.

| Var | Example |
|---|---|
| `SUMSUB_APP_TOKEN` | `sbx:...` — sandbox App Token from the dashboard. |
| `SUMSUB_SECRET_KEY` | The paired secret shown once at token creation. |
| `SUMSUB_BASE` | Optional. Defaults to `https://api.sumsub.com`. |

If the user has already supplied credentials in conversation, reuse them;
otherwise ask once before running. Never echo the secret back.

## Procedure

1. **Confirm necessity** — Restate the user's request in one sentence and
   re-state the recommendation to keep defaults. If they have a specific
   named tweak, proceed. Otherwise stop.
2. **Translate the user's intent into the compact spec** (below). Map their
   ask to `nameComparisonMode` / `addressComparisonMode` / ignore-flags.
3. **Validate** — `title` non-empty (≤256 chars); `mode` is `basic`
   (advanced is forbidden via API); every comparison mode is a valid enum.
4. **Generate payload** — run `${CLAUDE_SKILL_DIR}/scripts/build_cross_check_preset.py` with the compact spec on stdin → full payload on stdout.
5. **Create vs. update**:
   - **New preset** — POST via `${CLAUDE_SKILL_DIR}/scripts/post_cross_check_preset.sh`. Payload must NOT include `id`.
   - **Update existing** — first GET via `${CLAUDE_SKILL_DIR}/scripts/get_cross_check_preset.sh` so the user sees the diff, then PATCH via `${CLAUDE_SKILL_DIR}/scripts/patch_cross_check_preset.sh`. Payload must include `id`.
6. **GET the preset back** and verify what landed.
7. **Report** — lead with the human-readable summary, end with the id:
   - `title` and a one-line summary of what was tweaked vs. the default.
   - **Reminder**: "Default cross-check rules are recommended for the
     highest approval rate; you've now overridden them for these
     comparisons — monitor conversion before rolling to production."
   - Final line: `Preset ID (for level wiring / future PATCH): <id>`.

## Compact spec format (JSON or YAML on stdin)

```yaml
title: "Strict address, lenient name"
description: "Allow nickname variants but require exact address."

mode: basic                          # ONLY basic — advanced is forbidden via API
basicSettings:
  nameComparisonMode: weakContainment  # one of: strict | weakContainment | def | ai
  addressComparisonMode: strict        # one of: strict | fuzzy
  ignoreMiddleNameMismatch: true
  ignoreProvidedInfoMismatch: false    # if true, don't flag user-typed info that disagrees with the doc
```

### Comparison-mode meaning

`nameComparisonMode`:
- `strict` — exact match required.
- `weakContainment` — token-level containment (e.g. "Jon Smith" ⊆ "Jonathan Andrew Smith").
- `def` — Sumsub's recommended default; balances strictness and conversion.
- `ai` — ML-based comparison; tolerant of common variants and transliterations.

`addressComparisonMode`:
- `strict` — character-level match (after normalisation).
- `fuzzy` — tolerant of abbreviations and word order.

The deprecated values (`fuzzy`, `containment`, `fuzzyContainment` on names)
are NOT accepted via this skill.

## Outputs

On success, lead with the human-readable info:
- `title` and a one-line summary of what was tweaked vs. the workspace default.
- **Reminder**: "Default cross-check rules are recommended for the highest approval rate; you've now overridden them — monitor conversion before rolling to production."
- Final line: `Preset ID (for level wiring / future PATCH): <id>`.

On failure: HTTP status + Sumsub's `description` / `errorName`. Common causes:
- `403 Advanced cross-check presets cannot be managed via API` — `mode: advanced` is dashboard-only. Switch to `basic` mode.
- `400` with a validation message — one of the comparison-mode enums is wrong (e.g. a deprecated `fuzzy` / `containment` / `fuzzyContainment` name mode).

## Worked examples

- [`examples/strict-name-only.json`](examples/strict-name-only.json) — tighten name match, leave address on defaults.
- [`examples/lenient-for-emerging-markets.json`](examples/lenient-for-emerging-markets.json) — fuzzy address + ai name, ignore middle-name mismatch.

## Hand-off — attaching the preset to a level

Cross-check presets are *workspace-scoped*. The default preset
auto-applies to every level; if you've created a custom one, you have to
attach it to specific levels by setting `crossCheckPresetId` on the level.
That's done with `sumsub-create-level` (or a direct PATCH on the level via
`sumsub-api-generic`).

## See also

- [references/cross-check-preset-schema.md](references/cross-check-preset-schema.md) — full schema, every enum, gotchas.
- [Sumsub cross-check docs](https://docs.sumsub.com/docs/cross-checks).
