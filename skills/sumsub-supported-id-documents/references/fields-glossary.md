# Country document fields — glossary

Reference for the **editable** fields of a `CountryDocument` (one entry in
`countryMappings[<country>][<docType>]`). Use this to explain a change to the
user on the confirmation step and to build a correct change spec.

Set any of these keys in a change spec — `build_country_mappings.py` writes them
straight into the country/doc-type config (the field-recognition keys
`defaultFields`/`extraFields` get the category handling described below). Keys you
don't set keep their baseline value. Truly internal keys not listed anywhere here
(`shouldBeMaskedSettings`, `documentReferences`, …) are passed through untouched —
don't invent values for them.

## The full "Fields management" screen → spec keys

Every control on the dashboard "Fields management" drawer maps to one field:

| UI control | Spec key | Type / values | Mapping |
|---|---|---|---|
| **Accept digital documents** | `acceptDigitalDoc` | boolean | `true` = also accept documents submitted as **images/files** (scans, PDFs, digital copies). When `false`, file/scan/PDF **uploads** are dropped — this governs the upload axis ONLY, not screenshots (`acceptScreenshots` is separate). Don't paraphrase a `false` value as "only live camera photos" without also stating the screenshot flag. |
| **Accept document screenshots for POI** | `acceptScreenshots` | boolean | `true` = turn OFF screenshot protection for POI (⚠️ fraud risk). A **separate** fraud control — see the disambiguation below. |

### `acceptScreenshots` and `acceptDigitalDoc` are INDEPENDENT checks

They gate different things and neither requires the other:

- **`acceptScreenshots`** — its own check (`DocumentLivenessRejectionReasonProvider`:
  a screenshot is rejected only when `acceptScreenshots` is false). So
  **`acceptScreenshots: true` alone makes screenshots accepted** — you do NOT also
  need `acceptDigitalDoc`. There is no "camera-only" pre-filter that drops a
  screenshot before this check.
- **`acceptDigitalDoc`** — separate check for uploaded files/scans/PDFs/digital
  copies.

Consequences:
- **"Accept screenshots"** → set `acceptScreenshots: true` only. Don't touch
  `acceptDigitalDoc`.
