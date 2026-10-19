"""Small read-only adapters for local JSON, CSV and SQLite evidence.

No connector is represented as a live Zetaris integration. The SQL seed is a
synthetic CSV and carries its provenance through the SQLite adapter.
"""

from __future__ import annotations

import csv
import copy
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class JsonAdapter:
    kind = "JSON"

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)

    def read(self, filename: str) -> Any:
        if filename not in {"recall.json", "inventory.json"}:
            raise ValueError("Only declared fixture sources can be read")
        with (self.data_dir / filename).open(encoding="utf-8") as stream:
            return json.load(stream)


class CsvAdapter:
    kind = "CSV"

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)

    def read(self, filename: str) -> list[dict[str, str]]:
        if filename not in {"supplier_aliases.csv", "transfers.csv", "intake_ledger.csv"}:
            raise ValueError("Only declared fixture sources can be read")
        with (self.data_dir / filename).open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))


def _initialize_ledger(connection: sqlite3.Connection, rows: Iterable[dict]) -> None:
    connection.execute("""CREATE TABLE intake_ledger (
        record_id TEXT, intake_batch TEXT, supplier_id TEXT, sku TEXT,
        gtin TEXT, lot TEXT, units INTEGER, received_at TEXT, document_id TEXT
    )""")
    columns = ("record_id", "intake_batch", "supplier_id", "sku", "gtin", "lot",
               "units", "received_at", "document_id")
    connection.executemany(
        "INSERT INTO intake_ledger VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [tuple(row.get(column) for column in columns) for row in rows],
    )
    connection.commit()


def create_demo_database(path: str | Path) -> Path:
    """Write a new standalone fixture database; never overwrite an existing file."""
    target = Path(path)
    if target.exists():
        raise FileExistsError(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    try:
        _initialize_ledger(connection, CsvAdapter().read("intake_ledger.csv"))
    finally:
        connection.close()
    return target


class SqliteLedgerAdapter:
    kind = "SQLite"

    def __init__(self, rows: list[dict] | None = None, data_dir: Path = DATA_DIR):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        _initialize_ledger(
            self.connection,
            CsvAdapter(data_dir).read("intake_ledger.csv") if rows is None else rows,
        )
        self.connection.execute("PRAGMA query_only = ON")
        self.query_count = 0

    def by_intake_batch(self, intake_batch: str) -> list[dict]:
        self.query_count += 1
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM intake_ledger WHERE intake_batch = ? ORDER BY record_id",
            (intake_batch,),
        )]

    def close(self) -> None:
        self.connection.close()


class EvidenceFederation:
    """Joins exact keys across adapters; free text cannot select code or tools."""

    def __init__(self, ledger_rows: list[dict] | None = None, data_dir: Path = DATA_DIR,
                 alias_rows: list[dict] | None = None, transfer_rows: list[dict] | None = None,
                 source_names: dict | None = None):
        self.json = JsonAdapter(data_dir)
        self.csv = CsvAdapter(data_dir)
        self.sql = SqliteLedgerAdapter(ledger_rows, data_dir)
        self.alias_rows = copy.deepcopy(alias_rows)
        self.transfer_rows = copy.deepcopy(transfer_rows)
        self.sources = {"recall": "recall.json", "inventory": "inventory.json",
                        "aliases": "supplier_aliases.csv", "ledger": "sqlite:intake_ledger",
                        "transfers": "transfers.csv"}
        if source_names:
            self.sources.update(source_names)

    def supplier(self, alias: str | None) -> list[dict]:
        key = (alias or "").strip().casefold()
        rows = self.csv.read("supplier_aliases.csv") if self.alias_rows is None else self.alias_rows
        return [row for row in rows
                if row["alias"].strip().casefold() == key]

    def receipts(self, intake_batch: str | None) -> list[dict]:
        return self.sql.by_intake_batch(intake_batch) if intake_batch else []

    def transfers(self, item_id: str) -> list[dict]:
        return self.transfer_evidence(item_id)["records"]

    def transfer_evidence(self, item_id: str) -> dict:
        """Deduplicate direct transfer receipts; ambiguous graphs never get totals.

        The supported schema is one outgoing hop from a current inventory item.
        Explicit chained transfers require a future graph adapter and are retained
        as evidence with an unresolved quantity instead of recursively added.
        """
        source = self.csv.read("transfers.csv") if self.transfer_rows is None else self.transfer_rows
        rows = [copy.deepcopy(row) for row in source if row.get("item_id") == item_id]
        records, issues, seen = [], [], {}
        if any(not row.get("item_id") for row in source):
            issues.append("Transfer source contains a record with no inventory item identifier")
        for row in rows:
            transfer_id = row.get("transfer_id")
            if not isinstance(transfer_id, str) or not transfer_id.strip():
                issues.append("Transfer receipt lacks a stable transfer identifier")
            else:
                canonical = json.dumps(row, sort_keys=True, default=str)
                if any(other.get("transfer_id") == transfer_id and other.get("item_id") != item_id for other in source):
                    issues.append("Transfer identifier is reused across different inventory items")
                if transfer_id in seen:
                    if seen[transfer_id] == canonical:
                        continue
                    issues.append("Conflicting transfer records share the same identifier")
                seen[transfer_id] = canonical
            units = row.get("units")
            if isinstance(units, str) and re.fullmatch(r"[0-9]+", units.strip()):
                units = int(units)
            if isinstance(units, bool) or not isinstance(units, int) or units < 0:
                row["original_units"] = row.get("units")
                units = 0
                issues.append("Transfer quantity is not a non-negative integer")
            row["units"] = units
            if not row.get("destination") or not row.get("receipt_id"):
                issues.append("Transfer lacks a destination or receipt identifier")
            if any(row.get(field) for field in (
                    "parent_transfer_id", "upstream_transfer_id", "from_transfer_id", "source_transfer_id")):
                issues.append("Multi-hop transfer graph is unsupported; inspect downstream receipts")
            if row.get("hop", 1) not in (1, "1", None, ""):
                issues.append("Multi-hop transfer graph is unsupported; inspect downstream receipts")
            records.append(row)
        return {"records": records, "issues": list(dict.fromkeys(issues)),
                "outbound_units": None if issues else sum(row["units"] for row in records),
                "scope": "single_outgoing_hop_only"}

    def close(self) -> None:
        self.sql.close()
