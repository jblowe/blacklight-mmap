"""Unit tests for the pure helper functions (no database required)."""
from __future__ import annotations
from pathlib import Path

import pytest

from db import DbCreds, make_db_url
from forms import input_type_for_pg, normalize_value_for_db
from crosswalk import ColumnMeta, load_crosswalk, save_crosswalk
from introspect import load_schema


# --- db.make_db_url -------------------------------------------------------

def test_make_db_url_basic():
    url = make_db_url(DbCreds("localhost", 5432, "mydb", "alice", "secret"))
    assert url == "postgresql+psycopg2://alice:secret@localhost:5432/mydb"


def test_make_db_url_escapes_special_chars_in_password():
    # The bug this guards against: '@', ':' and '/' in a password used to
    # corrupt the connection URL.
    url = make_db_url(DbCreds("localhost", 5432, "mydb", "alice", "p@ss:w/rd"))
    assert "p%40ss%3Aw%2Frd" in url
    # The host portion must remain intact (only one real '@' separator).
    assert url.endswith("@localhost:5432/mydb")


# --- forms.input_type_for_pg ---------------------------------------------

@pytest.mark.parametrize("pg_type,expected", [
    ("integer", "number"),
    ("bigserial", "number"),
    ("numeric(10,2)", "number"),
    ("double precision", "number"),
    ("boolean", "checkbox"),
    ("date", "date"),
    ("timestamp without time zone", "datetime-local"),
    ("text", "text"),
    ("character varying(255)", "text"),
    ("jsonb", "text"),
    ("", "text"),            # fallback
    ("something_weird", "text"),  # fallback
])
def test_input_type_for_pg(pg_type, expected):
    assert input_type_for_pg(pg_type) == expected


# --- forms.normalize_value_for_db ----------------------------------------

def test_normalize_empty_string_becomes_none():
    assert normalize_value_for_db("text", "") is None
    assert normalize_value_for_db("text", "   ") is None


def test_normalize_none_stays_none():
    assert normalize_value_for_db("integer", None) is None


@pytest.mark.parametrize("raw", ["on", "true", "t", "1", "yes", "y", True])
def test_normalize_bool_truthy(raw):
    assert normalize_value_for_db("boolean", raw) is True


@pytest.mark.parametrize("raw", ["off", "false", "no", "nope"])
def test_normalize_bool_falsy(raw):
    assert normalize_value_for_db("boolean", raw) is False


def test_normalize_text_is_stripped_and_passed_through():
    assert normalize_value_for_db("text", "  hello  ") == "hello"


# --- crosswalk.load_crosswalk --------------------------------------------

def test_load_crosswalk_parses_tab_delimited(tmp_path: Path):
    csv = tmp_path / "cw.tsv"
    csv.write_text(
        "schema\ttable_name\tcolumn_name\tcolumn_label\tordinal_position\tdata_type\n"
        "public\tsites\tRecord_No\tID\t1\tinteger\n"
        "public\tsites\tname\tSite Name\t2\ttext\n"
        "public\tfinds\tRecord_No\tID\t1\tinteger\n",
        encoding="utf-8",
    )
    tables = load_crosswalk(str(csv))
    assert set(tables.keys()) == {"sites", "finds"}
    assert [c.name for c in tables["sites"]] == ["Record_No", "name"]
    assert tables["sites"][1].label == "Site Name"
    assert tables["sites"][1].data_type == "text"


def test_load_crosswalk_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_crosswalk(str(tmp_path / "does-not-exist.csv"))


def test_save_then_load_crosswalk_round_trips(tmp_path: Path):
    tables = {
        "sites": [
            ColumnMeta("Record_No", "Record_No", "integer"),
            ColumnMeta("name", "name", "text"),
        ],
        "finds": [ColumnMeta("Record_No", "Record_No", "integer")],
    }
    path = tmp_path / "nested" / "crosswalk-mydb.csv"   # parent dir auto-created
    save_crosswalk(str(path), tables, schema="public")
    assert path.exists()

    reloaded = load_crosswalk(str(path))
    assert set(reloaded.keys()) == {"sites", "finds"}
    assert [c.name for c in reloaded["sites"]] == ["Record_No", "name"]
    assert reloaded["sites"][1].data_type == "text"


# --- introspect.load_schema (no real database) ---------------------------

class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self._rows


class _FakeConn:
    def __init__(self, rows):
        self._rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        return _FakeResult(self._rows)


class _FakeEngine:
    def __init__(self, rows):
        self._rows = rows

    def connect(self):
        return _FakeConn(self._rows)


def test_load_schema_builds_table_dict():
    rows = [
        {"table_name": "sites", "column_name": "Record_No", "data_type": "integer"},
        {"table_name": "sites", "column_name": "name", "data_type": "text"},
        {"table_name": "finds", "column_name": "Record_No", "data_type": "integer"},
    ]
    tables = load_schema(_FakeEngine(rows), "public")
    assert set(tables.keys()) == {"sites", "finds"}
    assert [c.name for c in tables["sites"]] == ["Record_No", "name"]
    # label defaults to the column name
    assert tables["sites"][1].label == "name"
    assert tables["sites"][1].data_type == "text"
