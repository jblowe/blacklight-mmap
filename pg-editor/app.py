from __future__ import annotations
import json
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

from flask import (
    Flask, abort, flash, redirect, render_template, request, session, url_for
)
from flask_session import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

import config as cfg
from crosswalk import ColumnMeta, load_crosswalk, save_crosswalk
from introspect import load_schema
from db import DbCreds, get_engine, make_db_url, test_connection
from forms import input_type_for_pg, normalize_value_for_db

PK_NAME = "Record_No"

# Directory of this file, so the app works regardless of the current working
# directory it was launched from.
BASE_DIR = Path(__file__).resolve().parent

def _resolve(path: str) -> Path:
    """Resolve a (possibly relative) config path against the app directory."""
    p = Path(path)
    return p if p.is_absolute() else BASE_DIR / p

def _safe_name(s: str) -> str:
    """Sanitize a string for use in a filename."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in (s or "")).strip("_") or "db"

def crosswalk_path_for(dbname: str) -> Path:
    """Per-database crosswalk file path, e.g. instance/crosswalks/crosswalk-mydb.csv."""
    cw_dir = _resolve(getattr(cfg, "CROSSWALK_DIR", "instance/crosswalks"))
    return cw_dir / f"crosswalk-{_safe_name(dbname)}.csv"

def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = getattr(cfg, "SECRET_KEY", "change-me")
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = str(BASE_DIR / "instance" / "flask_session")
    app.config["SESSION_PERMANENT"] = False
    # If a user checks "Remember me" on the login page, we set session.permanent=True.
    # This controls how long the session cookie is kept by the browser.
    app.permanent_session_lifetime = timedelta(days=int(getattr(cfg, "SESSION_LIFETIME_DAYS", 30)))
    Session(app)

    # Schema metadata is no longer loaded from a static file at startup; it is
    # built per database connection (from a crosswalk file or by introspection)
    # and cached here, keyed by the connection URL.
    app.config["SCHEMA_CACHE"] = {}

    # Ensure config file exists
    _resolve(getattr(cfg, "TABLE_CONFIG_FILE", "instance/table_config.json")).parent.mkdir(parents=True, exist_ok=True)

    @app.context_processor
    def inject_branding():
        return dict(
            APP_LOGO=getattr(cfg, "APP_LOGO", ""),
            APP_TITLE=getattr(cfg, "APP_TITLE", ""),
            BANNER_BG=getattr(cfg, "BANNER_BG", "#0d6efd"),
            BANNER_FG=getattr(cfg, "BANNER_FG", "#ffffff"),
            BANNER_ACCENT=getattr(cfg, "BANNER_ACCENT", "#60a5fa"),
            logged_in=is_logged_in(),
        )

    def is_logged_in() -> bool:
        return bool(session.get("db_url"))

    def require_login():
        if not is_logged_in():
            flash("Please login with Postgres credentials first.", "warning")
            return redirect(url_for("login", next=request.path))
        return None

    def get_table_config() -> Dict[str, Any]:
        path = _resolve(getattr(cfg, "TABLE_CONFIG_FILE", "instance/table_config.json"))
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_table_config(conf: Dict[str, Any]) -> None:
        path = _resolve(getattr(cfg, "TABLE_CONFIG_FILE", "instance/table_config.json"))
        path.write_text(json.dumps(conf, indent=2, ensure_ascii=False), encoding="utf-8")

    def default_visibility_for_table(columns: List[ColumnMeta]) -> Tuple[List[str], List[str]]:
        """Default visibility rules.

        - View: only the first 10 non-PK columns
        - Edit: all non-PK columns
        """
        non_pk = [c.name for c in columns if c.name != PK_NAME]
        view_cols = non_pk[:10]
        edit_cols = non_pk
        return view_cols, edit_cols

    def get_or_init_table_config(table_name: str, columns: List[ColumnMeta]) -> Tuple[Dict[str, Any], bool]:
        """Return (conf, created).

        If the table has never been configured, create a starter configuration
        (View first 10 fields; Edit all fields) and persist it.
        """
        all_conf = get_table_config()
        if table_name in all_conf and isinstance(all_conf.get(table_name), dict):
            return all_conf[table_name], False

        view_cols, edit_cols = default_visibility_for_table(columns)
        all_conf[table_name] = {"view_cols": view_cols, "edit_cols": edit_cols}
        save_table_config(all_conf)
        return all_conf[table_name], True

    def get_effective_column_visibility(table_name: str, columns: List[ColumnMeta]) -> Tuple[List[str], List[str]]:
        """Return (view_cols, edit_cols) as lists of column names."""
        default_view, default_edit = default_visibility_for_table(columns)
        conf = get_table_config().get(table_name, {})
        view_cols = conf.get("view_cols") or default_view
        edit_cols = conf.get("edit_cols") or default_edit

        # ensure PK never appears
        view_cols = [c for c in view_cols if c != PK_NAME]
        edit_cols = [c for c in edit_cols if c != PK_NAME]

        # ensure they still exist in schema
        existing = {c.name for c in columns}
        view_cols = [c for c in view_cols if c in existing]
        edit_cols = [c for c in edit_cols if c in existing]

        return view_cols, edit_cols

    def get_engine_or_redirect():
        if not session.get("db_url"):
            return None, require_login()
        try:
            eng = get_engine(session["db_url"])
            return eng, None
        except Exception as e:
            flash(f"Could not create DB engine: {e}", "danger")
            session.pop("db_url", None)
            return None, redirect(url_for("login"))

    def build_tables_meta(eng, force: bool = False) -> Tuple[Dict[str, List[ColumnMeta]], str]:
        """Load schema metadata for the current connection.

        Returns (tables_meta, source) where source is "crosswalk" or "introspect".
        If a per-database crosswalk file exists it is used; otherwise the database
        is introspected and the result is written out as that crosswalk file.
        Pass force=True to always re-introspect and overwrite the file.
        """
        schema = getattr(cfg, "DEFAULT_SCHEMA", "public")
        path = Path(session.get("crosswalk_path") or crosswalk_path_for(session.get("dbname", "")))
        if not force and path.exists():
            return load_crosswalk(str(path)), "crosswalk"
        meta = load_schema(eng, schema)
        save_crosswalk(str(path), meta, schema)
        return meta, "introspect"

    def get_tables_meta(eng) -> Dict[str, List[ColumnMeta]]:
        """Return cached schema metadata for the current connection, building it
        (from crosswalk file or introspection) on first use."""
        key = session.get("db_url")
        cache = app.config["SCHEMA_CACHE"]
        if key not in cache:
            cache[key], _ = build_tables_meta(eng)
        return cache[key]

    def qident(name: str) -> str:
        """Return a safely quoted SQL identifier for Postgres.

        This supports both "normal" Postgres (unquoted identifiers folded to
        lowercase) and databases created with quoted, case-sensitive identifiers.
        """
        return '"' + (name or "").replace('"', '""') + '"'

    def qtable(schema: str, table: str) -> str:
        return f"{qident(schema)}.{qident(table)}"

    @app.get("/")
    def home():
        return redirect(url_for("tables"))

    @app.get("/about")
    def about():
        return render_template("about.html")

    @app.get("/login")
    def login():
        defaults = getattr(cfg, "DB_DEFAULTS", {}) or {}
        return render_template("login.html", defaults=defaults, next=request.args.get("next", ""))

    @app.post("/login")
    def login_post():
        host = request.form.get("host", "").strip() or "localhost"
        try:
            port = int(request.form.get("port", "5432").strip() or 5432)
        except ValueError:
            flash("Port must be a number.", "danger")
            return redirect(url_for("login"))
        dbname = request.form.get("dbname", "").strip() or "postgres"
        user = request.form.get("user", "").strip() or "postgres"
        password = request.form.get("password", "")

        creds = DbCreds(host=host, port=port, dbname=dbname, user=user, password=password)
        db_url = make_db_url(creds)

        try:
            eng = get_engine(db_url)
            test_connection(eng)

            # Capture connection identity for debugging and to detect when the user
            # accidentally logs into the wrong database/host.
            with eng.connect() as conn:
                ident_row = conn.execute(text(
                    """
                    SELECT
                      current_database() AS db,
                      current_user AS usr,
                      current_schema() AS schema,
                      inet_server_addr()::text AS server_addr,
                      inet_server_port() AS server_port
                    """
                )).mappings().first()
                session["db_ident"] = dict(ident_row) if ident_row else {}
        except Exception as e:
            flash(f"Login failed: {e}", "danger")
            return redirect(url_for("login"))

        session["db_url"] = db_url
        session["dbname"] = dbname
        # Remember the per-database crosswalk path so we can rebuild metadata
        # later even if the in-memory cache was lost (e.g. after a restart).
        cw_path = crosswalk_path_for(dbname)
        session["crosswalk_path"] = str(cw_path)

        # Build schema metadata now: use an existing crosswalk file, or introspect
        # the database and create one.
        try:
            meta, source = build_tables_meta(eng, force=False)
            app.config["SCHEMA_CACHE"][db_url] = meta
            session["schema_info"] = {
                "schema": getattr(cfg, "DEFAULT_SCHEMA", "public"),
                "table_count": len(meta),
                "path": str(cw_path),
                "source": source,
            }
        except Exception as e:
            flash(f"Logged in, but loading schema failed: {e}", "warning")
            session["schema_info"] = {}

        # Persist session across browser restarts if requested.
        # This still uses a cookie in the browser; expiration is controlled by app.permanent_session_lifetime.
        remember = request.form.get("remember") in ("on", "1", "true", "yes")
        session.permanent = bool(remember)

        info = session.get("schema_info") or {}
        if info.get("table_count"):
            verb = "loaded from crosswalk" if info.get("source") == "crosswalk" else "introspected"
            flash(f"Logged in. {info['table_count']} tables {verb}.", "success")
        else:
            flash(
                f"Logged in, but no base tables were found in schema "
                f"'{getattr(cfg, 'DEFAULT_SCHEMA', 'public')}'. Double-check host/port/dbname.",
                "warning",
            )
        nxt = request.form.get("next") or url_for("tables")
        return redirect(nxt)

    @app.get("/whoami")
    def whoami():
        """Lightweight diagnostic page to confirm which DB the app is connected to."""
        if not is_logged_in():
            return redirect(url_for("login", next=url_for("whoami")))
        ident = session.get("db_ident") or {}
        schema_info = session.get("schema_info") or {}
        return render_template("whoami.html", ident=ident, schema_info=schema_info)

    @app.get("/logout")
    def logout():
        # Drop this connection's cached schema too.
        app.config["SCHEMA_CACHE"].pop(session.get("db_url"), None)
        for k in ("db_url", "dbname", "crosswalk_path", "schema_info", "db_ident"):
            session.pop(k, None)
        flash("Logged out.", "info")
        return redirect(url_for("tables"))

    @app.get("/tables")
    def tables():
        eng, resp = get_engine_or_redirect()
        if resp:
            return resp
        try:
            tables_meta = get_tables_meta(eng)
        except Exception as e:
            flash(f"Could not load tables: {e}", "danger")
            tables_meta = {}
        # sort tables for nicer UI
        table_names = sorted(tables_meta.keys(), key=lambda s: s.lower())
        return render_template("tables.html", table_names=table_names)

    @app.get("/introspect")
    def introspect_page():
        eng, resp = get_engine_or_redirect()
        if resp:
            return resp
        path = Path(session.get("crosswalk_path") or crosswalk_path_for(session.get("dbname", "")))
        try:
            current = get_tables_meta(eng)
            table_count = len(current)
            column_count = sum(len(v) for v in current.values())
        except Exception as e:
            flash(f"Could not read current schema: {e}", "danger")
            table_count = column_count = 0
        return render_template(
            "introspect.html",
            ident=session.get("db_ident") or {},
            schema=getattr(cfg, "DEFAULT_SCHEMA", "public"),
            crosswalk_path=str(path),
            crosswalk_exists=path.exists(),
            table_count=table_count,
            column_count=column_count,
        )

    @app.post("/introspect")
    def introspect_run():
        eng, resp = get_engine_or_redirect()
        if resp:
            return resp
        try:
            meta, _ = build_tables_meta(eng, force=True)
            app.config["SCHEMA_CACHE"][session.get("db_url")] = meta
            path = session.get("crosswalk_path") or str(crosswalk_path_for(session.get("dbname", "")))
            cols = sum(len(v) for v in meta.values())
            flash(f"Introspected {len(meta)} tables ({cols} columns) → {path}", "success")
        except Exception as e:
            flash(f"Introspection failed: {e}", "danger")
        return redirect(url_for("introspect_page"))

    @app.get("/table/<table_name>")
    def table_page(table_name: str):
        eng, resp = get_engine_or_redirect()
        if resp:
            return resp

        tables_meta = get_tables_meta(eng)
        if table_name not in tables_meta:
            abort(404)

        tab = request.args.get("tab", "view")
        tab = tab if tab in ("view", "edit", "configure") else "view"

        columns = tables_meta[table_name]
        # initialize config on first visit; show Configure first time unless an explicit tab is requested
        conf, created = get_or_init_table_config(table_name, columns)
        if created and "tab" not in request.args:
            tab = "configure"

        view_cols, edit_cols = get_effective_column_visibility(table_name, columns)

        # VIEW
        page_size = int(getattr(cfg, "PAGE_SIZE", 25))
        try:
            page = max(int(request.args.get("page", "1")), 1)
        except Exception:
            page = 1
        offset = (page - 1) * page_size

        rows = []
        total = None
        last_page = None
        pk_values = []
        prev_pk = None
        next_pk = None
        first_pk = None
        last_pk = None

        schema = getattr(cfg, "DEFAULT_SCHEMA", "public")

        if tab == "view":
            try:
                cols = [PK_NAME] + [c for c in view_cols if c != PK_NAME]
                select_cols_sql = ", ".join(qident(c) for c in cols)
                tbl_sql = qtable(schema, table_name)
                q = text(
                    f"SELECT {select_cols_sql} FROM {tbl_sql} "
                    f"ORDER BY {qident(PK_NAME)} LIMIT :limit OFFSET :offset"
                )
                q_count = text(f"SELECT count(*) AS cnt FROM {tbl_sql}")

                with eng.connect() as conn:
                    rows = conn.execute(q, {"limit": page_size, "offset": offset}).mappings().all()
                    total = conn.execute(q_count).scalar_one()
                    if total is not None:
                        last_page = max((int(total) + page_size - 1) // page_size, 1)
            except Exception as e:
                flash(f"View failed: {e}", "danger")

        # EDIT
        # Two sub-modes: 'form' (one record at a time) and 'grid' (paginated
        # editable table). Pagination for the grid follows the same page/per_page
        # model used elsewhere (and in the Infrared app).
        editmode = request.args.get("editmode", "form")
        editmode = editmode if editmode in ("form", "grid") else "form"
        record_no = request.args.get("record")
        record = None

        per_page_options = [10, 25, 50, 100]
        try:
            per_page = int(request.args.get("per_page", page_size))
        except Exception:
            per_page = page_size
        if per_page < 1:
            per_page = page_size
        grid_rows = []
        grid_total = None
        grid_pages = None
        grid_start = 0
        grid_end = 0

        if tab == "edit" and editmode == "grid":
            try:
                tbl_sql = qtable(schema, table_name)
                grid_cols = [PK_NAME] + [c for c in edit_cols if c != PK_NAME]
                select_cols_sql = ", ".join(qident(c) for c in grid_cols)
                grid_offset = (page - 1) * per_page
                q = text(
                    f"SELECT {select_cols_sql} FROM {tbl_sql} "
                    f"ORDER BY {qident(PK_NAME)} LIMIT :limit OFFSET :offset"
                )
                q_count = text(f"SELECT count(*) AS cnt FROM {tbl_sql}")
                with eng.connect() as conn:
                    grid_rows = conn.execute(q, {"limit": per_page, "offset": grid_offset}).mappings().all()
                    grid_total = conn.execute(q_count).scalar_one()
                if grid_total is not None:
                    grid_pages = max((int(grid_total) + per_page - 1) // per_page, 1)
                    grid_start = grid_offset + 1 if grid_rows else 0
                    grid_end = grid_offset + len(grid_rows)
            except Exception as e:
                flash(f"Edit (table) load failed: {e}", "danger")

        elif tab == "edit":
            try:
                tbl_sql = qtable(schema, table_name)
                q_pks = text(
                    f"SELECT {qident(PK_NAME)} FROM {tbl_sql} "
                    f"ORDER BY {qident(PK_NAME)} LIMIT 2000"
                )

                # Only fetch columns we actually edit (+ PK for display)
                edit_fetch_cols = [PK_NAME] + [c for c in edit_cols if c != PK_NAME]
                select_cols_sql = ", ".join(qident(c) for c in edit_fetch_cols)
                q_record = text(
                    f"SELECT {select_cols_sql} FROM {tbl_sql} "
                    f"WHERE {qident(PK_NAME)} = :pk"
                )

                with eng.connect() as conn:
                    pk_values = conn.execute(q_pks).scalars().all()
                    if pk_values:
                        first_pk = pk_values[0]
                        last_pk = pk_values[-1]

                    if record_no:
                        record = conn.execute(q_record, {"pk": record_no}).mappings().first()

                    # prev/next helpers for UX
                    if record_no is not None and record_no != "":
                        try:
                            idx = [str(v) for v in pk_values].index(str(record_no))
                            if idx > 0:
                                prev_pk = pk_values[idx - 1]
                            if idx < (len(pk_values) - 1):
                                next_pk = pk_values[idx + 1]
                        except ValueError:
                            pass
            except Exception as e:
                flash(f"Edit load failed: {e}", "danger")

        # CONFIGURE
        return render_template(
            "table.html",
            table_name=table_name,
            tab=tab,
            editmode=editmode,
            columns=columns,
            view_cols=view_cols,
            edit_cols=edit_cols,
            rows=rows,
            total=total,
            last_page=last_page,
            page=page,
            page_size=page_size,
            per_page=per_page,
            per_page_options=per_page_options,
            grid_rows=grid_rows,
            grid_total=grid_total,
            grid_pages=grid_pages,
            grid_start=grid_start,
            grid_end=grid_end,
            pk_values=pk_values,
            record_no=record_no,
            record=record,
            prev_pk=prev_pk,
            next_pk=next_pk,
            first_pk=first_pk,
            last_pk=last_pk,
            input_type_for_pg=input_type_for_pg,
            conf=conf,
            PK_NAME=PK_NAME,
        )

    @app.post("/table/<table_name>/save")
    def table_save(table_name: str):
        eng, resp = get_engine_or_redirect()
        if resp:
            return resp

        tables_meta = get_tables_meta(eng)
        if table_name not in tables_meta:
            abort(404)

        columns = tables_meta[table_name]
        col_meta = {c.name: c for c in columns}
        # effective edit columns
        _, edit_cols = get_effective_column_visibility(table_name, columns)

        schema = getattr(cfg, "DEFAULT_SCHEMA", "public")

        pk = request.form.get(PK_NAME, "").strip()
        values: Dict[str, Any] = {}

        for c in edit_cols:
            meta = col_meta.get(c)
            if not meta:
                continue

            itype = input_type_for_pg(meta.data_type)
            if itype == "checkbox":
                raw = "on" if request.form.get(c) == "on" else ""
            else:
                raw = request.form.get(c, "")

            values[c] = normalize_value_for_db(meta.data_type, raw)

        tbl_sql = qtable(schema, table_name)

        try:
            with eng.begin() as conn:
                if pk:
                    if values:
                        set_sql = ", ".join(f"{qident(k)} = :{k}" for k in values.keys())
                        stmt = text(
                            f"UPDATE {tbl_sql} SET {set_sql} WHERE {qident(PK_NAME)} = :__pk"
                        )
                        params = dict(values)
                        params["__pk"] = pk
                        res = conn.execute(stmt, params)
                        flash(f"Updated {res.rowcount} row(s).", "success")
                    else:
                        flash("Nothing to update.", "warning")
                else:
                    if values:
                        cols_sql = ", ".join(qident(k) for k in values.keys())
                        vals_sql = ", ".join(f":{k}" for k in values.keys())
                        stmt = text(
                            f"INSERT INTO {tbl_sql} ({cols_sql}) VALUES ({vals_sql}) RETURNING {qident(PK_NAME)}"
                        )
                        new_pk = conn.execute(stmt, values).scalar_one_or_none()
                        flash(f"Inserted new row (Record_No={new_pk}).", "success")
                        return redirect(url_for("table_page", table_name=table_name, tab="edit", record=new_pk))
                    else:
                        # allow inserting a row with only defaults
                        stmt = text(
                            f"INSERT INTO {tbl_sql} DEFAULT VALUES RETURNING {qident(PK_NAME)}"
                        )
                        new_pk = conn.execute(stmt).scalar_one_or_none()
                        flash(f"Inserted new row (Record_No={new_pk}).", "success")
                        return redirect(url_for("table_page", table_name=table_name, tab="edit", record=new_pk))
        except SQLAlchemyError as e:
            flash(f"Save failed: {e}", "danger")

        return redirect(url_for("table_page", table_name=table_name, tab="edit", record=pk or ""))

    @app.post("/table/<table_name>/save_grid")
    def table_save_grid(table_name: str):
        """Bulk-save the editable table (grid) view.

        Each cell input is named ``row-<pk>-<col>`` with a matching hidden
        ``orig-<pk>-<col>``; only cells whose value actually changed are written.
        """
        eng, resp = get_engine_or_redirect()
        if resp:
            return resp

        tables_meta = get_tables_meta(eng)
        if table_name not in tables_meta:
            abort(404)

        columns = tables_meta[table_name]
        col_meta = {c.name: c for c in columns}
        _, edit_cols = get_effective_column_visibility(table_name, columns)
        edit_col_names = [c for c in edit_cols if c != PK_NAME]

        schema = getattr(cfg, "DEFAULT_SCHEMA", "public")
        tbl_sql = qtable(schema, table_name)

        pks = request.form.getlist("pk")
        rows_updated = 0
        cells_updated = 0

        try:
            with eng.begin() as conn:
                for pk in pks:
                    changes: Dict[str, Any] = {}
                    for c in edit_col_names:
                        meta = col_meta.get(c)
                        if not meta:
                            continue
                        field = f"row-{pk}-{c}"
                        orig_field = f"orig-{pk}-{c}"
                        itype = input_type_for_pg(meta.data_type)
                        if itype == "checkbox":
                            new_raw = "on" if request.form.get(field) == "on" else ""
                        else:
                            if field not in request.form:
                                continue  # column not present in this submission
                            new_raw = request.form.get(field, "")
                        orig_raw = request.form.get(orig_field, "")
                        if (new_raw or "") == (orig_raw or ""):
                            continue  # unchanged
                        changes[c] = normalize_value_for_db(meta.data_type, new_raw)

                    if changes:
                        set_sql = ", ".join(f"{qident(k)} = :{k}" for k in changes)
                        stmt = text(
                            f"UPDATE {tbl_sql} SET {set_sql} WHERE {qident(PK_NAME)} = :__pk"
                        )
                        params = dict(changes)
                        params["__pk"] = pk
                        conn.execute(stmt, params)
                        rows_updated += 1
                        cells_updated += len(changes)

            if rows_updated:
                flash(f"Updated {cells_updated} field(s) across {rows_updated} record(s).", "success")
            else:
                flash("No changes to save.", "info")
        except SQLAlchemyError as e:
            flash(f"Save failed: {e}", "danger")

        page = request.form.get("page", "1")
        per_page = request.form.get("per_page") or None
        return redirect(url_for("table_page", table_name=table_name, tab="edit",
                                editmode="grid", page=page, per_page=per_page))

    @app.post("/table/<table_name>/delete")
    def table_delete(table_name: str):
        if not getattr(cfg, "ALLOW_DELETES", True):
            flash("Deletes are disabled by configuration.", "warning")
            return redirect(url_for("table_page", table_name=table_name, tab="edit"))

        eng, resp = get_engine_or_redirect()
        if resp:
            return resp

        tables_meta = get_tables_meta(eng)
        if table_name not in tables_meta:
            abort(404)

        record_no = request.form.get(PK_NAME, "").strip()
        if not record_no:
            flash("No Record_No provided.", "warning")
            return redirect(url_for("table_page", table_name=table_name, tab="edit"))

        schema = getattr(cfg, "DEFAULT_SCHEMA", "public")

        tbl_sql = qtable(schema, table_name)
        try:
            with eng.begin() as conn:
                stmt = text(
                    f"DELETE FROM {tbl_sql} WHERE {qident(PK_NAME)} = :pk"
                )
                res = conn.execute(stmt, {"pk": record_no})
            flash(f"Deleted {res.rowcount} row(s).", "success")
        except SQLAlchemyError as e:
            flash(f"Delete failed: {e}", "danger")

        return redirect(url_for("table_page", table_name=table_name, tab="edit"))

    @app.post("/table/<table_name>/configure")
    def table_configure(table_name: str):
        eng, resp = get_engine_or_redirect()
        if resp:
            return resp

        tables_meta = get_tables_meta(eng)
        if table_name not in tables_meta:
            abort(404)

        columns = tables_meta[table_name]
        col_names = [c.name for c in columns if c.name != PK_NAME]

        view_cols = [c for c in request.form.getlist("view_cols") if c in col_names]
        edit_cols = [c for c in request.form.getlist("edit_cols") if c in col_names]

        conf_all = get_table_config()
        conf_all[table_name] = {"view_cols": view_cols, "edit_cols": edit_cols}
        save_table_config(conf_all)
        flash("Saved column configuration.", "success")
        return redirect(url_for("table_page", table_name=table_name, tab="configure"))

    return app

app = create_app()

if __name__ == "__main__":
    # For local dev (or use flask run)
    app.run(host="127.0.0.1", port=3010, debug=True)
