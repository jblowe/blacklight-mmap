from __future__ import annotations
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.engine import Engine

from crosswalk import ColumnMeta


def load_schema(engine: Engine, schema: str = "public") -> Dict[str, List[ColumnMeta]]:
    """Introspect a Postgres database into {table_name: [ColumnMeta, ...]}.

    This replaces the old CSV "crosswalk": instead of reading a static file we
    ask the live database what tables and columns exist.

    - Only base tables are included (views are not editable here).
    - Columns are returned in their natural (ordinal) order.
    - ``data_type`` comes straight from ``information_schema`` so the strings
      ('integer', 'boolean', 'character varying', 'timestamp without time zone',
      ...) match what ``forms.input_type_for_pg`` expects.
    - ``label`` defaults to the column name (there is no separate label source).
    """
    sql = text(
        """
        SELECT c.table_name, c.column_name, c.data_type
        FROM information_schema.columns AS c
        JOIN information_schema.tables AS t
          ON t.table_schema = c.table_schema
         AND t.table_name  = c.table_name
        WHERE c.table_schema = :schema
          AND t.table_type = 'BASE TABLE'
        ORDER BY c.table_name, c.ordinal_position
        """
    )
    tables: Dict[str, List[ColumnMeta]] = {}
    with engine.connect() as conn:
        for row in conn.execute(sql, {"schema": schema}).mappings():
            name = row["column_name"]
            tables.setdefault(row["table_name"], []).append(
                ColumnMeta(name=name, label=name, data_type=row["data_type"] or "text")
            )
    return tables
