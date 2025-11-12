import sqlite3
import os
from flask import g

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


def query_param(sql, params=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def execute(sql, params=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    db.commit()
    return cur.lastrowid
