#!/usr/bin/env python3
"""Build (and validate) a matrix-parameter path for GET /resources/kyt/txns/query/-.

Usage:
  build_query.py < spec.json          # prints the path, ready for find_transactions.sh

Spec:
  {
    "criteria": {
      "data.type": "travelRule",
      "data.info.paymentTxnId": "0xabc...",
      "data.info.amount__gte": 100,
      "data.txnDate__lte": "2026-05-21 23:59:59"
    },
    "order": "-createdAt",
    "limit": 10
  }

Hard rules (criteria non-empty, limit <= 100, no empty values) are enforced
here because they are cheap to check and stable. The field allowlist is NOT
enforced: the server owns it and has been expanding it, so unrecognised fields
are passed through with a warning and the server gets the final say.
"""
import json
import sys
from urllib.parse import quote

# Fields known to work. Advisory only — the server owns the real allowlist and
# it has been growing, so an unknown field here is a warning, not an error.
KNOWN_FIELDS = {
    "clientId",
    "data.applicant.paymentMethod.accountId",
    "data.counterparty.paymentMethod.accountId",
    "data.info.amount",
    "data.info.cryptoParams.cryptoChain",
    "data.info.currencyCode",
    "data.info.direction",
    "data.info.paymentTxnId",
    "data.txnDate",
    "data.type",
    "data.sourceKey",
}

OPERATOR_SUFFIXES = ("__gte", "__lte", "__ne")
MAX_LIMIT = 100
BASE_PATH = "/resources/kyt/txns/query/-"


def fail(msg):
    print("error: %s" % msg, file=sys.stderr)
    sys.exit(2)


def base_field(key):
    for suffix in OPERATOR_SUFFIXES:
        if key.endswith(suffix):
            return key[: -len(suffix)]
    return key


def main():
    try:
        spec = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        fail("spec is not valid JSON: %s" % e)

    criteria = spec.get("criteria") or {}
    if not isinstance(criteria, dict) or not criteria:
        fail("'criteria' must be a non-empty object — the server rejects unfiltered queries")

    unknown = [k for k in criteria if base_field(k) not in KNOWN_FIELDS]
    if unknown:
        print(
            "note: %s not in the known-good field list — the server decides. If it "
            "refuses, the error names the field; relay it rather than substituting "
            "another one." % ", ".join(unknown),
            file=sys.stderr,
        )

    limit = spec.get("limit", 100)
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        fail("'limit' must be an integer")
    if limit < 1:
        fail("'limit' must be at least 1")
    if limit > MAX_LIMIT:
        fail("'limit' must be <= %d (server limit)" % MAX_LIMIT)

    segments = []
    for key, value in criteria.items():
        if value is None or value == "":
            fail("criterion '%s' has an empty value" % key)
        # safe='' so spaces and colons in dates are encoded, as the server expects
        segments.append("%s=%s" % (key, quote(str(value), safe="")))

    path = BASE_PATH + ";" + ";".join(segments)

    params = ["limit=%d" % limit]
    order = spec.get("order")
    if order:
        params.insert(0, "order=%s" % quote(str(order), safe="-."))
    path += "?" + "&".join(params)

    print(path)
    print("built query with %d criteria, limit %d" % (len(criteria), limit), file=sys.stderr)


if __name__ == "__main__":
    main()
