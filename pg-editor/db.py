from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

@dataclass
class DbCreds:
    host: str
    port: int
    dbname: str
    user: str
    password: str

def make_db_url(creds: DbCreds) -> str:
    # URL-encode user/password so special characters (@ : / # etc.) don't corrupt the URL.
    user = quote_plus(creds.user)
    password = quote_plus(creds.password)
    return f"postgresql+psycopg2://{user}:{password}@{creds.host}:{creds.port}/{creds.dbname}"

def get_engine(db_url: str) -> Engine:
    # pool_pre_ping helps avoid stale connections
    return create_engine(db_url, pool_pre_ping=True, future=True)

def test_connection(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
