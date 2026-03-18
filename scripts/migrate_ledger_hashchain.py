#!/usr/bin/env python3
"""
Migrate ledger to include hash-chain column.

Adds a `chain_hash` column to ledger/return_log.csv where each row's hash
depends on the previous row's hash + its own data. This makes the ledger
tamper-evident: modifying any row breaks all subsequent hashes.

The chain uses SHA-256(prev_hash | row_data)[:16].
Genesis hash: SHA-256("GENESIS")[:16].

Usage:
    python scripts/migrate_ledger_hashchain.py
    python scripts/migrate_ledger_hashchain.py --verify  # verify after migration
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

GENESIS_HASH = hashlib.sha256(b"GENESIS").hexdigest()[:16]

DATA_FIELDS = [
    "timestamp",
    "run_status",
    "F",
    "omega",
    "kappa",
    "IC",
    "C",
    "S",
    "tau_R",
    "delta_kappa",
]

NEW_FIELDNAMES = [*DATA_FIELDS, "chain_hash"]


def row_canonical(row: dict[str, str]) -> str:
    """Canonical string for a ledger row (all data fields, pipe-separated)."""
    return "|".join(row.get(f, "") for f in DATA_FIELDS)


def compute_chain_hash(prev_hash: str, row: dict[str, str]) -> str:
    """SHA-256(prev_hash | canonical_row) truncated to 16 hex chars."""
    payload = f"{prev_hash}|{row_canonical(row)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def migrate(ledger_path: Path) -> int:
    """Add chain_hash column to existing ledger. Returns row count."""
    backup_path = ledger_path.parent / f"return_log.pre_hashchain.{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # Read existing data
    rows: list[dict[str, str]] = []
    with open(ledger_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        old_fields = reader.fieldnames or []
        for row in reader:
            rows.append(dict(row))

    print(f"Read {len(rows)} rows with columns: {old_fields}")

    if "chain_hash" in old_fields:
        print("Ledger already has chain_hash column. Checking integrity...")
        prev_hash = GENESIS_HASH
        broken = 0
        for i, row in enumerate(rows, 1):
            expected = compute_chain_hash(prev_hash, row)
            actual = row.get("chain_hash", "")
            if actual != expected:
                if broken == 0:
                    print(f"  Chain broken at row {i}: expected {expected}, got {actual}")
                broken += 1
            prev_hash = actual if actual else expected
        if broken:
            print(f"  {broken} broken links found. Re-run without --verify to rebuild.")
        else:
            print(f"  Chain intact: {len(rows)} rows verified.")
        return len(rows)

    # Backup
    shutil.copy(ledger_path, backup_path)
    print(f"Backed up to: {backup_path}")

    # Compute hash chain
    prev_hash = GENESIS_HASH
    for row in rows:
        chain_hash = compute_chain_hash(prev_hash, row)
        row["chain_hash"] = chain_hash
        prev_hash = chain_hash

    # Write migrated ledger
    with open(ledger_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=NEW_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            # Ensure only the expected fields are written
            clean_row = {k: row.get(k, "") for k in NEW_FIELDNAMES}
            writer.writerow(clean_row)

    print(f"Migrated {len(rows)} rows with hash chain.")
    print(f"  Genesis hash: {GENESIS_HASH}")
    print(f"  Final hash:   {prev_hash}")
    return len(rows)


def verify(ledger_path: Path) -> bool:
    """Verify the hash chain. Returns True if intact."""
    with open(ledger_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        if "chain_hash" not in fields:
            print("No chain_hash column — run migration first.")
            return False

        prev_hash = GENESIS_HASH
        count = 0
        for row in reader:
            count += 1
            expected = compute_chain_hash(prev_hash, row)
            actual = row.get("chain_hash", "")
            if actual != expected:
                print(f"BROKEN at row {count}: expected {expected}, got {actual}")
                return False
            prev_hash = actual

    print(f"Chain INTACT: {count} rows verified.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate ledger to include hash chain")
    parser.add_argument("--verify", action="store_true", help="Only verify, don't migrate")
    parser.add_argument(
        "--ledger",
        default=None,
        help="Path to ledger CSV (default: ledger/return_log.csv)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    ledger_path = Path(args.ledger) if args.ledger else repo_root / "ledger" / "return_log.csv"

    if not ledger_path.exists():
        print(f"No ledger found at {ledger_path}")
        return

    if args.verify:
        ok = verify(ledger_path)
        raise SystemExit(0 if ok else 1)
    else:
        migrate(ledger_path)
        print("\nVerifying...")
        ok = verify(ledger_path)
        raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
