#!/usr/bin/env python3
"""
csv_to_postgres_load.py

Load a CSV into a PostgreSQL table using a two-column mapping config CSV.

Config CSV format (with header optional):
    table_column,csv_column

Example:
    "SiteID","SITE_ID"
    "Ethnicity","ethnicity"
    "Photo","photo_url"

Usage:
    python csv_to_postgres_load.py input.csv "MySchema"."MyTable" "postgresql://user:pass@host:5432/dbname" mapping.csv

Notes:
- This script treats Postgres identifiers as CASE-SENSITIVE by *quoting* them.
- If you pass a schema-qualified table, use: schema.table (quotes are optional).
- CSV values are inserted as text; Postgres will cast when possible.
"""

from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List, Tuple, Optional


def normalize_csv_value(v, null_blank: bool):
    """Normalize CSV values before insertion.

    Rules:
    - Strip whitespace
    - Convert true/false (case-insensitive) to -1 / 0
    - If null_blank is set, convert blank-like values to None
    """
    if v is None:
        return None

    if isinstance(v, str):
        v = v.replace("\u00a0", " ").strip()
        lv = v.lower()

        # Boolean-like values → numeric flags
        if lv == "true":
            return -1
        if lv == "false":
            return 0

        if null_blank:
            if v == "" or v in ('""', "''"):
                return None
            if lv in ("null", "none", "n/a", "na", "."):
                return None

        return v

    return v



def make_dedupe_key(values_by_table_col: dict, dedupe_cols: list[str]):
    """Build a hashable key tuple from mapped values using the given table columns."""
    return tuple(values_by_table_col.get(c) for c in dedupe_cols)

def _import_psycopg():
    """
    Prefer psycopg (v3). Fall back to psycopg2 if installed.
    Returns (db_module, sql_module, connect_fn, paramstyle_placeholder)
    """
    try:
        import psycopg  # type: ignore
        from psycopg import sql  # type: ignore
        return psycopg, sql, psycopg.connect
    except Exception:
        try:
            import psycopg2  # type: ignore
            from psycopg2 import sql  # type: ignore
            return psycopg2, sql, psycopg2.connect
        except Exception as e:
            raise RuntimeError(
                "Neither 'psycopg' (v3) nor 'psycopg2' is installed. "
                "Install one of them, e.g.: pip install psycopg[binary]  (recommended) "
                "or: pip install psycopg2-binary"
            ) from e

def _strip_optional_quotes(ident: str) -> str:
    ident = ident.strip()
    if len(ident) >= 2 and ident[0] == '"' and ident[-1] == '"':
        return ident[1:-1]
    return ident

def _parse_table_ident(table: str) -> List[str]:
    """
    Parse table identifier possibly schema-qualified, preserving case if quoted.
    Accepts forms:
        MyTable
        public.MyTable
        "MySchema"."MyTable"
        "MyTable"
    Returns list of parts [schema, table] or [table]
    """
    table = table.strip()
    parts: List[str] = []
    buf = []
    in_quotes = False
    i = 0
    while i < len(table):
        ch = table[i]
        if ch == '"':
            in_quotes = not in_quotes
            buf.append(ch)
        elif ch == '.' and not in_quotes:
            part = ''.join(buf).strip()
            if part:
                parts.append(_strip_optional_quotes(part))
            buf = []
        else:
            buf.append(ch)
        i += 1
    tail = ''.join(buf).strip()
    if tail:
        parts.append(_strip_optional_quotes(tail))
    if not parts:
        raise ValueError("Empty table name.")
    return parts

