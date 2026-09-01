#!/usr/bin/env python3
"""
Assemble an AML resolution rule spec (JSON on stdin) into a full rule payload for
`POST /resources/api/agent/amlResolutionRules/draft/rules` (JSON on stdout).

This is a thin assembler + validator, NOT a translator. The rule `condition` is
the real Sumsub Condition AST, authored directly — the SAME shape as workflow
edge conditions (`{or:[{and:[{op, args:[{exp},{lit}]}]}]}`), where:
  - `{exp: "<raw path>"}`  is an expression path, verbatim (incl. bracket paths).
  - `{lit: "<json>"}`      is a literal, given **already JSON-encoded as a string**
                           the way the API stores it ("false_positive" ->
                           "\"false_positive\"", 2 -> "2", ["pep"] -> "[\"pep\"]").
                           The API rejects an un-encoded literal, so the encoding
                           is mandatory.

AML conditions may call a built-in function via the `call` op: the first arg is
the function name as `{exp: "namesIncompatible"}`, the rest are its arguments
(exp paths or JSON-encoded lits). This is the one operator workflows don't expose.

What the assembler does (and only this):
- Passes the `condition` AST through verbatim; validates every `op` against the
  known operator set, rejects a top-level `Condition.negate`, caps `lit` length.
- Assembles the review action (`matchStatus`/`riskLevel`/`whitelisted`/`note` as
  Criterion.Args, or the whole-review `expression` form) and the tags action,
  with a scalar convenience (a bare review value becomes a JSON-encoded `{lit}`);
  validates the `matchStatus` enum and the review/tags shape.
- Enforces that a rule has a review and/or tags action (the `emptyAction` guard).
"""
import json
import sys

MATCH_STATUSES = {"unknown", "potential_match", "false_positive", "true_positive"}

# Operator set mirrors the server's condition operator set. Unlike the workflow
# builder, `call` is allowed — AML rules invoke built-in functions
# (namesCompatible / dobsIncompatible / …) through it.
OPERATORS = {
    "eq", "eqIgnoreCase", "neIgnoreCase", "eqOrNull", "eqIgnoreCaseOrNull", "ne",
    "lt", "lte", "gt", "gte", "match", "notMatch", "in", "notIn",
    "startsWith", "notStartsWith", "endsWith", "notEndsWith", "empty", "notEmpty",
    "contains", "notContains", "containsAny", "notContainsAny", "containsAll",
    "containsOnly", "call",
}

# AST limits enforced server-side (Condition / Criterion).
MAX_OR_BRANCHES = 30
MAX_AND_CRITERIA = 30
MAX_ARGS = 10
MAX_EXP_LEN = 512
MAX_LIT_LEN = 8192


# ---------- condition validation (pass-through, not transform) ----------------

def _validate_condition(cond) -> None:
    """Walk a hand-authored Condition AST and validate it without transforming it:
      - reject any `op` not in the known operator set (catches typos),
      - reject a top-level `Condition.negate` — negate via the not* operators
        (notContains, notIn, notEmpty, ne, …) instead, as the UI does,
      - enforce the server-side size limits (branches / criteria / args / lengths).
    `lit` values are passed through verbatim (the author supplies them already
    JSON-encoded, the way the API stores them)."""
    if not isinstance(cond, dict):
        raise ValueError("condition must be the Condition AST object {or:[{and:[...]}]}")
    if cond.get("negate"):
        raise ValueError("top-level condition.negate is not supported; use a not* operator instead")
    branches = cond.get("or")
    if not isinstance(branches, list) or not branches:
        raise ValueError("condition must have a non-empty 'or' list of AND-branches")
    if len(branches) > MAX_OR_BRANCHES:
        raise ValueError(f"condition has {len(branches)} OR branches; max {MAX_OR_BRANCHES}")
    for branch in branches:
        if not isinstance(branch, dict):
            raise ValueError(f"each 'or' entry must be an object with an 'and' list; got {branch!r}")
        criteria = branch.get("and")
        if not isinstance(criteria, list) or not criteria:
            raise ValueError("each OR branch must have a non-empty 'and' list of criteria")
        if len(criteria) > MAX_AND_CRITERIA:
            raise ValueError(f"an OR branch has {len(criteria)} criteria; max {MAX_AND_CRITERIA}")
        for crit in criteria:
            if not isinstance(crit, dict):
                raise ValueError(f"each criterion must be an object {{op, args}}; got {crit!r}")
            op = crit.get("op")
            if op not in OPERATORS:
                raise ValueError(f"unknown operator {op!r}; allowed: {sorted(OPERATORS)}")
            args = crit.get("args") or []
            if len(args) > MAX_ARGS:
                raise ValueError(f"criterion {op!r} has {len(args)} args; max {MAX_ARGS}")
            for arg in args:
                if not isinstance(arg, dict):
                    raise ValueError(f"each arg must be {{exp: ...}} or {{lit: ...}}; got {arg!r}")
                exp, lit = arg.get("exp"), arg.get("lit")
                if exp is not None and len(str(exp)) > MAX_EXP_LEN:
                    raise ValueError(f"exp longer than {MAX_EXP_LEN} chars: {str(exp)[:60]!r}…")
                if lit is not None and isinstance(lit, str) and len(lit) > MAX_LIT_LEN:
                    raise ValueError(f"lit longer than {MAX_LIT_LEN} chars")


