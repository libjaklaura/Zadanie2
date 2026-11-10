from flask import current_app, g
import psycopg
from psycopg.rows import dict_row


def get_db():
    if "db" not in g:
        g.db = psycopg.connect(row_factory=dict_row, **current_app.config["DB_CONFIG"])
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=None):
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

