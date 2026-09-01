#!/usr/bin/env python3
"""Expand a compact wallet-address spec into the JSON array the import endpoint wants.

Usage:
  build_wallet_import.py < spec.json > payload.json

Spec (JSON on stdin):
  {
    "defaults":  { "asset": "BTC", "chain": "BTC" },
    "addresses": [ { "walletAddress": "bc1q..." }, { "walletAddressHash": "9f2c..." } ]
  }

Emits a JSON array of wallet entries. Validation is deliberately strict: the
import endpoint answers 200 with a per-entry error list, so anything caught
here is an error the caller would otherwise only notice by reading errorCount.
"""
import json
import sys

IMPORT_LIMIT = 10000
PASSTHROUGH = ("walletAddress", "walletAddressHash", "asset", "chain")


def fail(msg):
    print("error: %s" % msg, file=sys.stderr)
    sys.exit(2)


def main():
    try:
        spec = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        fail("spec is not valid JSON: %s" % e)

    if isinstance(spec, list):
        spec = {"addresses": spec}
    if not isinstance(spec, dict):
        fail("spec must be an object or an array of addresses")

    defaults = spec.get("defaults") or {}
    addresses = spec.get("addresses")
    if not isinstance(addresses, list) or not addresses:
        fail("'addresses' must be a non-empty array")
    if len(addresses) > IMPORT_LIMIT:
        fail(
            "%d addresses exceeds the server limit of %d per call — split into chunks"
            % (len(addresses), IMPORT_LIMIT)
        )

    out = []
    for i, raw in enumerate(addresses):
        if not isinstance(raw, dict):
            fail("addresses[%d] must be an object" % i)

        entry = {k: v for k, v in defaults.items() if k in PASSTHROUGH}
        for k, v in raw.items():
            if k.startswith("_"):
                continue
            entry[k] = v

        addr = (entry.get("walletAddress") or "").strip()
        hashed = (entry.get("walletAddressHash") or "").strip()
        if not addr and not hashed:
            fail(
                "addresses[%d]: either 'walletAddress' or 'walletAddressHash' is required"
                % i
            )
        if addr and hashed:
            fail(
                "addresses[%d]: sending both 'walletAddress' and 'walletAddressHash' is "
                "only valid when the hash matches Sumsub's hashing of the address; the "
                "server rejects the entry otherwise. Send just one." % i
            )

        if addr:
            entry["walletAddress"] = addr
            entry.pop("walletAddressHash", None)
        else:
            entry["walletAddressHash"] = hashed
            entry.pop("walletAddress", None)

        entry.pop("source", None)  # server always stamps 'api'
        out.append(entry)

    seen, dupes = set(), 0
    for e in out:
        key = e.get("walletAddress") or e.get("walletAddressHash")
        if key in seen:
            dupes += 1
        seen.add(key)
    if dupes:
        print("note: %d duplicate address(es) in the batch" % dupes, file=sys.stderr)

    json.dump(out, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    print("built %d wallet entries" % len(out), file=sys.stderr)


if __name__ == "__main__":
    main()
