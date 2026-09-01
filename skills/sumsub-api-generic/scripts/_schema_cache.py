"""Local cache for the Sumsub OpenAPI schema.

The schema is publicly served (no authentication required) at:

    https://api.sumsub.com/agents-openapi.json

We fetch it on first use, cache locally for 24 h, and refresh transparently
on the next call once the cache goes stale. On a refresh that fails (network
down, server 5xx) we fall back to the stale cache with a stderr warning.

Environment:
  SUMSUB_OPENAPI            optional — absolute path to a local schema file
                            (bypasses cache + fetch entirely)
  SUMSUB_OPENAPI_URL        optional — override the source URL
  SUMSUB_SCHEMA_REFRESH=1   optional — force re-fetch even if cache is fresh
  XDG_CACHE_HOME            optional — override base cache dir
                            (default: ~/.cache)
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_SCHEMA_URL = "https://api.sumsub.com/agents-openapi.json"
CACHE_TTL_SECONDS = 24 * 60 * 60  # 1 day


def schema_url() -> str:
    return os.environ.get("SUMSUB_OPENAPI_URL") or DEFAULT_SCHEMA_URL


def cache_path() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "sumsub" / "openapi.json"


def _is_fresh(path: Path) -> bool:
    if not path.is_file():
        return False
    return (time.time() - path.stat().st_mtime) < CACHE_TTL_SECONDS


def _fetch_or_none() -> bytes | None:
    url = schema_url()
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"warning: schema fetch from {url} failed: {exc}", file=sys.stderr)
        return None


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".tmp.{os.getpid()}")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def load_schema() -> dict:
    """Return the parsed schema, fetching/caching as needed.

    Resolution order:
    1. $SUMSUB_OPENAPI override (skip cache + fetch).
    2. Local cache, if fresh (≤ 1 day) and SUMSUB_SCHEMA_REFRESH not set.
    3. Fetch from the schema URL, atomic-write to cache, return.
    4. On network failure with stale cache: fall back to stale + stderr warning.
    """
    override = os.environ.get("SUMSUB_OPENAPI")
    if override:
        p = Path(override)
        if not p.is_file():
            sys.exit(f"error: SUMSUB_OPENAPI={override} not a file")
        return json.loads(p.read_text())

    cache = cache_path()
    force = os.environ.get("SUMSUB_SCHEMA_REFRESH") == "1"

    if not force and _is_fresh(cache):
        return json.loads(cache.read_text())

    data = _fetch_or_none()
    if data is None:
        if cache.is_file():
            print(f"warning: using stale schema cache at {cache}", file=sys.stderr)
            return json.loads(cache.read_text())
        sys.exit(
            f"error: could not fetch schema from {schema_url()} and no cache exists at {cache}."
        )

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as exc:
        sys.exit(f"error: schema URL returned non-JSON ({exc}); first 200 bytes: {data[:200]!r}")

    if not parsed.get("openapi"):
        sys.exit("error: response did not look like OpenAPI (no 'openapi' field)")

    _atomic_write(cache, data)
    return parsed
