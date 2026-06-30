"""Route tests that don't require a live Postgres connection.

Since schema metadata now comes from the live database, the table list and the
per-table pages are login-gated and simply redirect to /login when logged out.
"""
from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_home_redirects_to_tables(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/tables")


def test_login_page_renders(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_tables_redirects_to_login_when_logged_out(client):
    resp = client.get("/tables")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_table_page_redirects_to_login_when_logged_out(client):
    resp = client.get("/table/anything")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_introspect_page_redirects_to_login_when_logged_out(client):
    resp = client.get("/introspect")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_introspect_post_redirects_to_login_when_logged_out(client):
    resp = client.post("/introspect")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_save_grid_redirects_to_login_when_logged_out(client):
    resp = client.post("/table/anything/save_grid")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_login_with_bad_port_flashes_error(client):
    # Should short-circuit before any DB connection attempt.
    resp = client.post(
        "/login",
        data={"host": "localhost", "port": "not-a-number", "dbname": "x",
              "user": "x", "password": "x"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Port must be a number" in resp.data


def test_whoami_redirects_when_logged_out(client):
    resp = client.get("/whoami")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