def read_mapping(mapping_csv_path: str) -> List[Tuple[str, str]]:
    """
    Returns list of (table_col, csv_col) pairs in order.
    Header row is optional; if detected, it is skipped.
    """
    pairs: List[Tuple[str, str]] = []
    with open(mapping_csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Remove empty rows
    rows = [r for r in rows if any((c or "").strip() for c in r)]
    if not rows:
        raise ValueError(f"Mapping file is empty: {mapping_csv_path}")

    # If first row looks like a header, skip it
    first = [c.strip().lower() for c in rows[0][:2]]
    if len(first) >= 2 and ("table" in first[0] or "postgres" in first[0] or "db" in first[0]) and ("csv" in first[1] or "source" in first[1]):
        rows = rows[1:]

    for idx, row in enumerate(rows, start=1):
        if len(row) < 2:
            raise ValueError(f"Mapping row {idx} has <2 columns: {row}")
        table_col = row[0].strip()
        csv_col = row[1].strip()
        if not table_col or not csv_col:
            raise ValueError(f"Mapping row {idx} has blank values: {row}")
        pairs.append((_strip_optional_quotes(table_col), csv_col))
    return pairs

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Load CSV into a Postgres table using a mapping config.")
    parser.add_argument("csv_file", help="Input CSV file to load")
    parser.add_argument("table", help='Target Postgres table name (optionally schema-qualified). Example: public.MyTable or "MySchema"."MyTable"')
    parser.add_argument("conn", help="Postgres connection string, e.g. postgresql://user:pass@host:5432/dbname")
    parser.add_argument("mapping_csv", help="Mapping CSV with 2 columns: table_column,csv_column")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
    parser.add_argument("--encoding", default="utf-8-sig", help="CSV encoding (default: utf-8-sig)")
    parser.add_argument("--null-blank", action="store_true", help="Treat blank strings as NULL (default: false)")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate, but do not insert")
    parser.add_argument("--debug", action="store_true", help="Print diagnostics (effective options + first few rows values)")
    parser.add_argument("--commit-every", type=int, default=1000, help="Commit every N rows (default: 1000)")
    parser.add_argument("--dedupe-skip", action="store_true",
                        help="Skip inserting rows that match an existing record on the dedupe key (see --dedupe-cols).")
    parser.add_argument("--dedupe-cols", default="Site_Name,Revisits",
                        help="Comma-separated target table column names that define uniqueness. Default: Site_Name,Revisits")
    args = parser.parse_args(argv)

    db, sql, connect = _import_psycopg()

    mapping = read_mapping(args.mapping_csv)
    table_parts = _parse_table_ident(args.table)

    # Build SQL safely with Identifier quoting
    table_ident = sql.SQL(".").join([sql.Identifier(p) for p in table_parts])
    col_idents = [sql.Identifier(tc) for tc, _ in mapping]
    cols_sql = sql.SQL(", ").join(col_idents)
    placeholders = sql.SQL(", ").join([sql.Placeholder() for _ in mapping])

    insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        table_ident,
        cols_sql,
        placeholders
    )

    # Read CSV and validate columns
    with open(args.csv_file, newline='', encoding=args.encoding) as f:
        reader = csv.DictReader(f, delimiter=args.delimiter)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row (DictReader needs headers).")

        missing = [csv_col for _, csv_col in mapping if csv_col not in reader.fieldnames]
        if missing:
            raise ValueError(
                "CSV is missing required column(s) referenced by mapping: "
                + ", ".join(missing)
                + "\nCSV headers are: " + ", ".join(reader.fieldnames)
            )

        row_count = 0
        inserted = 0

        if args.dry_run:
            # Just count/validate
            for _ in reader:
                row_count += 1
            print(f"[DRY RUN] Validated mapping and read {row_count} rows. No inserts performed.")
            print("Would run SQL like:")
            print(insert_sql.as_string(db.connect(args.conn) if hasattr(db, "connect") else connect(args.conn)))  # best-effort preview
            return 0

        # Connect + insert
        # psycopg3 connect returns Connection; psycopg2 connect returns connection
        conn = connect(args.conn)
        try:
            cur = conn.cursor()
            failures = []
            skipped_dupes = 0
            existing_keys = set()
            dedupe_cols = [c.strip() for c in args.dedupe_cols.split(',') if c.strip()]
            if args.dedupe_skip:
                if not dedupe_cols:
                    raise ValueError('--dedupe-cols resolved to empty list')
                key_cols_sql = sql.SQL(', ').join([sql.Identifier(c) for c in dedupe_cols])
                preload_sql = sql.SQL('SELECT {} FROM {}').format(key_cols_sql, table_ident)
                cur.execute(preload_sql)
                for r in cur.fetchall():
                    existing_keys.add(tuple(r))
                if args.debug:
                    print(f"[DEBUG] preloaded {len(existing_keys)} existing key(s) for dedupe on {dedupe_cols}", file=sys.stderr)
            if args.debug:
                print(f"[DEBUG] null_blank={args.null_blank} delimiter={args.delimiter!r} encoding={args.encoding} commit_every={args.commit_every}", file=sys.stderr)
            batch = 0
            failures = []
            for row in reader:
                row_count += 1
                values = []
                for _, csv_col in mapping:
                    raw = row.get(csv_col, None)
                    v = normalize_csv_value(raw, args.null_blank)
                    values.append(v)
                values_by_table_col = {mapping[i][0]: values[i] for i in range(len(values))}
                if args.dedupe_skip:
                    key = make_dedupe_key(values_by_table_col, dedupe_cols)
                    if key in existing_keys:
                        skipped_dupes += 1
                        if args.debug and row_count <= 5:
                            print(f"[DEBUG] row {row_count} skipped as duplicate on {dedupe_cols}: {key}", file=sys.stderr)
                        continue

                if args.debug and row_count <= 5:
                    preview = values_by_table_col
                    print(f"[DEBUG] row {row_count} mapped values: {preview}", file=sys.stderr)
                # Use a savepoint so a single bad row does not rollback prior successful inserts
                cur.execute("SAVEPOINT row_sp")
                try:
                    cur.execute(insert_sql, values)
                    inserted += 1
                    batch += 1
                    if args.dedupe_skip:
                        existing_keys.add(make_dedupe_key(values_by_table_col, dedupe_cols))
                    cur.execute("RELEASE SAVEPOINT row_sp")
                except Exception as e:
                    cur.execute("ROLLBACK TO SAVEPOINT row_sp")
                    cur.execute("RELEASE SAVEPOINT row_sp")
                    failures.append({
                        "row_number": row_count,
                        "error": str(e),
                        "values": values,
                        "mapped": values_by_table_col,
                    })
                    continue
                except Exception as e:
                    conn.rollback()
                    failures.append({
                        "row_number": row_count,
                        "error": str(e),
                        "values": values,
                    })
                    continue

                if args.commit_every > 0 and batch >= args.commit_every:
                    conn.commit()
                    batch = 0
                    if inserted % (args.commit_every * 5) == 0:
                        print(f"... inserted {inserted} rows", file=sys.stderr)

            
            conn.commit()

            print(f"Done. Inserted {inserted} row(s) into {args.table}.")

            if args.dedupe_skip:
                print(f"Skipped duplicates: {skipped_dupes}")

            if failures:
                print("\n=== FAILED ROWS REPORT ===")
                print(f"Failed rows: {len(failures)}")
                for f in failures:
                    print(f"- CSV row {f['row_number']}: {f['error']}")
                    print(f"  Values: {f['values']}")
                    if 'mapped' in f:
                        print(f"  Mapped: {f['mapped']}")
            else:
                print("No failed rows.")

            return 0
        except Exception:
            # rollback on error to keep DB clean
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise
