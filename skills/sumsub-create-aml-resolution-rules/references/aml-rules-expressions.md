# AML resolution rules expression reference

The inventory of every legal `exp` path, field type, built-in function, and enum value usable in AML resolution rule conditions and review actions, generated from Sumsub's `AmlRuleExpressionContext` schema. Open it whenever a rule needs an `exp` path (or an allowed value) you can't quote from memory, or to verify one before POSTing.

**This reference is split into three files** (this one is the index):

1. **This file** — preamble: how to use the reference, root variables, the shared `applicant` / `applicantIdDoc` and `Date` shapes, and the enum caveat below.
2. [**`aml-rules-context-fields.md`**](aml-rules-context-fields.md) — every legal dotted `exp` path with its type (`## Types` / `## Index` / `## Functions`).
3. [**`aml-rules-enumerations.md`**](aml-rules-enumerations.md) — the allowed **values** for fields that are closed enums (see the caveat below).

> **⚠️ Enum caveat — many `String` / `List of String` fields are actually closed enums.** In the context-fields doc, most enum-backed fields (risk labels, match statuses, PEP institution kinds, match types, quantifind levels, entity type, …) appear only as plain `String`, without their allowed values. Those vocabularies live in [`aml-rules-enumerations.md`](aml-rules-enumerations.md) — **check there for the valid values before comparing against such a field**, and remember a closed set means "only X" is `containsOnly ["X"]`, never `notContainsAny [the-others]`. (`TargetEntityType` and `VendorType` are tabled inline in the context-fields doc; the rest are in the enumerations file.)

**Efficient access — don't read end-to-end; this is a lookup database.**

- **Validate a path:** `grep '<leafFieldName>' aml-rules-context-fields.md`. The leaf field name (the last component of the path) appears verbatim in both the Types row and the Index entry. Searching for a full dotted path like `match.analysis.tinCompatible` returns no matches — the Index renders each segment as a markdown link so the dotted form is not a contiguous substring.
- **Find a field's allowed values:** search [`aml-rules-enumerations.md`](aml-rules-enumerations.md) — each enum lists the `exp` paths that use it under **Used by**, so you can go from a field to its vocabulary and back.
- **Explore a namespace:** open [`aml-rules-context-fields.md`](aml-rules-context-fields.md) and jump to the `### <TypeName>` section directly. Anchors are stable (`#ScreeningInputExpressionData`, `#AmlCaseExpressionData`, `#HitExpressionData`, …).

**Root variables.** `applicant` (the applicant being screened), `applicantIdDoc` (their identity document), `input` (the data sent to the AML vendor for screening), `screening` (the AML case as a whole), `match` (the current hit under evaluation — rule conditions run once per unreviewed hit).

**`applicant` and `applicantIdDoc` paths.** The generated tables type them as plain `Object`: they reuse the applicant / POI document shapes shared with workflow expressions. For their field lists, see [`../../sumsub-create-workflow/references/workflow-expressions.md`](../../sumsub-create-workflow/references/workflow-expressions.md) — the `applicant` (`#ApplicantExpressionData`) and `poi` (`#PoiExpressionData`) types are the same shapes.

**`Date` fields.** Every field typed `Date` (e.g. `input.dob`, `match.previousReview.modifiedAt`, `match.sources.latestEndDate`) exposes these sub-fields:

| Field | Type | Description |
| --- | --- | --- |
| `timestamp` | `long` | Unix timestamp in milliseconds |
| `yyyymmdd` | `int` | Numeric day in YYYYMMDD format, e.g. 20230123 |
| `year` | `int` | Year |
| `month` | `int` | Month of year (starts from 1) |
| `dayOfMonth` | `int` | Day of month (starts from 1) |
| `ageInYears` | `int` | Time delta in years between this date and now |
| `ageInDays` | `int` | Time delta in days between this date and now |

So `match.sources.latestEndDate.ageInDays > 366` means "the latest source end date is more than a year ago", and `match.previousReview.modifiedAt.ageInYears < 2` means "the previous review is less than two years old".

**Out of scope here.** These files list paths, types, functions, and enum values only. Operators (`eq`, `in`, `containsAny`, `call`, …) and the condition AST shape are covered in [`aml-resolution-rules-schema.md`](aml-resolution-rules-schema.md) and the `SKILL.md` operator table.
