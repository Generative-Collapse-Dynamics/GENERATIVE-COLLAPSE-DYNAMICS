# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 2.2.x   | :white_check_mark: |
| 2.1.x   | :white_check_mark: |
| < 2.1   | :x:                |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Please report vulnerabilities through GitHub's private vulnerability reporting:

1. Go to the [Security tab](../../security/advisories) of this repository
2. Click **"Report a vulnerability"**
3. Provide a detailed description including:
   - Steps to reproduce
   - Affected component (kernel, validator, CLI, API, dashboard)
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

| Stage        | Target    |
|--------------|-----------|
| Acknowledge  | 48 hours  |
| Assess       | 1 week    |
| Fix & release| 2 weeks   |

## Security Model

UMCP operates on a trust boundary between **validated data** (contracts,
casepacks, integrity checksums) and **untrusted input** (user-supplied
traces, raw data files, CLI arguments).

### Trusted (Tier-0 Protocol)

- Frozen parameters from `frozen_contract.py`
- SHA-256 checksums in `integrity/sha256.txt`
- JSON Schema Draft 2020-12 validation
- Three-valued verdicts (CONFORMANT / NONCONFORMANT / NON_EVALUABLE)

### Untrusted (validated before use)

- User-supplied trace vectors and weights
- YAML/JSON contract and casepack files
- CLI arguments and API request bodies
- File paths and directory references

## Design Principles

1. **No `eval()` or `exec()`** — all computation uses typed functions
2. **Schema validation first** — all data validated against JSON Schema before processing
3. **SHA-256 integrity** — 187+ tracked files checksummed; CI fails on mismatch
4. **Frozen parameters** — seam-derived constants, not user-configurable at runtime
5. **Append-only ledger** — `ledger/return_log.csv` is never overwritten
6. **No network calls in core** — the kernel, validator, and seam are offline-only

## Attack Surface

| Component    | Risk Level | Mitigation |
|--------------|------------|------------|
| CLI          | Low        | `argparse` with strict type validation |
| API (FastAPI)| Medium     | Pydantic models, CORS defaults, no auth by default |
| Dashboard    | Medium     | Read-only Streamlit, no write operations |
| File I/O     | Low        | Path validation, no symlink following |
| Dependencies | Low        | Dependabot monitoring (pip + GitHub Actions) |

## Contributor Security Checklist

Before submitting code changes:

- [ ] No hardcoded secrets, tokens, or credentials
- [ ] No `eval()`, `exec()`, or `__import__()` on user input
- [ ] File paths validated and sandboxed to workspace
- [ ] All external input validated against schemas
- [ ] Dependencies pinned or version-bounded
- [ ] No new network calls in Tier-0 or Tier-1 code
