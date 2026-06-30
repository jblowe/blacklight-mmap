# Flask Postgres Table Editor (Bootstrap 5)

A small Flask app that:
- on login, loads each database's table/column metadata from a per-database
  *crosswalk* CSV (`instance/crosswalks/crosswalk-<dbname>.csv`), **introspecting
  the database and creating that file automatically if it does not yet exist**,
- shows a list of tables,
- for each table, provides:
  - **View**: paginated table view
  - **Edit**: add/update/delete records (primary key assumed to be `Record_No`)
  - **Configure**: choose which columns appear in View/Edit
- **Introspect** (navbar): re-read the live schema and overwrite the crosswalk
  file on demand (e.g. after the schema changes).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# No crosswalk file needed up front — it is generated on first login by
# introspecting the database. (Files land in instance/crosswalks/.)

# Put your logo here (or change APP_LOGO in config.py)
cp /path/to/tap-logo-small-v2.png static/img/

python app.py        # serves on http://127.0.0.1:3010
# ...or use the Flask CLI (defaults to port 5000):
# export FLASK_APP=app.py && flask run --debug
```

Open: http://127.0.0.1:3010 (or http://127.0.0.1:5000 if you used `flask run`)

## Login

Use **Login** in the navbar to enter Postgres credentials.  
For simplicity, credentials are stored in a server-side session (Flask-Session filesystem).

If you check **Remember my login on this browser**, the session cookie is persisted across browser restarts.
The lifetime is controlled by `SESSION_LIFETIME_DAYS` in `config.py`.

## Notes / assumptions

- Primary key is **Record_No** (integer-ish) and is not editable.
- Schema is `public` by default (`DEFAULT_SCHEMA` in `config.py`).
- Crosswalk files are written as comma-delimited CSV; on read the delimiter is auto-detected,
  so hand-edited tab-delimited files are also accepted.
- Per-database crosswalk files live in `CROSSWALK_DIR` (`instance/crosswalks` by default),
  named `crosswalk-<dbname>.csv`. Delete a file (or use **Introspect**) to regenerate it.
