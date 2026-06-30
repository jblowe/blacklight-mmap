from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import csv

# Column order used when reading and writing crosswalk files.
CROSSWALK_HEADER = [
    "schema", "table_name", "column_name",
    "column_label", "ordinal_position", "data_type",
]

@dataclass(frozen=True)
class ColumnMeta:
    name: str
    label: str
    data_type: str

def _sniff_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8", errors="ignore")[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
        return dialect.delimiter
    except Exception:
        # default to tab since many "psql/pg_dump" exports use it
        return "\t"

def load_crosswalk(path: str) -> Dict[str, List[ColumnMeta]]:
    """Load a crosswalk file.
    Only the first 6 columns are used:
    schema, table_name, column_name, column_label, ordinal_position, data_type
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Crosswalk file not found: {p}")

    delim = _sniff_delimiter(p)
    tables: Dict[str, List[ColumnMeta]] = {}

    with p.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.reader(f, delimiter=delim)
        header = next(reader, None)
        if not header:
            return tables

        # Normalize header names (lowercase, strip)
        norm = [h.strip().lower() for h in header]

        # If the file has extra columns, keep reading but only use first 6 logical fields.
        # Prefer name-based indexing when possible.
        def idx(col: str, fallback: int) -> int:
            return norm.index(col) if col in norm else fallback

        i_schema = idx("schema", 0)
        i_table = idx("table_name", 1)
        i_col = idx("column_name", 2)
        i_label = idx("column_label", 3)
        i_type = idx("data_type", 5)

        for row in reader:
            if not row or len(row) < 6:
                continue
            table = (row[i_table] or "").strip()
            col = (row[i_col] or "").strip()
            label = (row[i_label] or col).strip()
            dtype = (row[i_type] or "text").strip()

            if not table or not col:
                continue

            tables.setdefault(table, []).append(ColumnMeta(name=col, label=label, data_type=dtype))

    return tables


def save_crosswalk(path: str, tables: Dict[str, List[ColumnMeta]], schema: str = "public") -> None:
    """Write a crosswalk file that ``load_crosswalk`` can read back.

    Produces a comma-delimited file with a header row and the six standard
    columns. Used to persist the result of introspecting a database.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CROSSWALK_HEADER)
        for table in sorted(tables.keys(), key=lambda s: s.lower()):
            for ordinal, col in enumerate(tables[table], start=1):
                writer.writerow([schema, table, col.name, col.label, ordinal, col.data_type])
