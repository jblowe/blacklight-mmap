from __future__ import annotations
from typing import Any, Dict, Tuple

def input_type_for_pg(pg_type: str) -> str:
    t = (pg_type or "").lower().strip()

    # common Postgres types (best-effort)
    if any(x in t for x in ["int", "serial"]):
        return "number"
    if any(x in t for x in ["numeric", "decimal", "real", "double", "float"]):
        return "number"
    if "bool" in t:
        return "checkbox"
    if t == "date":
        return "date"
    if "timestamp" in t or "time without time zone" in t or "time with time zone" in t:
        return "datetime-local"
    if "text" in t or "char" in t or "uuid" in t or "json" in t:
        return "text"

    # fallback
    return "text"

def normalize_value_for_db(pg_type: str, raw: Any) -> Any:
    """Convert strings from HTML form into something SQLAlchemy can pass through.
    Keep it conservative; Postgres will also coerce many strings.
    """
    t = (pg_type or "").lower().strip()
    if raw is None:
        return None
    if isinstance(raw, str):
        raw = raw.strip()
    if raw == "":
        return None

    if "bool" in t:
        # HTML checkbox gives 'on' when checked; missing when unchecked
        if raw in (True, "true", "t", "1", 1, "on", "yes", "y"):
            return True
        return False

    # numbers: keep as string and let Postgres cast, unless it's clearly int
    return raw
