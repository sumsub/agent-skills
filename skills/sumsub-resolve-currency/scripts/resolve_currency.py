#!/usr/bin/env python3
"""Resolve a currency against a Sumsub catalogue, mirroring the server's own rules.

Usage:
  get_currencies.sh crypto > crypto.json
  resolve_currency.py --catalogue crypto.json --code USDT --chain TRON
  resolve_currency.py --catalogue fiat.json --type fiat --code eur

  # or a batch: {"queries":[{"code":"USDT","chain":"TRX"}, ...]} on stdin
  resolve_currency.py --catalogue crypto.json < queries.json

Exit codes: 0 resolved, 1 not found, 3 ambiguous, 2 usage/input error.

The point of this script is that it refuses to guess. The server returns *no
currency* when a lookup matches several rows, so a resolver that silently picks
the first hit would disagree with production.
"""
import argparse
import json
import sys

# Mirrors KytCurrencyModel.ALIASES_TO_CRYPTO_CHAINS. Applied after upper+trim.
CHAIN_ALIASES = {
    "ETHEREUM": "ETH",
    "BITCOIN": "BTC",
    "MATIC": "POL",
    "POLYGON": "POL",
    "POL_POLYGON": "POL",
    "BSC": "BNB",
    "BEP20": "BNB",
    "TRON": "TRX",
    "TRC20": "TRX",
    "SOLANA": "SOL",
    "STELLAR": "XLM",
    "AVAXC": "AVAX",
    "CAVAX": "AVAX",
    "AVAX_C": "AVAX",
    "ARBI": "ARB",
    "ARBITRUM": "ARB",
    "ARBEVM": "ARB",
    "OPTIMISM": "OP",
    "APTOS": "APT",
    "MANTLE": "MNT",
    "PULSE": "PLS",
    "PLASMA": "XPL",
    "VECHAIN": "VET",
    "HYPEEVM": "HYPE",
    "HYPEREVM": "HYPE",
    "SEIEVM": "SEI",
    "MONAD": "MON",
    "SONIC": "S",
    "ETH_BASE": "BASE",
}

NATIVE = ""  # empty cryptoChain means "the native coin of its own chain"


def norm(s):
    return s.strip().upper() if isinstance(s, str) else ""


def normalize_chain(raw):
    v = norm(raw)
    return CHAIN_ALIASES.get(v, v)


def load_catalogue(path):
    with open(path) as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        data = data.get("list", {}).get("items", data.get("items", []))
    if not isinstance(data, list):
        raise SystemExit("error: catalogue must be a JSON array (or {list:{items:[]}})")
    return data


def resolve_fiat(catalogue, code):
    code_n = norm(code)
    hits = [c for c in catalogue if norm(c.get("currencyCode")) == code_n]
    if not hits:
        return {"status": "not_found", "reason": "no fiat currency with that code"}
    return {
        "status": "resolved",
        "send": {"currencyCode": hits[0].get("currencyCode"), "currencyType": "fiat"},
        "entry": hits[0],
    }


def resolve_crypto(catalogue, code, chain, contract):
    code_n = norm(code)
    by_code = [c for c in catalogue if norm(c.get("currencyCode")) == code_n]
    if not by_code:
        return {"status": "not_found", "reason": "no asset with that symbol"}

    chain_n = normalize_chain(chain)
    # The server treats code == chain as the native coin (the BTC/BTC mistake).
    if chain_n == code_n:
        chain_n = NATIVE

    contract_n = norm(contract)

    def chain_of(entry):
        return normalize_chain(entry.get("cryptoChain") or "")

    if chain is None:
        candidates = by_code
    else:
        candidates = [c for c in by_code if chain_of(c) == chain_n]
        if not candidates:
            return {
                "status": "not_found",
                "reason": "symbol exists but not on that chain",
                "chain_normalised_to": chain_n or "(native)",
                "available_chains": sorted(
                    {(c.get("cryptoChain") or "(native)") for c in by_code}
                ),
            }

    if contract_n:
        exact = [c for c in candidates if norm(c.get("contractAddress")) == contract_n]
        if exact:
            candidates = exact
        else:
            # Mirrors the server: it falls back to (code, chain) and keeps going,
            # logging that the contract is probably wrong. Surface that, loudly.
            return {
                "status": "resolved" if len(candidates) == 1 else "ambiguous",
                "warning": (
                    "contractAddress did not match any entry; the server would fall "
                    "back to (code, chain) and accept the match silently. Verify it."
                ),
                "send": _send(candidates[0]) if len(candidates) == 1 else None,
                "entry": candidates[0] if len(candidates) == 1 else None,
                "candidates": _summarise(candidates) if len(candidates) > 1 else None,
            }

    if len(candidates) > 1:
        return {
            "status": "ambiguous",
            "reason": (
                "%d assets share this symbol; the server returns NO currency for an "
                "ambiguous lookup. Pin it with cryptoChain (and contractAddress if "
                "the symbol repeats on one chain)." % len(candidates)
            ),
            "candidates": _summarise(candidates),
        }

    return {"status": "resolved", "send": _send(candidates[0]), "entry": candidates[0]}


def _send(entry):
    out = {"currencyCode": entry.get("currencyCode"), "currencyType": "crypto"}
    chain = entry.get("cryptoChain") or ""
    out["cryptoParams"] = {"cryptoChain": chain} if chain else {}
    if not chain:
        out["_note"] = "native coin — send cryptoChain empty or omit cryptoParams"
    return out


def _summarise(entries):
    return [
        {
            "currencyCode": e.get("currencyCode"),
            "cryptoChain": e.get("cryptoChain") or "(native)",
            "contractAddress": e.get("contractAddress"),
            "chainId": e.get("chainId"),
            "name": e.get("name"),
        }
        for e in entries[:25]
    ]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalogue", required=True, help="JSON from get_currencies.sh")
    ap.add_argument("--type", choices=("crypto", "fiat"), default="crypto")
    ap.add_argument("--code")
    ap.add_argument("--chain", default=None, help="omit entirely to search all chains")
    ap.add_argument("--contract", default=None)
    args = ap.parse_args()

    catalogue = load_catalogue(args.catalogue)

    if args.code:
        queries = [{"code": args.code, "chain": args.chain, "contract": args.contract}]
    else:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            raise SystemExit("error: no --code given and stdin is not valid JSON: %s" % e)
        queries = payload.get("queries") if isinstance(payload, dict) else payload
        if not isinstance(queries, list) or not queries:
            raise SystemExit("error: expected {'queries': [...]} or a non-empty array")

    results = []
    for q in queries:
        if args.type == "fiat":
            r = resolve_fiat(catalogue, q.get("code"))
        else:
            r = resolve_crypto(catalogue, q.get("code"), q.get("chain"), q.get("contract"))
        r["query"] = q
        results.append(r)

    json.dump(results if len(results) > 1 else results[0], sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")

    statuses = {r["status"] for r in results}
    if "ambiguous" in statuses:
        return 3
    if "not_found" in statuses:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