# ---------- review / tags assembly --------------------------------------------

def _to_arg(value, field: str) -> dict:
    """Review-field value → Criterion.Arg. A scalar becomes a JSON-encoded `{lit}`
    (the convenience layer); an explicit `{exp:...}`/`{lit:...}` passes through."""
    if isinstance(value, dict):
        if set(value) == {"exp"} or set(value) == {"lit"}:
            return value
        raise ValueError(f"review.{field} object must be exactly {{\"exp\": ...}} or {{\"lit\": ...}}; got {value!r}")
    if isinstance(value, bool):
        return {"lit": "true" if value else "false"}
    if isinstance(value, (int, float)):
        return {"lit": json.dumps(value)}
    if isinstance(value, str):
        return {"lit": json.dumps(value)}
    raise ValueError(f"review.{field} must be a string, bool, number, or {{exp|lit}} object; got {value!r}")


def _build_review(review: dict) -> dict:
    field_keys = {"matchStatus", "riskLevel", "whitelisted", "note"}
    unknown = set(review) - field_keys - {"expression"}
    if unknown:
        raise ValueError(f"unknown review keys: {sorted(unknown)}; allowed: expression, {sorted(field_keys)}")

    if review.get("expression") is not None:
        if any(review.get(k) is not None for k in field_keys):
            raise ValueError(
                "review.expression is the whole-review form (e.g. 'match.previousReview') and replaces "
                "matchStatus/riskLevel/whitelisted/note entirely — set either expression OR the per-field keys, not both")
        return {"expression": str(review["expression"])}

    out = {}
    for key in ("matchStatus", "riskLevel", "whitelisted", "note"):
        if review.get(key) is None:
            continue
        arg = _to_arg(review[key], key)
        if key == "matchStatus" and "lit" in arg:
            literal = json.loads(arg["lit"]) if arg["lit"].startswith('"') else arg["lit"]
            if literal not in MATCH_STATUSES:
                raise ValueError(
                    f"review.matchStatus {literal!r} is not a valid match status; "
                    f"allowed: {sorted(MATCH_STATUSES)}")
        if key == "whitelisted" and "lit" in arg and arg["lit"] not in ("true", "false"):
            raise ValueError(f"review.whitelisted must be a boolean; got {review[key]!r}")
        out[key] = arg
    if not out:
        raise ValueError("review must set expression or at least one of matchStatus/riskLevel/whitelisted/note")
    return out


# ---------- top-level ----------------------------------------------------------

def build_rule(spec: dict) -> dict:
    name = spec.get("name")
    if not name:
        raise ValueError("rule spec must have 'name' (the human-readable rule name)")
    if len(name) > 1000:
        raise ValueError("'name' is longer than 1000 chars")

    rule = {"name": name}

    if spec.get("id") is not None:
        rule["id"] = spec["id"]

    description = spec.get("description")
    if description is not None:
        if len(description) > 3000:
            raise ValueError("'description' is longer than 3000 chars")
        rule["description"] = description

    # Guard the removed authoring shapes so old specs fail loudly, not silently.
    if "conditionRaw" in spec:
        raise ValueError(
            "'conditionRaw' is no longer a separate key — write the Condition AST directly "
            "under 'condition' (the expression mini-language was removed). See SKILL.md.")
    cond = spec.get("condition")
    if cond is None:
        raise ValueError("rule spec must have 'condition' (the Condition AST {or:[{and:[...]}]})")
    if isinstance(cond, str):
        raise ValueError(
            "'condition' must be the Condition AST object, not a string — the expression "
            "mini-language ('screening.vendor = …', 'fn(...)') was removed. Write the AST "
            "directly, e.g. {\"or\":[{\"and\":[{\"op\":\"eq\",\"args\":[{\"exp\":\"screening.vendor\"},"
            "{\"lit\":\"\\\"complyAdvantageCSOM\\\"\"}]}]}]}. See SKILL.md.")
    _validate_condition(cond)
    rule["condition"] = cond

    review = spec.get("review")
    if review is not None:
        if not isinstance(review, dict):
            raise ValueError("'review' must be an object")
        rule["review"] = _build_review(review)

    tags = spec.get("tags")
    if tags is not None:
        tags = tags if isinstance(tags, list) else [tags]
        if not tags:
            raise ValueError("'tags' must be a non-empty list when present")
        if len(tags) > 100:
            raise ValueError(f"'tags' has {len(tags)} entries; max 100")
        rule["tags"] = {"tags": [str(t) for t in tags]}

    if review is None and tags is None:
        raise ValueError(
            "rule must have a 'review' action and/or 'tags' — a rule with neither fails "
            "validation with an emptyAction notice")

    # Pass-through unknown keys (escape hatch for future fields).
    handled = {"id", "name", "description", "condition", "review", "tags"}
    for k, v in spec.items():
        if k in handled or v is None:
            continue
        rule[k] = v

    return rule


def main():
    try:
        spec = json.load(sys.stdin)
    except ValueError as e:
        print(f"error: invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(2)
    try:
        payload = build_rule(spec)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