- **"Screenshots are on globally but still rejected"** → most likely the applicant
  is on a **Verification Level whose own document settings override global**
  (level settings win when the level has `useCustomIdDocSettings: true`). Check that
  level's `idDocSettings`, not `acceptDigitalDoc` — and fix it there via the
  [`sumsub-create-level`](../../sumsub-create-level/SKILL.md) skill (set
  `acceptScreenshots: true` on the level's `idDocSettings.countryMappings` entry).

If a request maps to several of these fields and the intent isn't unambiguous
(e.g. broad phrasings about what kinds of documents to accept), **ask the user
which fields they mean rather than guessing** — these are fraud-sensitive and
easy to over-reach.
| **Custom ID document expiry settings** (dropdown) | `expirationCheckMode` | enum: `allowExpired`, `strict`, `generallyAcceptedRegulations`, `localRegulations` | the dropdown value |
| **Accept documents with no valid expiry date** (checkbox) | `expirationCheckMode` | — | checked ⇒ `localRegulations`; unchecked ⇒ `generallyAcceptedRegulations` (same field as above) |
| **Mode: Default / MRZ document** | `ocrSettings.ocrRuleMode` | enum: `DEFAULT`, `MRZ_DOC` | Default ⇒ `DEFAULT`; MRZ document ⇒ `MRZ_DOC` (see note below) |
| **Preferred characters: Latin / Non-latin** | `ocrSettings.preferNonLatinFromOcr` | boolean | Latin ⇒ `false`; Non-latin ⇒ `true` (see note below) |
| **Subtypes: Accept all** | `allowedOcrDocumentTypes` + `forbiddenOcrDocumentTypes` | string[] | both empty `[]` |
| **Subtypes: Accept only selected** | `allowedOcrDocumentTypes` | string[] | list of allowed OCR subtype ids |
| **Subtypes: Reject only selected** | `forbiddenOcrDocumentTypes` | string[] | list of rejected OCR subtype ids |
| **Hide document subtypes for applicants in WebSDK** | `disableDocumentReferences` | boolean | `true` = hide subtypes in WebSDK |
| **Default Fields** (checkboxes) | `defaultFields` | string[] | see below — free recognition |
| **Extra Fields** (checkboxes) | `extraFields` → `availableFields` (wire) | string[] | see below — PAID recognition |
| **Document sides** (one/two/smart) | `sidesSelectionMode` | enum (`disabled`,`smartMode`,`oneSide`,`twoSides`) | see note below |

**Deprecated — read-only, never write.** `supported`, `doubleSided`,
`doubleSidedCanBeChanged`, `acceptedAsPoa`, `acceptSameDocAsPoa` are deprecated
on the backend and `build_country_mappings.py` rejects them. They still show up
in GET responses (catalogue and current settings) — read them for context only.
Replacements: "accept this doc type at all" and sides → `sidesSelectionMode`
(`disabled` = don't accept); the POA flags have no replacement here — decline
such an edit.

**Gated — read-only, never write.** `shouldBeSigned` (require a signature — in
the dashboard the checkbox exists only behind the
`showRejectByMissingSignatureSetting` feature flag; enabling the field makes
autochecks reject unsigned documents) and `shouldBeMasked` (see the Masking
section below) are rejected by `build_country_mappings.py`. Explain the gate and
point the user to the dashboard / Sumsub support instead.

> When setting `ocrSettings`, pass the whole nested object, e.g.
> `ocrSettings: {ocrRuleMode: MRZ_DOC, preferNonLatinFromOcr: false}`.
> The OCR subtype ids for `allowedOcrDocumentTypes`/`forbiddenOcrDocumentTypes`
> are the `documentReferences[].ocrDocumentTypes` values from the catalogue /
> current settings (e.g. `bra.id.type1`).

### Custom ID document expiry settings (`expirationCheckMode`)

Controls which documents are accepted based on their expiry date. From strictest
to most lenient (the exact UI dropdown wording):

| Value | UI label | Accepts |
|---|---|---|
| `strict` | "Accept only valid documents" | only non-expired, currently-valid documents |
| `generallyAcceptedRegulations` | "Accept valid and officially extended documents" | valid + officially extended documents |
| `localRegulations` | "Accept valid and officially extended documents and accept document with no valid expiry date" | the above **plus** documents with no valid expiry date |
| `allowExpired` | "Accept valid and expired documents" | valid **and** expired documents (most lenient) |

The **"Accept documents with no valid expiry date"** checkbox is a shortcut on top
of this: ticking it switches `generallyAcceptedRegulations` → `localRegulations`
(the difference between those two is exactly "also accept no-expiry-date docs").

When to use which: `strict` for the tightest control; `generallyAcceptedRegulations`
is the common default; `localRegulations` when documents legitimately lack an expiry
date in that country; `allowExpired` only when expired documents must be accepted.

**What "officially extended" means** — the modes that accept extended documents
(`generallyAcceptedRegulations` / `localRegulations`) rely on Sumsub's built-in
**expiry-extension rules** (e.g. "Brazilian ID — owner 60+ valid indefinitely; new
type valid until 01.03.2032"). These are read-only reference data baked into Sumsub
(not a client setting, can't be edited). Read them with `get_extension_rules.sh`
(`GET /resources/api/agent/globalSettings/extensionRules`) — `general` rules apply
broadly, `local` rules apply under `localRegulations`. The dashboard shows the
matching rule text in the blue info box under "Custom ID document expiry settings".

### Mode: Default vs MRZ document

MRZ = Machine Readable Zone — the `<<<` lines at the bottom of passports and many
ID cards that machines read directly.

- **`DEFAULT`** — normal mode. OCR reads the document's visual fields; the document
  is processed even if a field required by the settings is absent from the subtype.
  An MRZ is not required.
- **`MRZ_DOC`** — the document is **rejected if it has no MRZ line**. The backend
  requires at least one MRZ field to be read (the first MRZ line is mandatory; the
  others are required only if present on the document).

When to use which: pick `MRZ_DOC` for documents where an MRZ must be present
(passports, MRZ-bearing IDs) — it's stricter and more reliable, since the MRZ is
harder to forge and parses more accurately. Use `DEFAULT` for documents without a
mandatory MRZ.

### Preferred characters: Latin vs Non-latin

Controls which alphabet OCR extracts the data in.

- **Latin** (`preferNonLatinFromOcr: false`, default) — OCR prefers Latin
  characters, transliterating the data into the Latin alphabet (as in the MRZ).
- **Non-latin** (`preferNonLatinFromOcr: true`) — OCR prefers the document's
  **native non-Latin script** (Arabic, Cyrillic, CJK, Thai, …) rather than a
  transliteration.

When to use which: set **Non-latin** for documents from countries with a
non-Latin writing system when you want names/fields captured in the original
script instead of a Latin transliteration; otherwise leave it Latin.

### Document sides

How many sides the applicant must submit. On the main **"Supported ID Documents"**
screen each country/doc-type cell is a dropdown; its options map to
`sidesSelectionMode` like this:

| Dropdown option (UI) | `sidesSelectionMode` | Meaning |
|---|---|---|
| **One Side** | `oneSide` | always ask for a single side |
| **Two Sides** | `twoSides` | always ask for both sides |
| **Smart mode** | `smartMode` | auto-detect how many sides are needed |
| **Any Side** | *(not set — left unset)* | accept any one side of a two-sided doc (only offered for doc types in the any-sides catalogue) |
| **Don't accept** | `disabled` | this doc type is not accepted for this country |

So "Don't accept" = `sidesSelectionMode: disabled` (equivalent to disabling the
doc type), and the three positive options set `oneSide` / `twoSides` /
`smartMode`. "Any Side" is a special case — the UI leaves `sidesSelectionMode`
unset; only use it when the user explicitly wants "any single side" and the doc
type supports it.

`doubleSided` (both sides required) and `doubleSidedCanBeChanged` (whether the
client may flip it) are **deprecated** — replaced by `sidesSelectionMode`. Read
them for context (the catalogue/current settings still carry them), but they are
not settable: `build_country_mappings.py` rejects them — always set
`sidesSelectionMode` instead.

> **Sides-loss note.** Historically a sparse override created without sides (e.g.
> by only setting `extraFields`) degraded a two-sided document to "Any Side" —
> the backend read-merge did not backfill the deprecated `doubleSided` from the
> catalogue default. Fixed on the backend behind the temp feature flag
> `backfillDoubleSidedInCountryMappings`. If a user reports a document showing
> "Any Side" after a fields edit, check that flag is enabled for the client; the
> immediate manual fix is setting an explicit `sidesSelectionMode` on the pair.

**Priority — `sidesSelectionMode` wins over `doubleSided`.** The backend resolves
sides as: if `sidesSelectionMode` is set, use it (`twoSides` ⇒ double-sided);
otherwise fall back to the legacy `doubleSided` boolean. So if a doc's current
settings show "uses the legacy doubleSided", it just means `sidesSelectionMode`
isn't set there — sides come from `doubleSided`, which still works. Setting
`sidesSelectionMode` via this skill's edit flow is safe: it takes effect immediately and overrides
`doubleSided` (the old field stays in the data but is ignored). Don't try to keep
both in sync — just set `sidesSelectionMode`.

### Masking (`shouldBeMasked` / `shouldBeMaskedSettings`) — NOT editable here

`shouldBeMasked` (boolean) turns on **masking of sensitive data** on the document
(e.g. covering parts of a number); `shouldBeMaskedSettings` (`MaskingSettings`)
holds the detailed masking rules. The catalogue defines it only for legally
protected national identifiers (JPN My Number, KOR RRN, NLD BSN, NGA NIN, SGP
NRIC — all default `true`), and for NGA ID_CARD even the dashboard lets only
Sumsub staff change it. Turning masking off may violate local law, so this skill
does not edit either key (`build_country_mappings.py` rejects `shouldBeMasked`;
`shouldBeMaskedSettings` is internal pass-through). Report their values freely;
for changes, point the user to the dashboard OCR constructor or Sumsub support.

## Recognition fields (Default Fields / Extra Fields)

| Field | Type | Meaning |
|---|---|---|
| `defaultFields` | string[] | The **"Default Fields"** column — fields checked here are recognised, free of charge. Checked by default; omit one to uncheck it (stop recognising). |
| `extraFields` (spec) → `availableFields` (wire) | string[] | The **"Extra Fields"** column — fields checked here are recognised but ⚠️ **billed** (see below). Unchecked by default. The spec uses `extraFields`; the script maps it to the API's `availableFields`. |

> **You can't empty the whole Default Fields column.** Sending `defaultFields: []`
> (or omitting the list on a sparse override) does **NOT** disable all default fields —
> the backend keeps the catalogue defaults whenever the client's list is empty/absent
> (`OcrFieldsInfoModel#enrichWithClientCountryDocument` only overrides on a NON-EMPTY
> list). At least one default field always stays on. To stop recognising a specific
> field, send the remaining fields you DO want (the column is replaced wholesale) — not
> an empty list, which silently no-ops. `build_country_mappings.py` rejects
> `defaultFields: []` for this reason. The Extra Fields column is the opposite: its base
> is empty and your `extraFields` list only adds.

> **`dob` (date of birth) can have a downstream effect — but only where an age-based
> rule exists.** Some **expiry-extension rules** depend on the holder's age (e.g. BRA
> ID "owner 60+ ⇒ valid indefinitely") and can only be evaluated when `dob` is
> recognised. Before warning that disabling `dob` breaks expiry checks, **check
> whether such a rule actually applies to this `(country, docType)`** by reading the
> extension rules — run [`../scripts/get_extension_rules.sh`](../scripts/get_extension_rules.sh)
> and filter to the pair (same call as SKILL.md procedure **C**). Most doc types
> (e.g. passports) have no age-based rule, so turning `dob` off there is harmless and
> needs no warning. Only flag it when an age-based extension rule exists for that pair.

## The two columns mirror the dashboard "Fields management" screen

The spec keys map 1:1 to the UI:

| Spec key | UI column | Cost | Default state |
|---|---|---|---|
| `defaultFields` | Default Fields | free | checked (recognised) |
| `extraFields` | Extra Fields | PAID (needs `ADVANCED_OCR`) | unchecked |

You just list which fields are **checked** in each column — exactly what you'd
tick in the UI. The script prints a `Field recognition result:` summary in the
same language so the user can cross-check against the screen.

## A field's column is FIXED by the catalogue — you can't move it

A field belongs to exactly one column — **Default Fields** or **Extra Fields** —
and that assignment is baked into the catalogue (`documents-by-countries.json`)
per country and doc type. You **cannot** put e.g. `placeOfBirth` under
`defaultFields` for a doc type where it's an Extra Field — the backend validates
against the fixed column and **silently drops** the misplaced field (PUT still
returns 200).

`build_country_mappings.py` guards against this: it auto-routes each field to its
real column and prints a `warning:` for every correction. Trust those warnings —
if it says a field was moved, that's the only column the backend accepts it in. To
see which column a field lives in, read the catalogue first (a `{country, docType}`
query returns the canonical Default / Extra split).

## ⚠️ Extra Fields require the ADVANCED_OCR entitlement (extra cost)

"Extra Fields" (`extraFields` in the spec, `availableFields` on the wire) are a
**paid add-on**, gated behind the client's `ADVANCED_OCR` entitlement. If the
client does **not** have `ADVANCED_OCR`, the backend **silently clears** them when
reading the settings (`GlobalSettingsHelper.mergeCountryDocumentWithDefault`) —
there is no error.

Consequences for an edit:

- Before checking any `extraFields` for a client, confirm they have `ADVANCED_OCR`
  in their entitlements (a key of `allowedChecks` from `sumsub-check-permissions`).
- If they don't, warn the user that extra fields incur additional cost and that
  the change will be dropped server-side until `ADVANCED_OCR` is enabled — do
  not report success.
- Default Fields are NOT gated and carry no extra charge.

## Field-name values are per country/doc type

The valid field names for each column are **not** a fixed global list — they vary
by country and document type. Don't guess them. Read the catalogue first to learn
what's valid for the target country/doc type:

```bash
echo '{"countries":["DEU"],"docTypes":["ID_CARD"]}' \
  | query_supported_docs.py --data-file /tmp/supported-docs.json
```

The returned `defaultFields` (Default Fields column) + `availableFields` (Extra
Fields column) are exactly the names you may use in a change spec — `defaultFields`
under `defaultFields`, `availableFields` under `extraFields`.
