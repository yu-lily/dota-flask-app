import psycopg2

import click
from flask import current_app, g
from flask.cli import with_appcontext
import psycopg2
import os


def get_db():
    if 'conn' not in g:
        g.conn = psycopg2.connect(
            host="localhost",
            database="dota",
            user="postgres",
            password=os.getenv("POSTGRES_PASS"))
        g.cur = g.db.cursor()

    return g.cur


def close_db():
    conn, cur = g.pop('conn', None), g.pop('cur', None)

    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
