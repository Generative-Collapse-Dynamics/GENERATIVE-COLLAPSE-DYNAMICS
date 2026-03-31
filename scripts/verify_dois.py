#!/usr/bin/env python3
"""Verify DOIs in Bibliography.bib - write results to JSON."""

from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.request

BIB = "paper/Bibliography.bib"
OUT = "/tmp/doi_results.json"

with open(BIB) as f:
    content = f.read()

# Parse entries
bib_entries = re.split(r"(?=@\w+\{)", content)
dois = []
for entry in bib_entries:
    if not entry.strip():
        continue
    key_m = re.match(r"@\w+\{(\w+),", entry)
    doi_m = re.search(r"doi\s*=\s*\{([^}]+)\}", entry)
    if key_m and doi_m:
        key = key_m.group(1)
        doi = doi_m.group(1).strip()
        if not doi.startswith("10.5281/zenodo"):
            dois.append((key, doi))

print(f"Found {len(dois)} external DOIs to verify", flush=True)
ctx = ssl.create_default_context()
results = []

for i, (key, doi) in enumerate(dois):
    url = f"https://doi.org/{doi}"
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "DOI-Checker/1.0 (bibliography audit)")
        req.add_header("Accept", "text/html")
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        code = resp.getcode()
        final = resp.geturl()
        results.append({"key": key, "doi": doi, "status": "OK", "code": code, "url": final[:120]})
    except urllib.error.HTTPError as e:
        results.append({"key": key, "doi": doi, "status": f"HTTP-{e.code}", "code": e.code, "url": ""})
    except Exception as e:
        results.append({"key": key, "doi": doi, "status": "ERR", "code": 0, "url": str(e)[:80]})

    if (i + 1) % 20 == 0:
        print(f"  {i + 1}/{len(dois)} done", flush=True)
        # Save intermediate
        with open(OUT, "w") as f:
            json.dump(results, f, indent=1)
        time.sleep(1.5)
    else:
        time.sleep(0.25)

with open(OUT, "w") as f:
    json.dump(results, f, indent=1)

ok = sum(1 for r in results if r["status"] == "OK")
fail = len(results) - ok
print(f"\nDone: {ok} OK, {fail} non-OK out of {len(results)}")
print(f"Results saved to {OUT}")
