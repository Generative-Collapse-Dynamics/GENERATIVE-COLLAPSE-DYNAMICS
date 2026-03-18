"""Tests for hash-chain ledger integrity.

Covers:
- Hash chain computation (unit)
- Ledger append with chain_hash (integration)
- Chain verification (tamper detection)
- CLI subcommand: umcp ledger verify / stats
- Migration script
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

from umcp.cli import (
    LEDGER_DATA_FIELDS,
    LEDGER_FIELDNAMES,
    LEDGER_GENESIS_HASH,
    _append_to_ledger,
    _compute_chain_hash,
    _get_last_chain_hash,
    _ledger_row_canonical,
    _verify_ledger_chain,
)

UMCP = [sys.executable, "-m", "umcp"]


class TestHashChainUnit:
    """Unit tests for hash chain primitives."""

    def test_genesis_hash_is_sha256_prefix(self) -> None:
        expected = hashlib.sha256(b"GENESIS").hexdigest()[:16]
        assert expected == LEDGER_GENESIS_HASH
        assert len(LEDGER_GENESIS_HASH) == 16

    def test_row_canonical_deterministic(self) -> None:
        row = {
            "timestamp": "2026-01-01T00:00:00Z",
            "run_status": "CONFORMANT",
            "F": "0.95",
            "omega": "0.05",
            "kappa": "-0.05",
            "IC": "0.95",
            "C": "0.1",
            "S": "0.08",
            "tau_R": "5",
            "delta_kappa": "-1.0",
        }
        canon1 = _ledger_row_canonical(row)
        canon2 = _ledger_row_canonical(row)
        assert canon1 == canon2
        # Pipe separated, includes all data fields
        assert "|" in canon1
        parts = canon1.split("|")
        assert len(parts) == len(LEDGER_DATA_FIELDS)

    def test_row_canonical_excludes_chain_hash(self) -> None:
        row = {
            "timestamp": "2026-01-01T00:00:00Z",
            "run_status": "CONFORMANT",
            "F": "0.95",
            "omega": "0.05",
            "kappa": "-0.05",
            "IC": "0.95",
            "C": "0.1",
            "S": "0.08",
            "tau_R": "",
            "delta_kappa": "",
            "chain_hash": "abc123",
        }
        canon = _ledger_row_canonical(row)
        assert "abc123" not in canon

    def test_compute_chain_hash_deterministic(self) -> None:
        row = {"timestamp": "t", "run_status": "CONFORMANT", "F": "0.9"}
        h1 = _compute_chain_hash("prev", row)
        h2 = _compute_chain_hash("prev", row)
        assert h1 == h2
        assert len(h1) == 16

    def test_compute_chain_hash_changes_with_prev(self) -> None:
        row = {"timestamp": "t", "run_status": "CONFORMANT"}
        h1 = _compute_chain_hash("aaa", row)
        h2 = _compute_chain_hash("bbb", row)
        assert h1 != h2

    def test_compute_chain_hash_changes_with_data(self) -> None:
        row1 = {"timestamp": "t1", "run_status": "CONFORMANT"}
        row2 = {"timestamp": "t2", "run_status": "CONFORMANT"}
        h1 = _compute_chain_hash("same", row1)
        h2 = _compute_chain_hash("same", row2)
        assert h1 != h2

    def test_fieldnames_has_chain_hash(self) -> None:
        assert "chain_hash" in LEDGER_FIELDNAMES
        assert LEDGER_FIELDNAMES[-1] == "chain_hash"

    def test_data_fields_excludes_chain_hash(self) -> None:
        assert "chain_hash" not in LEDGER_DATA_FIELDS


class TestGetLastChainHash:
    """Tests for reading the last chain hash from ledger."""

    def test_missing_file_returns_genesis(self, tmp_path: Path) -> None:
        assert _get_last_chain_hash(tmp_path / "nonexistent.csv") == LEDGER_GENESIS_HASH

    def test_empty_file_returns_genesis(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.csv"
        f.write_text("")
        assert _get_last_chain_hash(f) == LEDGER_GENESIS_HASH

    def test_header_only_returns_genesis(self, tmp_path: Path) -> None:
        f = tmp_path / "header.csv"
        f.write_text(",".join(LEDGER_FIELDNAMES) + "\n")
        assert _get_last_chain_hash(f) == LEDGER_GENESIS_HASH

    def test_no_chain_hash_column_returns_genesis(self, tmp_path: Path) -> None:
        f = tmp_path / "old.csv"
        f.write_text("timestamp,run_status,F\n2026-01-01,CONFORMANT,0.9\n")
        assert _get_last_chain_hash(f) == LEDGER_GENESIS_HASH

    def test_reads_last_row_hash(self, tmp_path: Path) -> None:
        f = tmp_path / "ledger.csv"
        rows = [
            dict.fromkeys(LEDGER_FIELDNAMES, ""),
            dict.fromkeys(LEDGER_FIELDNAMES, ""),
        ]
        rows[0]["chain_hash"] = "aaa1112233445566"
        rows[1]["chain_hash"] = "bbb9988776655443"
        with open(f, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=LEDGER_FIELDNAMES)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        assert _get_last_chain_hash(f) == "bbb9988776655443"


class TestAppendToLedger:
    """Integration tests for _append_to_ledger with hash chain."""

    def test_new_ledger_has_chain_hash_header(self, tmp_path: Path) -> None:
        _append_to_ledger(tmp_path, "CONFORMANT")
        ledger = tmp_path / "ledger" / "return_log.csv"
        assert ledger.exists()
        with open(ledger) as f:
            header = f.readline().strip()
        assert "chain_hash" in header

    def test_first_row_chains_from_genesis(self, tmp_path: Path) -> None:
        _append_to_ledger(tmp_path, "CONFORMANT")
        ledger = tmp_path / "ledger" / "return_log.csv"
        with open(ledger) as f:
            reader = csv.DictReader(f)
            row = next(reader)
        # Verify the chain hash was computed from GENESIS
        expected = _compute_chain_hash(LEDGER_GENESIS_HASH, row)
        assert row["chain_hash"] == expected

    def test_two_rows_chain_correctly(self, tmp_path: Path) -> None:
        _append_to_ledger(tmp_path, "CONFORMANT", {"F": "0.95", "omega": "0.05"})
        _append_to_ledger(tmp_path, "CONFORMANT", {"F": "0.90", "omega": "0.10"})
        ledger = tmp_path / "ledger" / "return_log.csv"
        with open(ledger) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        # Row 1 chains from genesis
        assert rows[0]["chain_hash"] == _compute_chain_hash(LEDGER_GENESIS_HASH, rows[0])
        # Row 2 chains from row 1's hash
        assert rows[1]["chain_hash"] == _compute_chain_hash(rows[0]["chain_hash"], rows[1])

    def test_chain_is_tamper_evident(self, tmp_path: Path) -> None:
        """If we modify row 1's data, row 2's hash should no longer verify."""
        _append_to_ledger(tmp_path, "CONFORMANT", {"F": "0.95"})
        _append_to_ledger(tmp_path, "CONFORMANT", {"F": "0.90"})
        ledger = tmp_path / "ledger" / "return_log.csv"

        # Tamper: change F in row 1
        with open(ledger) as f:
            lines = f.readlines()
        # lines[1] is row 1 data — change a value
        lines[1] = lines[1].replace("0.95", "0.99")
        with open(ledger, "w") as f:
            f.writelines(lines)

        # Verify should fail
        valid, _, _ = _verify_ledger_chain(ledger)
        assert not valid


class TestVerifyLedgerChain:
    """Tests for chain verification logic."""

    def test_empty_ledger_is_valid(self, tmp_path: Path) -> None:
        valid, count, _msg = _verify_ledger_chain(tmp_path / "nonexistent.csv")
        assert valid
        assert count == 0

    def test_valid_chain_passes(self, tmp_path: Path) -> None:
        _append_to_ledger(tmp_path, "CONFORMANT", {"F": "0.95"})
        _append_to_ledger(tmp_path, "CONFORMANT", {"F": "0.90"})
        _append_to_ledger(tmp_path, "CONFORMANT", {"F": "0.85"})
        ledger = tmp_path / "ledger" / "return_log.csv"
        valid, count, msg = _verify_ledger_chain(ledger)
        assert valid
        assert count == 3
        assert "intact" in msg.lower()

    def test_tampered_chain_detected(self, tmp_path: Path) -> None:
        for f_val in ["0.95", "0.90", "0.85", "0.80"]:
            _append_to_ledger(tmp_path, "CONFORMANT", {"F": f_val})
        ledger = tmp_path / "ledger" / "return_log.csv"

        # Tamper: overwrite chain_hash of row 2
        with open(ledger) as f:
            lines = f.readlines()
        # Corrupt the chain_hash in line 3 (row 2, 0-indexed)
        parts = lines[2].strip().split(",")
        parts[-1] = "0000000000000000"
        lines[2] = ",".join(parts) + "\n"
        with open(ledger, "w") as f:
            f.writelines(lines)

        valid, row_num, msg = _verify_ledger_chain(ledger)
        assert not valid
        assert row_num == 2
        assert "broken" in msg.lower()

    def test_no_chain_hash_column_reports_migration_needed(self, tmp_path: Path) -> None:
        ledger = tmp_path / "old.csv"
        ledger.write_text("timestamp,run_status,F\n2026-01-01,CONFORMANT,0.9\n")
        valid, count, msg = _verify_ledger_chain(ledger)
        assert valid
        assert count == 0
        assert "migration" in msg.lower()


class TestCLILedger:
    """CLI integration tests for umcp ledger subcommand."""

    def test_ledger_help(self) -> None:
        r = subprocess.run([*UMCP, "ledger", "--help"], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0
        assert "ledger" in r.stdout.lower()

    def test_ledger_verify(self) -> None:
        r = subprocess.run([*UMCP, "ledger", "verify"], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0
        assert "CONFORMANT" in r.stdout

    def test_ledger_stats(self) -> None:
        r = subprocess.run([*UMCP, "ledger", "stats"], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0
        assert "Rows:" in r.stdout
        assert "chain_hash" in r.stdout.lower() or "Hash chain:" in r.stdout

    def test_ledger_verify_verbose(self) -> None:
        r = subprocess.run([*UMCP, "ledger", "verify", "-v"], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0


class TestMigrationScript:
    """Tests for the migration script."""

    def test_migration_script_verify_flag(self) -> None:
        r = subprocess.run(
            [sys.executable, "scripts/migrate_ledger_hashchain.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0
        assert "INTACT" in r.stdout

    def test_migration_script_already_migrated(self) -> None:
        """Running migration on already-migrated ledger should detect it."""
        r = subprocess.run(
            [sys.executable, "scripts/migrate_ledger_hashchain.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0
        assert "already has chain_hash" in r.stdout.lower() or "INTACT" in r.stdout
